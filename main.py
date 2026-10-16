"""Streamlit demo of the existing engine, not the unimplemented RAW pipeline."""

import csv
import io
import json
from pathlib import Path
from typing import Any, Dict

import streamlit as st

from src.classify import ClinicalRuleEngine


ROOT = Path(__file__).resolve().parent
ISSUE_HELP = {
    "F-01": "Cấp thông thường chưa khả đạt: cùng biến triệu chứng đang được yêu cầu vừa là object vừa là chuỗi.",
    "F-02": "Tuổi dưới một tháng, 10,5 và 17,5 chưa được các khoảng sốc hiện tại bao phủ; không tự làm tròn tuổi.",
    "F-03": "Đúng 6 tuần: cấp dùng <=1008 giờ, mạn dùng >6 tuần; ranh giới và nguồn thời gian cần chốt.",
    "F-04": "R03 dùng tác nhân nghi ngờ thay tiêu chí dị nguyên đã biết; các rule phản vệ chưa kiểm tra thời điểm.",
    "F-05": "Sốc chỉ tham chiếu R02/R03; ca chỉ đạt R01 dù HATT thấp vẫn không vào rule sốc hiện tại.",
    "F-06": "CIndU khác chưa loại Ice cube dương; Adrenergic chưa có nhánh; nhiều test dương cần chính sách phân thể.",
    "F-07": "Chưa có validator enum/range: giá trị test sai có thể được coi là không dương; HATT âm vẫn có thể thỏa rule.",
    "F-08": "Stella FALSE/UNKNOWN vẫn có thể vào CSU GĐ2 vì IgE <40; YAML khác workflow, chưa có nhánh loại cohort.",
    "F-09": "Thiếu sàng lọc phản vệ chung có thể chặn CSU dù xét nghiệm đầy đủ; không tự điền Không vào trường thiếu.",
    "F-10": "CIndU được chọn trước CSU khi cùng khớp; điều kiện cohort và biểu diễn đồng mắc chưa chốt.",
    "F-11": "ASST null có thể kích hoạt fallback ngoài CSU; rule UNKNOWN ưu tiên cao vẫn có thể chặn fallback.",
    "F-12": "Công thức HATT thiếu kiểm tra kiểu: chuỗi/list/object có thể crash; boolean có thể bị kết luận sốc sai.",
    "F-13": "Lý do UNKNOWN có thể bị lẫn với lỗi kiểu từ nhánh OR đã đủ bằng chứng, làm sai lý do cần rà soát.",
}
STATUS_HELP = {
    "CLASSIFIED": "Đã chẩn đoán rõ — Đầy đủ dữ liệu, xác định chính xác mặt bệnh và thỏa mãn quy tắc y khoa.",
    "INSUFFICIENT_DATA": "Bệnh án thiếu dữ liệu — Thiếu xét nghiệm bắt buộc hoặc cần tiếp tục theo dõi thêm (INSUFFICIENT).",
    "NEEDS_REVIEW": "Cần bác sĩ rà soát — Có điểm mâu thuẫn hoặc dấu hiệu lâm sàng cần bác sĩ đánh giá trực tiếp.",
    "UNRESOLVED": "Chưa xác định được — Dữ liệu bệnh án không khớp với bất kỳ quy tắc nào trong nhóm bệnh.",
}


def parse_csv_patient(file_bytes: bytes) -> Dict[str, Any]:
    text = file_bytes.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        parsed = {}
        for k, v in row.items():
            if v is None:
                continue
            v_strip = v.strip()
            if v_strip.isdigit():
                parsed[k] = int(v_strip)
            elif v_strip.lower() == "true":
                parsed[k] = True
            elif v_strip.lower() == "false":
                parsed[k] = False
            else:
                try:
                    parsed[k] = float(v_strip)
                except ValueError:
                    parsed[k] = v_strip
        return parsed
    raise ValueError("File CSV trống hoặc không có dòng dữ liệu.")


def generate_clinical_summary_html(patient: Dict[str, Any], title: str = "Phiếu tóm tắt lâm sàng") -> str:
    if not isinstance(patient, dict):
        return "<p style='color: #64748b;'>Chưa có dữ liệu bệnh án.</p>"
    tuoi = patient.get("tuoi", "Chưa rõ")
    ha = patient.get("huyet_ap_tam_thu_thap_nhat", patient.get("huyet_ap", "Chưa rõ"))
    thuc_an = patient.get("yeu_to_nghi_ngo_pv_thuc_an", {}).get("co_khong") if isinstance(patient.get("yeu_to_nghi_ngo_pv_thuc_an"), dict) else patient.get("yeu_to_nghi_ngo_pv_thuc_an", "Không")
    thuoc = patient.get("yeu_to_nghi_ngo_pv_thuoc", {}).get("co_khong") if isinstance(patient.get("yeu_to_nghi_ngo_pv_thuoc"), dict) else patient.get("yeu_to_nghi_ngo_pv_thuoc", "Không")
    
    da_list = patient.get("trieu_chung_da_hien_tai_pv", {}).get("danh_sach_chon", []) if isinstance(patient.get("trieu_chung_da_hien_tai_pv"), dict) else []
    if not da_list and patient.get("trieu_chung_da_hien_tai"):
        da_list = [str(patient.get("trieu_chung_da_hien_tai"))]
    
    ho_hap_list = patient.get("trieu_chung_ho_hap_hien_tai_pv", {}).get("danh_sach_chon", []) if isinstance(patient.get("trieu_chung_ho_hap_hien_tai_pv"), dict) else []
    
    san_phu = patient.get("hien_tai_co_san_phu", "Không")
    khoi_phat = patient.get("thoi_gian_khoi_phat_gio", patient.get("thoi_gian_khoi_phat_tuan", "Chưa rõ"))
    asst = patient.get("asst_ket_qua", "Chưa làm")
    il24 = patient.get("ige_khang_il24_ket_qua", "Chưa làm")
    
    da_text = ", ".join(da_list) if da_list else "Không ghi nhận"
    ho_hap_text = ", ".join(ho_hap_list) if ho_hap_list else "Không ghi nhận"
    
    return f"""
    <div style="background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px; font-size: 12px; line-height: 1.5; color: #1e293b; margin-bottom: 10px;">
        <div style="border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; margin-bottom: 8px; font-weight: bold; color: #1d4ed8; text-transform: uppercase;">
            {title}
        </div>
        <div style="margin-bottom: 5px;">
            <strong>Tuổi:</strong> {tuoi} | <strong>HATT đo:</strong> <span style="color: #b91c1c; font-weight: bold;">{ha} mmHg</span>
        </div>
        <div style="background-color: #fff1f2; border: 1px solid #fecdd3; border-radius: 4px; padding: 5px; margin-bottom: 5px;">
            <strong>Dị nguyên nghi ngờ:</strong> Thức ăn: {thuc_an} | Thuốc: {thuoc}
        </div>
        <div style="background-color: #fefce8; border: 1px solid #fef08a; border-radius: 4px; padding: 5px; margin-bottom: 5px;">
            <strong>Triệu chứng lâm sàng:</strong><br>
            • Da/Niêm mạc: {da_text}<br>
            • Hô hấp: {ho_hap_text}
        </div>
        <div style="background-color: #f3e8ff; border: 1px solid #e9d5ff; border-radius: 4px; padding: 5px; margin-bottom: 5px;">
            <strong>Mày đay & Xét nghiệm:</strong><br>
            • Sẩn phù: {san_phu} | Khởi phát: {khoi_phat}<br>
            • ASST: {asst} | IgE anti-IL24: {il24}
        </div>
        <div style="font-size: 11px; color: #64748b; font-style: italic; text-align: center; margin-top: 4px;">
            Bác sĩ đối chiếu tóm tắt này để chỉnh số đo bên ô JSON bên cạnh
        </div>
    </div>
    """

LAYERS = (
    ("T1 · Sốc phản vệ", ("R-SOC",)),
    ("T2 · Phản vệ và theo dõi", ("R01-PV", "R02-PV", "R03-PV", "R-PV-THEODOI")),
    ("T3 · Mày đay cấp", ("R-SANGLOC-CAP", "R01-CAP-NANG", "R01-CAP-THUONG")),
    ("T4 · Mày đay cảm ứng mạn tính — CIndU", (
        "R-CindU-00", "R-CindU-01", "R-CindU-02", "R-CindU-03", "R-CindU-04",
    )),
    ("T5 · Mày đay tự phát mạn tính — CSU", (
        "R-CSU-00", "R-GD-01", "R-GD-02", "R-CSU-T1-01", "R-CSU-T1-02",
        "R-CSU-T2-01", "R-CSU-OVL-01", "R-CSU-UNK-01", "R-CSU-UNK-02",
    )),
    ("T6 · Chưa đủ dữ kiện / ngoại lệ", ("R-DEFAULT",)),
)


def clear_result() -> None:
    st.session_state["result"] = None
    st.session_state["run_error"] = None


def reject_constant(value: str) -> None:
    raise ValueError("JSON không hỗ trợ NaN hoặc Infinity.")


def parse_patient(text: str) -> Dict[str, Any]:
    data = json.loads(text, parse_constant=reject_constant)
    if not isinstance(data, dict):
        raise ValueError("Đầu vào phải là một JSON object.")
    patient = data.get("du_lieu", data)
    if not isinstance(patient, dict):
        raise ValueError("du_lieu phải là một JSON object.")
    metadata = {"nhan", "expected_engine", "workflow_gap", "id", "mo_ta"}
    return {key: value for key, value in patient.items() if key not in metadata}


def render() -> None:
    st.set_page_config(page_title="Hệ thống Rule-based Mày đay", page_icon="🩺", layout="wide")
    st.title("HỆ THỐNG RULE-BASED MÀY ĐAY")
    with st.expander("Cách sử dụng web", expanded=True):
        st.markdown(
            "1. Chọn đầu ra và ca giả định (hoặc tải file bệnh án mới); bấm **Phân loại và giải thích**.\n"
            "2. Xem trạng thái, rule được chọn và rule chặn; mở **Logic suy luận** để xem cách hệ thống suy luận ra kết quả.\n"
            "3. Có thể sửa json để thử các trường hợp trước/tại/sau ngưỡng phân loại, sửa một biến mỗi lần hoặc xóa một trường rồi chạy lại.\n"
            "4. So với kết quả kì vọng xem kết quả thay đổi thế nào."
        )
        st.subheader("Bảng ý nghĩa các trạng thái hệ thống")
        st.table([{"Trạng thái": status, "Ý nghĩa lâm sàng": explanation} for status, explanation in STATUS_HELP.items()])
        st.caption("TRUE/FALSE/UNKNOWN là trạng thái điều kiện, không phải nhãn bệnh. Ưu tiên số nhỏ hơn được xét trước.")
    try:
        engine = ClinicalRuleEngine(str(ROOT / "rules/classification_rules.yaml"))
        fixture = json.loads((ROOT / "data/synthetic/rule_logic_cases.json").read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        st.error(f"Không nạp được cấu hình demo ({type(exc).__name__}). Kiểm tra YAML và bộ ca giả định.")
        return

    rules = {rule["rule_id"]: rule for rule in engine.rules}
    targets = [rule for rule in engine.rules if "target_label" in rule]
    labels = list(dict.fromkeys(rule["target_label"] for rule in targets))
    MODULES = {
        "Tất cả phân hệ": {
            "prefixes": None,
            "rules": None,
            "labels": labels,
        },
        "🔴 Phân hệ Phản vệ": {
            "prefixes": ["PV", "SOC"],
            "rules": ["R-SOC", "R01-PV", "R02-PV", "R03-PV", "R-PV-THEODOI"],
            "labels": ["Sốc phản vệ", "Phản vệ", "Theo dõi phản vệ (Chưa đủ dữ kiện)"],
        },
        "🟠 Phân hệ Mày đay cấp": {
            "prefixes": ["CAP"],
            "rules": ["R-SANGLOC-CAP", "R01-CAP-NANG", "R01-CAP-THUONG"],
            "labels": ["Mày đay cấp có dấu hiệu nặng", "Mày đay cấp thông thường"],
        },
        "🟣 Phân hệ Mày đay mạn (CIndU & CSU)": {
            "prefixes": ["CINDU", "CSU", "DEFAULT", "NEGATIVE", "EMPTY"],
            "rules": [
                "R-CindU-00", "R-CindU-01", "R-CindU-02", "R-CindU-03", "R-CindU-04",
                "R-CSU-00", "R-GD-01", "R-GD-02", "R-CSU-T1-01", "R-CSU-T1-02",
                "R-CSU-T2-01", "R-CSU-OVL-01", "R-CSU-UNK-01", "R-CSU-UNK-02", "R-DEFAULT"
            ],
            "labels": [
                "Mày đay CindU da vẽ nổi", "Mày đay CindU Choline (do nóng)",
                "Mày đay CindU do lạnh", "Mày đay CindU khác",
                "Mày đay CSU type 1", "Mày đay CSU type 2",
                "Mày đay CSU overlap", "Mày đay CSU unknown",
                "Chưa phân loại (Tiếp tục theo dõi)"
            ],
        }
    }

    st.sidebar.header("Chọn phân hệ & nguồn bệnh án")
    selected_module_name = st.sidebar.selectbox(
        "1. Phân hệ bệnh án:",
        list(MODULES.keys()),
        key="selected_module",
        on_change=clear_result
    )
    mod_info = MODULES[selected_module_name]

    data_source_mode = st.sidebar.radio(
        "2. Chọn nguồn bệnh án:",
        ["Ca giả định mẫu", "Tải file mới (.json, .csv)"],
        key="source_mode",
        on_change=clear_result
    )

    uploaded_file = None
    if data_source_mode == "Tải file mới (.json, .csv)":
        uploaded_file = st.sidebar.file_uploader(
            "Tải file hồ sơ bệnh nhân:",
            type=["json", "csv"],
            key="sidebar_patient_uploader",
            on_change=clear_result
        )
        if uploaded_file is not None:
            try:
                file_name = uploaded_file.name
                if file_name.endswith(".json"):
                    raw_data = json.loads(uploaded_file.getvalue().decode("utf-8"))
                    patient_data = raw_data.get("du_lieu", raw_data)
                    st.session_state["patient_json"] = json.dumps(patient_data, ensure_ascii=False, indent=2)
                    st.sidebar.success(f"Đã nạp file: {file_name}")
                elif file_name.endswith(".csv"):
                    csv_data = parse_csv_patient(uploaded_file.getvalue())
                    st.session_state["patient_json"] = json.dumps(csv_data, ensure_ascii=False, indent=2)
                    st.sidebar.success(f"Đã nạp CSV: {file_name}")
            except Exception as upload_err:
                st.sidebar.error(f"Lỗi đọc file: {upload_err}")
        case_id = uploaded_file.name if uploaded_file else "Bệnh nhân mới"
        selected_case = {"mo_ta": f"Hồ sơ mới: {case_id} ({selected_module_name})", "du_lieu": {}, "workflow_gap": None, "expected_engine": {}}
    else:
        if mod_info["prefixes"] is None:
            candidate_cases = fixture["cases"]
            candidate_labels = labels
        else:
            candidate_cases = [
                case for case in fixture["cases"]
                if any(case["id"].startswith(p) for p in mod_info["prefixes"])
                or case.get("expected_engine", {}).get("matched_rule_id") in mod_info["rules"]
            ]
            candidate_labels = [l for l in labels if l in mod_info["labels"]]

        selected_label = st.sidebar.selectbox(
            "3. Đầu ra cần minh họa:",
            ["Tất cả"] + candidate_labels,
            key="output_label",
            on_change=clear_result,
        )
        selected_rules = {rule["rule_id"] for rule in targets if rule["target_label"] == selected_label}
        cases = [
            case for case in candidate_cases
            if selected_label == "Tất cả"
            or case["expected_engine"].get("matched_rule_id") in selected_rules
            or selected_rules.intersection(case["expected_engine"].get("rule_results", {}))
        ]
        if not cases:
            st.warning("Chưa có ca minh họa cho tiêu chí này trong phân hệ đã chọn.")
            return
        by_id = {case["id"]: case for case in cases}
        if st.session_state.get("case_id") not in by_id:
            st.session_state["case_id"] = cases[0]["id"]
        case_id = st.sidebar.selectbox(
            "4. Bệnh án giả định:",
            list(by_id),
            key="case_id",
            on_change=clear_result,
            format_func=lambda identifier: f"{identifier} · {by_id[identifier]['mo_ta']}",
        )
        selected_case = by_id[case_id]
        if st.session_state.get("loaded_case") != case_id:
            st.session_state["patient_json"] = json.dumps(selected_case["du_lieu"], ensure_ascii=False, indent=2)
            st.session_state["loaded_case"] = case_id
            clear_result()
        st.sidebar.caption(f"{len(candidate_cases)} ca trong phân hệ · YAML {engine.rules_version}")

    input_tab, layers_tab, catalog_tab = st.tabs([
        "Bệnh án & kết quả", "Logic suy luận", "Bảng quy tắc & Mức ưu tiên",
    ])
    with input_tab:
        left, right = st.columns([1, 1])
        with left:
            st.subheader("Dữ liệu bệnh án (Phiếu khám lâm sàng & Mã JSON)")
            
            try:
                current_patient = parse_patient(st.session_state.get("patient_json", "{}"))
            except (ValueError, RecursionError):
                current_patient = None

            # Bố cục song song: Phiếu khám lâm sàng tóm tắt (HTML) bên cạnh Ô soạn thảo JSON
            col_html, col_json = st.columns([1, 1])
            with col_html:
                card_title = f"Phiếu khám: {case_id}"
                st.markdown(generate_clinical_summary_html(current_patient, title=card_title), unsafe_allow_html=True)
            with col_json:
                st.caption("Mã JSON bệnh án (Chỉnh sửa tùy ý):")
                st.text_area("Mã JSON bệnh án", height=320, key="patient_json", on_change=clear_result, label_visibility="collapsed")

            input_changed = current_patient != selected_case.get("du_lieu", {})
            if st.button("Phân loại và giải thích", key="classify", type="primary"):
                clear_result()
                try:
                    patient = parse_patient(st.session_state["patient_json"])
                except (ValueError, RecursionError):
                    st.session_state["run_error"] = (
                        "JSON không hợp lệ. Cần một object CANONICAL hoặc object có du_lieu là object; "
                        "không dùng NaN/Infinity."
                    )
                else:
                    try:
                        st.session_state["result"] = engine.classify_patient(patient)
                    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
                        # F-12 remains in the engine; the demo must show the failure, not invent a label.
                        st.session_state["run_error"] = (
                            f"Engine không hoàn tất ({type(exc).__name__}). Kiểm tra kiểu dữ liệu; "
                            "lỗi công thức HATT F-12 đã được ghi nhận. Không có kết luận bệnh."
                        )
            with st.expander("Kỳ vọng của ca gốc — để đối chiếu sau suy diễn"):
                if input_changed:
                    st.warning("Dữ liệu JSON hiện tại đã được chỉnh sửa; bảng kỳ vọng bên dưới là tiêu chuẩn của ca mẫu ban đầu.")
                
                exp_engine = selected_case.get("expected_engine", {})
                if isinstance(exp_engine, dict):
                    if "exception" in exp_engine:
                        st.error(f"Ca mẫu gốc ghi nhận lỗi ngoại lệ kỹ thuật: **{exp_engine['exception']}**")
                    else:
                        exp_label = exp_engine.get("predicted_label") or "Chưa kết luận bệnh"
                        exp_status = exp_engine.get("status", "Chưa rõ")
                        exp_matched = exp_engine.get("matched_rule_id") or "Không có"
                        
                        col_e1, col_e2, col_e3 = st.columns(3)
                        col_e1.metric("Nhãn kỳ vọng", exp_label)
                        col_e2.metric("Trạng thái", exp_status)
                        col_e3.metric("Rule chính", exp_matched)
                        
                        st.markdown("#### Bảng các quy tắc (Rule) kỳ vọng cho ca này:")
                        exp_rules_table = []
                        exp_rule_results = exp_engine.get("rule_results", {})
                        
                        rule_ids_to_show = list(exp_rule_results.keys())
                        if exp_matched and exp_matched != "Không có" and exp_matched not in rule_ids_to_show:
                            rule_ids_to_show.insert(0, exp_matched)
                            
                        for r_id in rule_ids_to_show:
                            r_info = rules.get(r_id, {})
                            r_name = r_info.get("name", r_id)
                            r_val = exp_rule_results.get(r_id)
                            
                            if r_id == exp_matched:
                                status_str = "THỎA MÃN (Chính)"
                            elif r_val is True:
                                status_str = "ĐẠT"
                            elif r_val is False:
                                status_str = "KHÔNG ĐẠT"
                            elif r_val is None:
                                status_str = "CHƯA RÕ"
                            else:
                                status_str = str(r_val)
                                
                            exp_rules_table.append({
                                "Mã Rule": r_id,
                                "Nội dung y khoa (Ngôn ngữ thường)": r_name,
                                "Kỳ vọng": status_str
                            })
                            
                        if exp_rules_table:
                            st.table(exp_rules_table)
                        else:
                            st.info("Ca này không có danh sách chi tiết các rule trong hồ sơ gốc.")
                else:
                    st.write(str(exp_engine))
                st.caption("Kỳ vọng mô tả kết quả chuẩn của ca mẫu, dùng để bác sĩ đối chiếu sau khi chạy chẩn đoán.")

        result = st.session_state["result"]
        with right:
            st.subheader("Kết quả chẩn đoán của hệ thống")
            if st.session_state["run_error"]:
                st.error(st.session_state["run_error"])
            elif result is None:
                st.info("Bấm Phân loại và giải thích để xem kết quả cho JSON hiện tại.")
            else:
                a, b = st.columns(2)
                a.metric("Trạng thái", result["status"])
                b.metric("Ưu tiên", result["priority"])
                explanation = f"**{result['status']}** — {STATUS_HELP.get(result['status'], '')}"
                if result["status"] == "NEEDS_REVIEW":
                    st.error(explanation)
                elif result["status"] in {"INSUFFICIENT_DATA", "UNRESOLVED"}:
                    st.warning(explanation)
                else:
                    st.info(explanation)
                if current_patient and isinstance(current_patient.get("huyet_ap_tam_thu_thap_nhat"), bool):
                    st.error("**F-12 · HATT boolean: nhãn bên dưới không đáng tin cậy.** Engine có thể coi true/false là số khi tính công thức; cần sửa kiểu dữ liệu và chạy lại.")
                st.subheader(result["predicted_label"] or "Chưa kết luận bệnh")
                st.write("**Lý do lâm sàng:**", result["decision_trace"])
                st.write("**Rule được chọn:**", result["matched_rule_id"] or "Không có")
                st.write("**Rule cùng khớp:**", ", ".join(result["matched_rule_ids"]) or "Không có")
                st.write("**Rule chặn / xung đột:**", ", ".join(result["blocking_rule_ids"]) or "Không có")
                if result["missing_fields"]:
                    st.write("**Trường cần bổ sung:**")
                    st.write(result["missing_fields"])
                st.caption(f"YAML {result['rules_version']} · SHA-256 {result['rules_sha256']}")
                
                # BẢNG CÁC QUY TẮC Y KHOA ĐƯỢC ĐỐI CHIẾU CHO CA NÀY (NGÔN NGỮ THƯỜNG)
                st.markdown("#### Bảng các quy tắc (Rule) được đối chiếu ca này:")
                matched_id = result.get("matched_rule_id")
                active_rules_rows = []
                for r_id, r_info in rules.items():
                    r_val = result["rule_results"].get(r_id)
                    if r_id == matched_id or r_val is True or r_id in result.get("blocking_rule_ids", []):
                        status_str = "THỎA MÃN (Chính)" if r_id == matched_id else ("ĐẠT" if r_val is True else "BỊ CHẶN")
                        active_rules_rows.append({
                            "Mã Rule": r_id,
                            "Nội dung y khoa (Ngôn ngữ thường)": r_info.get("name", r_id),
                            "Đánh giá": status_str
                        })
                if active_rules_rows:
                    st.table(active_rules_rows)

                st.download_button("Tải kết quả JSON", json.dumps(result, ensure_ascii=False, indent=2),
                                   file_name="rule_result.json", mime="application/json")
            if selected_case["workflow_gap"]:
                issue_id = selected_case["workflow_gap"]
                st.warning(
                    f"**Ca gốc · {issue_id}** — {ISSUE_HELP[issue_id]} "
                    "Đây là chú thích của ca gốc; JSON đã sửa có thể có vấn đề khác."
                )

    with layers_tab:
        st.subheader("Logic suy luận của hệ thống")
        st.caption("Cách máy tính đối chiếu qua từng tầng quy tắc và lý do đưa ra kết luận chẩn đoán bằng ngôn ngữ lâm sàng dễ hiểu.")

        if result:
            st.markdown(f"### Kết luận chẩn đoán: **{result.get('predicted_label', 'Chưa kết luận bệnh')}**")
            st.info(f"**Lý do lâm sàng:** {result.get('decision_trace', 'Không có mô tả')}")

            # Diễn giải suy luận từng bước cho ca này
            st.markdown("#### Các bước suy luận của hệ thống đối với bệnh án này:")
            matched_id = result.get("matched_rule_id")
            blocking_ids = result.get("blocking_rule_ids", [])

            steps_data = []
            steps_data.append({
                "Bước suy luận": "1. Sàng lọc ban đầu",
                "Nội dung đối chiếu": "Đánh giá các điều kiện cơ sở về thời gian khởi phát, triệu chứng da, hô hấp, tuần hoàn.",
                "Kết quả": "ĐẠT — Đủ dữ kiện đưa vào bộ máy suy luận"
            })

            if matched_id == "R-SOC":
                steps_data.append({
                    "Bước suy luận": "2. Đánh giá Sốc phản vệ (Ưu tiên 1)",
                    "Nội dung đối chiếu": "Kiểm tra tiêu chuẩn phản vệ kết hợp tụt huyết áp nghiêm trọng theo tuổi (HATT < 90 mmHg hoặc giảm > 30% nền).",
                    "Kết quả": "THỎA MÃN — Kết luận SỐC PHẢN VỆ ngay lập tức"
                })
            elif matched_id in ["R01-PV", "R02-PV", "R03-PV"]:
                steps_data.append({
                    "Bước suy luận": "2. Đánh giá Sốc phản vệ (Ưu tiên 1)",
                    "Nội dung đối chiếu": "Kiểm tra tụt huyết áp theo tuổi.",
                    "Kết quả": "KHÔNG ĐẠT (Huyết áp chưa tụt) — Loại trừ Sốc phản vệ"
                })
                steps_data.append({
                    "Bước suy luận": "3. Đánh giá Phản vệ (Ưu tiên 2)",
                    "Nội dung đối chiếu": f"Thỏa mãn tiêu chuẩn {matched_id} sau tiếp xúc dị nguyên kèm tổn thương đa cơ quan.",
                    "Kết quả": f"THỎA MÃN — Kết luận PHẢN VỆ theo quy tắc {matched_id}"
                })
            elif "CAP" in str(matched_id):
                steps_data.append({
                    "Bước suy luận": "2. Sàng lọc cấp tính (R-SANGLOC-CAP)",
                    "Nội dung đối chiếu": "Khởi phát dưới 6 tuần (<= 1008 giờ) có sẩn phù bờ rõ.",
                    "Kết quả": "ĐẠT tiêu chuẩn Mày đay cấp"
                })
                steps_data.append({
                    "Bước suy luận": "3. Đánh giá mức độ nặng",
                    "Nội dung đối chiếu": f"Đối chiếu các dấu hiệu nặng (Ngứa nhiều, phù mạch, toàn thân). Quy tắc thỏa mãn: {matched_id}.",
                    "Kết quả": f"KẾT LUẬN — {result.get('predicted_label')}"
                })
            else:
                steps_data.append({
                    "Bước suy luận": "2. Đánh giá theo phân hệ",
                    "Nội dung đối chiếu": f"Hồ sơ đối chiếu qua các quy tắc chẩn đoán, thỏa mãn quy tắc: {matched_id}.",
                    "Kết quả": f"KẾT LUẬN — {result.get('predicted_label')}"
                })

            if blocking_ids:
                steps_data.append({
                    "Bước suy luận": "4. Chặn các quy tắc thấp hơn",
                    "Nội dung đối chiếu": f"Các quy tắc có mức ưu tiên thấp hơn ({', '.join(blocking_ids)}) bị chặn theo thứ tự ưu tiên y khoa.",
                    "Kết quả": "ĐÃ CHẶN theo luật ưu tiên"
                })

            st.table(steps_data)
        else:
            st.info("Chưa có kết quả chạy. Vui lòng bấm nút **Phân loại và giải thích** ở Tab 1 để xem các bước máy tính suy luận ra kết quả cho ca này.")



    with catalog_tab:
        st.subheader("Bảng quy tắc chẩn đoán & Mức độ ưu tiên")
        st.caption("Tổng hợp quy tắc theo từng bệnh án (Phản vệ, Mày đay cấp, Mày đay mạn) bằng ngôn ngữ y khoa dễ hiểu, không dùng mã code.")
        
        tab_pv, tab_cap, tab_man = st.tabs(["🔴 Phân hệ Phản vệ", "🟠 Phân hệ Mày đay cấp", "🟣 Phân hệ Mày đay mạn (CIndU & CSU)"])
        
        with tab_pv:
            st.markdown("#### Bảng quy tắc phân hệ Phản vệ")
            pv_rules_data = [
                {
                    "Mức ưu tiên": "Ưu tiên 1 (Tối khẩn)",
                    "Mã Rule": "R-SOC",
                    "Kết luận bệnh": "Sốc phản vệ",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Thỏa mãn tiêu chuẩn phản vệ (R01, R02 hoặc R03) VÀ có tụt huyết áp theo lứa tuổi (HATT < 90 mmHg hoặc giảm > 30% so với nền)."
                },
                {
                    "Mức ưu tiên": "Ưu tiên 2 (Cấp cứu)",
                    "Mã Rule": "R01-PV",
                    "Kết luận bệnh": "Phản vệ (Không rõ dị nguyên)",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Bệnh cảnh cấp tính ở da/niêm mạc (mày đay, phù môi/lưỡi) kèm ít nhất một biểu hiện suy hô hấp (khó thở, thở rít) hoặc tụt huyết áp."
                },
                {
                    "Mức ưu tiên": "Ưu tiên 2 (Cấp cứu)",
                    "Mã Rule": "R02-PV",
                    "Kết luận bệnh": "Phản vệ (Dị nguyên nghi ngờ)",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Sau tiếp xúc thức ăn/thuốc/côn trùng nghi ngờ, xuất hiện đồng thời tổn thương từ 2 trong 4 hệ: Da/niêm mạc, Hô hấp, Tuần hoàn, Tiêu hóa nặng (đau quặn bụng, nôn)."
                },
                {
                    "Mức ưu tiên": "Ưu tiên 2 (Cấp cứu)",
                    "Mã Rule": "R03-PV",
                    "Kết luận bệnh": "Phản vệ (Dị nguyên đã biết)",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Sau tiếp xúc với dị nguyên người bệnh đã từng dị ứng, xuất hiện tụt huyết áp hoặc co thắt đường thở (ngoài đường hít)."
                },
                {
                    "Mức ưu tiên": "Ưu tiên 3",
                    "Mã Rule": "THEODOIPV",
                    "Kết luận bệnh": "Tiếp tục theo dõi phản vệ",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Có triệu chứng dị ứng nhưng chưa đủ tiêu chí kết luận Sốc hoặc Phản vệ; tự động kích hoạt để bác sĩ theo dõi sát."
                }
            ]
            st.table(pv_rules_data)

        with tab_cap:
            st.markdown("#### Bảng quy tắc phân hệ Mày đay cấp tính")
            cap_rules_data = [
                {
                    "Mức ưu tiên": "Tiên quyết",
                    "Mã Rule": "R-SANGLOC-CAP",
                    "Kết luận bệnh": "Sàng lọc cấp tính",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Hiện tại có sẩn phù dạng bờ rõ (tròn, vòng, bản đồ) + Có ảnh chụp sẩn phù + Thời gian khởi phát <= 1008 giờ (6 tuần)."
                },
                {
                    "Mức ưu tiên": "Ưu tiên 1 (Bước 1)",
                    "Mã Rule": "R01-CAP-NANG-NGUA",
                    "Kết luận bệnh": "Cấp nặng do Ngứa nhiều",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Triệu chứng da ghi nhận 'Ngứa nhiều' -> Phân loại ngay vào nhóm Cấp có dấu hiệu nặng."
                },
                {
                    "Mức ưu tiên": "Ưu tiên 1 (Bước 2)",
                    "Mã Rule": "R01-CAP-NANG-PHUMACH",
                    "Kết luận bệnh": "Cấp nặng do Phù mạch",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Có phù mạch đáng kể tại môi, lưỡi, thanh quản, mi mắt hoặc tiền sử đã phải nhập viện >= 1 lần do phù mạch."
                },
                {
                    "Mức ưu tiên": "Ưu tiên 1 (Bước 3)",
                    "Mã Rule": "R02-CAP-NANG-TOANTHAN",
                    "Kết luận bệnh": "Cấp nặng do Toàn thân",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Sẩn phù kèm dấu hiệu toàn thân: Tiêu hóa (nôn, đau bụng), Hô hấp nhẹ (khò khè), hoặc tổn thương lan rộng > 50% diện tích cơ thể (BSA), hoặc > 50 nốt sẩn."
                },
                {
                    "Mức ưu tiên": "Ưu tiên 2 (Bước 4)",
                    "Mã Rule": "R01-CAP-THUONG",
                    "Kết luận bệnh": "Mày đay cấp thông thường",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Có sẩn phù cấp tính nhưng phủ định toàn bộ các dấu hiệu nặng ở Bước 1, Bước 2 và Bước 3."
                }
            ]
            st.table(cap_rules_data)

        with tab_man:
            st.markdown("#### Bảng quy tắc phân hệ Mày đay mạn tính (CIndU & CSU)")
            man_rules_data = [
                {
                    "Mức ưu tiên": "Nhóm CIndU",
                    "Mã Rule": "R-CindU-01",
                    "Kết luận bệnh": "Mày đay Da vẽ nổi (Symptomatic Dermographism)",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Khởi phát > 6 tuần sau khi có kích thích cọ xát cơ học + Test da vẽ nổi (FricTest) dương tính (+)."
                },
                {
                    "Mức ưu tiên": "Nhóm CIndU",
                    "Mã Rule": "R-CindU-02",
                    "Kết luận bệnh": "Mày đay Cholinergic",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Sẩn phù xuất hiện khi nhiệt độ cơ thể tăng (nóng bức, gắng sức, mồ hôi) + Test kích thích Cholinergic (+)."
                },
                {
                    "Mức ưu tiên": "Nhóm CIndU",
                    "Mã Rule": "R-CindU-03",
                    "Kết luận bệnh": "Mày đay do Lạnh (Cold Urticaria)",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Xuất hiện sau khi tiếp xúc không khí/nước lạnh + Test cục đá (TempTest / Ice cube) dương tính (+)."
                },
                {
                    "Mức ưu tiên": "Nhóm CIndU",
                    "Mã Rule": "R-CindU-04",
                    "Kết luận bệnh": "Mày đay cảm ứng thể khác",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Âm tính với các kích thích trên nhưng dương tính với áp lực chậm, ánh sáng mặt trời hoặc tiếp xúc nước."
                },
                {
                    "Mức ưu tiên": "Nhóm CSU",
                    "Mã Rule": "R-CSU-T1",
                    "Kết luận bệnh": "Mày đay CSU Thể tự dị ứng (Type I)",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Khởi phát > 6 tuần, test ASST (+), theo dõi >= 60 ngày: IgE kháng IL-24 dương tính (+)."
                },
                {
                    "Mức ưu tiên": "Nhóm CSU",
                    "Mã Rule": "R-CSU-T2",
                    "Kết luận bệnh": "Mày đay CSU Thể tự miễn (Type IIb)",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Khởi phát > 6 tuần, test ASST (+), theo dõi >= 60 ngày: Tự kháng thể IgG dương tính (+) và IgE kháng IL-24 âm tính (-)."
                },
                {
                    "Mức ưu tiên": "Nhóm CSU",
                    "Mã Rule": "R-CSU-OVL",
                    "Kết luận bệnh": "Mày đay CSU Thể chồng lấp (Overlap)",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Đồng thời dương tính cả tự kháng thể IgG và IgE kháng IL-24."
                },
                {
                    "Mức ưu tiên": "Nhóm CSU",
                    "Mã Rule": "R-CSU-UNK",
                    "Kết luận bệnh": "Mày đay CSU Không xác định (Unknown)",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Cả tự kháng thể IgG và IgE kháng IL-24 đều âm tính (-)."
                },
                {
                    "Mức ưu tiên": "Ngoại lệ",
                    "Mã Rule": "R-DEFAULT",
                    "Kết luận bệnh": "Chưa phân loại (Tiếp tục theo dõi)",
                    "Tiêu chí chẩn đoán (Ngôn ngữ thường)": "Hồ sơ mạn tính thiếu kết quả bắt buộc: ASST còn trống, chưa đủ 60 ngày theo dõi hoặc chưa có xét nghiệm ELISA."
                }
            ]
            st.table(man_rules_data)


if __name__ == "__main__":
    render()
