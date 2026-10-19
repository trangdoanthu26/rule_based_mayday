import csv
import io
import json
import re
from html import escape
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st

from src.pipeline import classify_form, load_engines


ROOT = Path(__file__).resolve().parent
ISSUE_HELP = {
    "F-01": "Dữ liệu cấp dạng chuỗi cũ cần đổi sang danh sách triệu chứng đúng schema.",
    "F-02": "Các khoảng tuổi sốc đã liên tục từ lúc sinh; không tự làm tròn tuổi.",
    "F-03": "Đúng 6 tuần: cấp dùng <=1008 giờ, mạn dùng >6 tuần; ranh giới và nguồn thời gian cần chốt.",
    "F-04": "R03 dùng tác nhân nghi ngờ thay tiêu chí dị nguyên đã biết; các rule phản vệ chưa kiểm tra thời điểm.",
    "F-05": "Sốc tham chiếu R01/R02/R03 sau thay đổi của issue #7.",
    "F-06": "CIndU khác chưa loại Ice cube dương; Adrenergic chưa có nhánh; nhiều test dương cần chính sách phân thể.",
    "F-07": "Chưa có validator enum/range: giá trị test sai có thể được coi là không dương; HATT âm vẫn có thể thỏa rule.",
    "F-08": "Stella FALSE/UNKNOWN vẫn có thể vào CSU GĐ2 vì IgE <40; YAML khác workflow, chưa có nhánh loại cohort.",
    "F-09": "Định tuyến theo mẫu mạn giữ rule phản vệ ngoài phạm vi CSU.",
    "F-10": "CIndU được chọn trước CSU khi cùng khớp; điều kiện cohort và biểu diễn đồng mắc chưa chốt.",
    "F-11": "ASST null có thể kích hoạt fallback ngoài CSU; rule UNKNOWN ưu tiên cao vẫn có thể chặn fallback.",
    "F-12": "Dữ liệu HATT sai kiểu cần rà soát, không dùng để kết luận sốc.",
    "F-13": "Lý do UNKNOWN có thể bị lẫn với lỗi kiểu từ nhánh OR đã đủ bằng chứng, làm sai lý do cần rà soát.",
}
STATUS_HELP = {
    "CLASSIFIED": "Hệ thống đã xác định nhóm phân loại từ dữ liệu đã nhập.",
    "THEODOIPV": "Đủ dữ kiện đánh giá nhưng chưa đạt tiêu chí sốc hoặc phản vệ; tiếp tục theo dõi.",
    "INSUFFICIENT_DATA": "Thiếu dữ kiện hoặc chưa đủ thời gian; xem rule chặn và trường cần bổ sung.",
    "NEEDS_REVIEW": "Chưa có kết luận bệnh: có xung đột hoặc dữ liệu cần rà soát; xem điều kiện và trace của các rule chặn.",
    "UNRESOLVED": "Không có rule đích phù hợp sau đánh giá hiện tại.",
}
STATUS_LABELS = {
    "CLASSIFIED": "ĐÃ PHÂN LOẠI",
    "THEODOIPV": "THEO DÕI PHẢN VỆ",
    "INSUFFICIENT_DATA": "CHƯA ĐỦ DỮ KIỆN",
    "NEEDS_REVIEW": "CẦN RÀ SOÁT",
    "UNRESOLVED": "CHƯA XÁC ĐỊNH PHÂN LOẠI",
}


def parse_csv_patient(file_bytes: bytes) -> Dict[str, Any]:
    text = file_bytes.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        parsed = {}
        for k, v in row.items():
            if k is None:
                raise ValueError("Dòng CSV có nhiều cột hơn tiêu đề.")
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


LAYERS = (
    ("T1 · Sốc phản vệ", ("R-SOC",)),
    ("T2 · Phản vệ và theo dõi", ("R01-PV", "R02-PV", "R03-PV", "R-PV-THEODOI")),
    ("T3 · Mày đay cấp", ("R-SANGLOC-CAP", "R01-CAP-NANG-NGUA", "R02-CAP-NANG-PHUMACH",
                           "R03-CAP-NANG-CONLAI", "R01-CAP-THUONG")),
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
    metadata = {"nhan", "expected_engine", "workflow_gap", "id", "mo_ta", "form_type"}
    return {key: value for key, value in patient.items() if key not in metadata}


def clinical_field_labels() -> Dict[str, str]:
    labels = {}
    for path in sorted((ROOT / "docs/01_data_dictionary").glob("*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            cells = line.split("|")
            if len(cells) > 5:
                field = re.fullmatch(r"\s*\*\*`([^`]+)`\*\*\s*", cells[1])
                if field:
                    label = cells[2].strip().replace("**", "").replace("`", "")
                    unit = cells[4].strip()
                    if "_pv" in field[1]:
                        label += " (phản vệ)"
                    labels[field[1]] = label + (f" ({unit})" if unit not in {"null", "", "-"} else "")
    labels.update({
        "tuoi": "Tuổi (năm)", "so_ngay_theo_doi": "Số ngày theo dõi (ngày)",
        "danh_sach_chon": "Các mục được chọn", "co_khong": "Ghi nhận",
        "dau_bung_quan_that": "Đau bụng quặn thắt", "non_so_lan": "Số lần nôn",
        "non": "Nôn", "buon_non_tieu_chay": "Buồn nôn / tiêu chảy",
        "stella_dat": "Đạt tiêu chuẩn Stella", "dang_ton_thuong": "Dạng tổn thương",
        "muc_do_lan_rong": "Mức độ lan rộng", "phan_bo": "Phân bố tổn thương",
        "khac_ghi_ro": "Thông tin khác", "dac_biet_ghi_ro": "Chi tiết vị trí đặc biệt",
    })
    return labels


def evidence_highlights(result: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, str]:
    """Mark evaluated fields, including dependencies, without re-running rules."""
    related = ({result["matched_rule_id"]} if result["matched_rule_id"]
               else set(result["blocking_rule_ids"]))
    pending = [rules[identifier]["conditions"] for identifier in related]
    while pending:
        node = pending.pop()
        if isinstance(node, dict):
            reference = node.get("ref_rule")
            if reference in rules and reference not in related:
                related.add(reference)
                pending.append(rules[reference]["conditions"])
            pending.extend(value for value in node.values() if isinstance(value, (dict, list)))
        elif isinstance(node, list):
            pending.extend(node)
    highlights = {
        event["field_path"]: "matched" for event in result["trace"]
        if event["rule_id"] in related and event["field_path"] and event["result"] is True
    }
    if result["status"] == "NEEDS_REVIEW":
        highlights.update({
            event["field_path"]: "review" for event in result["trace"]
            if event["rule_id"] in related and event["field_path"] and event["result"] is None
            and event["reason"] in {"INVALID_TYPE", "NON_FINITE"}
        })
    highlights.update({path: "missing" for path in result["missing_fields"]})
    return highlights


def patient_html(patient: Dict[str, Any], highlights: Optional[Dict[str, str]] = None) -> str:
    """Present the supplied fields without deriving or filling clinical data."""
    labels = clinical_field_labels()
    highlights = highlights or {}
    rendered_paths = set()
    badges = {"matched": "Khớp điều kiện", "missing": "Cần bổ sung", "review": "Cần rà soát"}

    def render_value(value: Any, path: str = "") -> str:
        if isinstance(value, dict):
            if not value:
                return "Chưa có thông tin"
            rows = []
            items = list(value.items())
            if not path:
                items.sort(key=lambda item: not any(
                    field == item[0] or field.startswith(item[0] + ".") for field in highlights
                ))
            for key, item in items:
                key = str(key)
                field = f"{path}.{key}" if path else key
                rendered_paths.add(field)
                state = highlights.get(field, "")
                marker = (f' data-field="{escape(field)}" data-evidence="{state}"'
                          if state in badges else "")
                badge = f"<small>{badges[state]}</small>" if state in badges else ""
                rows.append(f"<dt{marker}>{escape(labels.get(key, key))}{badge}</dt>"
                            f"<dd{marker}>{render_value(item, field)}</dd>")
            return "<dl>" + "".join(rows) + "</dl>"
        if isinstance(value, list):
            return ("<ul>" + "".join(f"<li>{render_value(item, path)}</li>" for item in value) + "</ul>"
                    if value else "Không có mục được chọn")
        if value is None or value == "":
            return "Chưa cung cấp"
        if isinstance(value, bool):
            return "Có" if value else "Không"
        if value == -1 or (isinstance(value, str) and value.strip().lower() == "unknown"):
            return "Không rõ"
        if isinstance(value, str) and value.strip().lower() == "n/a":
            return "Không áp dụng"
        return escape(str(value))

    content = render_value(patient)
    missing = "".join(
        f'<p data-field="{escape(field)}" data-evidence="missing">'
        + escape(" › ".join(labels.get(part, part) for part in field.split(".")))
        + "<small>Cần bổ sung</small>Chưa có trong JSON</p>"
        for field, state in highlights.items() if state == "missing" and field not in rendered_paths
    )
    return (
        '<section class="patient-sheet" aria-label="Bệnh án đang kiểm tra">'
        '<style>.patient-sheet{padding:0 .5rem 0 0;'
        'font-size:1rem}.patient-sheet dl{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);'
        'gap:.5rem 1rem;margin:.5rem 0}.patient-sheet dt{font-weight:600;overflow-wrap:anywhere}'
        '.patient-sheet dd{margin:0;overflow-wrap:anywhere}.patient-sheet ul{padding-left:1.2rem;margin:0}'
        '.patient-sheet dd dl{grid-template-columns:1fr;gap:.15rem}'
        '.patient-sheet>dl>dt,.patient-sheet>dl>dd{border-bottom:1px solid #8884;padding:.5rem 0}'
        '.patient-sheet [data-evidence="matched"]{background:#168a6430}'
        '.patient-sheet [data-evidence="missing"]{background:#c58a1630}'
        '.patient-sheet [data-evidence="review"]{background:#c9424230}'
        '.patient-sheet small{display:block;font-size:.75rem;font-weight:normal}'
        '@media(max-width:600px){.patient-sheet dl{grid-template-columns:1fr;gap:.25rem}}'
        '</style>' + missing + content + '</section>'
    )


def render() -> None:
    st.set_page_config(page_title="Rule-based Mề đay", page_icon="🔎", layout="wide")
    st.title("Hệ thống Rule-based mề đay")
    st.caption("Chọn bệnh án giả định, phân loại và đối chiếu dữ kiện với kết luận.")
    st.warning("Dữ liệu giả định · Các khác biệt CIndU/CSU và mapping RAW vẫn cần rà soát. Xem lưu ý theo ca.")
    with st.expander("Cách sử dụng web · Cách đọc kết quả", expanded=True):
        st.markdown(
            "1. Chọn mẫu bệnh án và ca giả định hoặc tải file JSON/CSV; bấm **Phân loại và giải thích**.\n"
            "2. Xem kết quả và trường thiếu; mở **Logic suy luận** để đối chiếu rule và trace.\n"
            "3. Sửa một biến trong JSON mỗi lần, thử trước/tại/sau ngưỡng hoặc xóa một trường rồi chạy lại.\n"
            "4. Kỳ vọng chỉ thuộc ca gốc; JSON đã sửa cần xác định kỳ vọng riêng."
        )
        st.table([{"Trạng thái": STATUS_LABELS[status], "Ý nghĩa": explanation}
                  for status, explanation in STATUS_HELP.items()])
        st.caption("TRUE/FALSE/UNKNOWN là trạng thái điều kiện, không phải nhãn bệnh. Ưu tiên số nhỏ hơn được xét trước.")
    try:
        engines = load_engines()
        fixture = json.loads((ROOT / "data/synthetic/rule_logic_cases.json").read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        st.error(f"Không nạp được cấu hình demo ({type(exc).__name__}). Kiểm tra YAML và bộ ca giả định.")
        return

    st.sidebar.header("Chọn nội dung minh họa")
    form_type = st.sidebar.selectbox(
        "Mẫu bệnh án", ["phan_ve", "cap", "man"],
        format_func=lambda value: {"phan_ve": "Phản vệ", "cap": "Mày đay cấp", "man": "Mày đay mạn"}[value],
        key="form_type", on_change=clear_result,
    )
    engine = engines[form_type]
    rules = {rule["rule_id"]: rule for rule in engine.rules}
    targets = [rule for rule in engine.rules if "target_label" in rule]
    labels = list(dict.fromkeys(rule["target_label"] for rule in targets))
    st.session_state.setdefault("result", None)
    st.session_state.setdefault("run_error", None)
    st.session_state.setdefault("patient_json", "{}")
    data_source_mode = st.sidebar.radio(
        "Chọn nguồn bệnh án", ["Ca giả định mẫu", "Tải file mới (.json, .csv)"],
        key="source_mode", on_change=clear_result,
    )
    if st.session_state.get("active_source") != data_source_mode:
        st.session_state["loaded_case"] = None
        st.session_state["loaded_upload"] = None
        st.session_state["patient_json"] = "{}"
        st.session_state["active_source"] = data_source_mode
        clear_result()

    selected_label = "Tất cả"
    if data_source_mode == "Tải file mới (.json, .csv)":
        uploaded_file = st.sidebar.file_uploader(
            "Tải file hồ sơ bệnh nhân", type=["json", "csv"],
            key="sidebar_patient_uploader", on_change=clear_result,
        )
        case_id = uploaded_file.name if uploaded_file else "Bệnh án mới"
        selected_case = {"mo_ta": f"Hồ sơ mới: {case_id}", "du_lieu": {},
                         "workflow_gap": None, "expected_engine": {}}
        if uploaded_file is not None:
            upload_key = (uploaded_file.name, uploaded_file.getvalue())
            if st.session_state.get("loaded_upload") != upload_key:
                st.session_state["loaded_upload"] = upload_key
                st.session_state["patient_json"] = ""
                clear_result()
                try:
                    if uploaded_file.name.lower().endswith(".json"):
                        patient_data = parse_patient(uploaded_file.getvalue().decode("utf-8"))
                    else:
                        patient_data = parse_patient(json.dumps(
                            parse_csv_patient(uploaded_file.getvalue()), allow_nan=False,
                        ))
                    st.session_state["patient_json"] = json.dumps(patient_data, ensure_ascii=False, indent=2)
                    st.sidebar.success(f"Đã nạp file: {case_id}")
                except (ValueError, UnicodeError, RecursionError, csv.Error) as exc:
                    st.sidebar.error(f"Không đọc được bệnh án ({type(exc).__name__}). Kiểm tra JSON/CSV.")
        elif st.session_state.get("loaded_upload") is not None:
            st.session_state["loaded_upload"] = None
            st.session_state["patient_json"] = "{}"
            clear_result()
    else:
        if st.session_state.get("output_label") not in ["Tất cả"] + labels:
            st.session_state["output_label"] = "Tất cả"
        selected_label = st.sidebar.selectbox(
            "Đầu ra cần minh họa", ["Tất cả"] + labels, key="output_label", on_change=clear_result,
        )
        selected_rules = {rule["rule_id"] for rule in targets if rule["target_label"] == selected_label}
        cases = [case for case in fixture["cases"] if case["form_type"] == form_type
                 and (selected_label == "Tất cả"
                      or case["expected_engine"].get("matched_rule_id") in selected_rules
                      or selected_rules.intersection(case["expected_engine"].get("rule_results", {})))]
        if not cases:
            st.warning("Chưa có ca minh họa cho tiêu chí này trong mẫu đã chọn.")
            return
        by_id = {case["id"]: case for case in cases}
        if st.session_state.get("case_id") not in by_id:
            st.session_state["case_id"] = cases[0]["id"]
        case_id = st.sidebar.selectbox(
            "Bệnh án giả định", list(by_id), key="case_id", on_change=clear_result,
            format_func=lambda identifier: f"{identifier} · {by_id[identifier]['mo_ta']}" if identifier in by_id else identifier,
        )
        selected_case = by_id[case_id]
        if st.session_state.get("loaded_case") != case_id:
            st.session_state["patient_json"] = json.dumps(selected_case["du_lieu"], ensure_ascii=False, indent=2)
            st.session_state["loaded_case"] = case_id
            clear_result()
        st.sidebar.caption(f"{len(cases)} ca trong mẫu · YAML {engine.rules_version}")
    st.sidebar.caption("Chỉ engine của mẫu đã chọn được chạy. Dùng bệnh án giả định để thử.")

    input_tab, layers_tab, catalog_tab = st.tabs([
        "Bệnh án & kết quả", "Logic suy luận", "Bảng quy tắc & Mức ưu tiên",
    ])
    try:
        current_patient = parse_patient(st.session_state["patient_json"])
    except (ValueError, RecursionError):
        current_patient = None
    input_changed = current_patient != selected_case["du_lieu"]

    with input_tab:
        st.write(selected_case["mo_ta"])
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
                    st.session_state["result"] = classify_form(form_type, patient, engines)
                except (TypeError, ValueError, OverflowError, RecursionError) as exc:
                    st.session_state["run_error"] = (
                        f"Engine không hoàn tất ({type(exc).__name__}). Kiểm tra kiểu dữ liệu; "
                        "không có kết luận bệnh."
                    )
        result = st.session_state["result"]
        highlights = evidence_highlights(result, rules) if result else {}
        st.caption("Xanh: khớp điều kiện · Vàng: cần bổ sung · Đỏ: cần rà soát.")
        left, right = st.columns([1.4, 1], gap="large")
        with left:
            st.subheader("Dữ liệu bệnh án")
            preview, editor = st.columns(2)
            with preview:
                st.caption(f"Phiếu khám: {case_id}")
                if current_patient is None:
                    st.warning("Không thể hiển thị bệnh án: JSON chưa hợp lệ. Sửa dữ liệu ở ô JSON.")
                else:
                    try:
                        st.html(patient_html(current_patient, highlights))
                    except RecursionError:
                        st.warning("Không thể hiển thị bệnh án: cấu trúc JSON lồng quá nhiều tầng.")
            with editor:
                st.text_area("Mã JSON bệnh án", height=380, key="patient_json", on_change=clear_result)
                st.caption("Trường thiếu không được tự bổ sung. Sửa JSON rồi chạy phân loại lại.")
            if selected_case["expected_engine"]:
                with st.expander("Kỳ vọng của ca gốc — để đối chiếu sau suy diễn"):
                    if input_changed:
                        st.warning("JSON hiện tại đã khác ca gốc: kỳ vọng bên dưới không tự cập nhật.")
                    st.json(selected_case["expected_engine"])
                    st.caption("Kỳ vọng mô tả hành vi hiện tại, không phải nhãn chuẩn lâm sàng; không truyền vào engine.")

        with right:
            st.subheader("Kết quả chẩn đoán của hệ thống")
            if st.session_state["run_error"]:
                st.error(st.session_state["run_error"])
            elif result is None:
                st.info("Bấm Phân loại và giải thích để xem kết quả cho JSON hiện tại.")
            else:
                title = "Theo dõi phản vệ" if result["status"] == "THEODOIPV" else (result["predicted_label"] or "Chưa kết luận bệnh")
                st.subheader("KẾT LUẬN: " + title.upper())
                st.markdown(f"**Trạng thái:** {STATUS_LABELS[result['status']]}")
                st.caption(f"Mức ưu tiên: {result['priority']}")
                explanation = f"**{STATUS_LABELS[result['status']]}** — {STATUS_HELP[result['status']]}"
                if result["status"] == "NEEDS_REVIEW":
                    st.error(explanation)
                elif result["status"] in {"INSUFFICIENT_DATA", "UNRESOLVED", "THEODOIPV"}:
                    st.warning(explanation)
                if not result["missing_fields"]:
                    st.write(result["decision_trace"])
                if result["missing_fields"]:
                    st.write("**Trường cần bổ sung:**")
                    field_labels = clinical_field_labels()
                    for raw_field in result["missing_fields"]:
                        field = str(raw_field)
                        st.write("• " + " › ".join(field_labels.get(part, part) for part in field.split(".")))
                with st.expander("Kết quả và trace đầy đủ"):
                    st.write("**Rule được chọn:**", result["matched_rule_id"] or "Không có")
                    st.write("**Rule cùng khớp:**", ", ".join(result["matched_rule_ids"]) or "Không có")
                    st.write("**Rule chặn / xung đột:**", ", ".join(result["blocking_rule_ids"]) or "Không có")
                    st.caption(f"YAML {result['rules_version']} · SHA-256 {result['rules_sha256']}")
                    st.json(result)
                st.markdown("#### Bảng các quy tắc được đối chiếu ca này")
                active_rules_rows = []
                for rule_id, rule in rules.items():
                    value = result["rule_results"][rule_id]
                    if value is True or rule_id in result["blocking_rule_ids"]:
                        active_rules_rows.append({
                            "Mã Rule": rule_id, "Nội dung": rule["name"],
                            "Đánh giá": "UNKNOWN" if value is None else "TRUE" if value else "FALSE",
                            "Vai trò": "Kết luận chính" if rule_id == result["matched_rule_id"] else
                                       "Chặn / xung đột" if rule_id in result["blocking_rule_ids"] else "Khớp",
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
        if result:
            st.write("**Trạng thái:**", STATUS_LABELS[result["status"]])
            st.write("**Lý do:**", result["decision_trace"])
        st.subheader("Pha 1 · Đánh giá điều kiện và phụ thuộc")
        st.markdown(
            "**Mục tiêu của pha này là biết từng rule TRUE, FALSE hay UNKNOWN; chưa chọn nhãn bệnh.**\n\n"
            "Ví dụ trong mẫu phản vệ, `R-SOC` cần kết quả `R01-PV`, `R02-PV` hoặc `R03-PV`:\n\n"
            "1. Khi gặp một rule được tham chiếu nhưng chưa tính, engine tính rule đó trước.\n"
            "2. Kết quả được lưu vào **cache — bảng nhớ tạm**, chẳng hạn `R02-PV = TRUE`.\n"
            "3. `R-SOC` lấy kết quả đã lưu, kết hợp điều kiện huyết áp để đánh giá sốc. "
            "Rule khác cần `R02-PV` cũng dùng lại kết quả, không tính lại trong lần chạy đó.\n"
            "4. Engine tiếp tục tính các rule còn lại trong mẫu đã chọn; "
            "không dừng ngay khi một rule khớp."
        )
        st.info(
            "Mỗi lần phân loại có một bảng nhớ mới. Kết quả bệnh án A không dùng cho bệnh án B; "
            "sửa JSON rồi chạy lại cũng tính lại từ dữ liệu mới. UNKNOWN được lưu nguyên là UNKNOWN, không đổi thành FALSE."
        )
        st.subheader("Pha 2 · Chọn kết luận theo ưu tiên")
        st.write(
            "Sau khi đã có kết quả toàn bộ rule, engine mới chọn kết luận. Ưu tiên số nhỏ hơn được xét trước: "
            "nếu cả sốc và phản vệ đều TRUE, chọn sốc làm nhãn chính. UNKNOWN có thể đổi kết luận ở ưu tiên cao "
            "sẽ chặn việc chọn bệnh ở tầng thấp; các nhãn khác nhau cùng ưu tiên cần rà soát. "
            "Thứ tự tính phụ thuộc ở pha 1 khác thứ tự chọn nhãn ở pha 2."
        )
        st.caption("TRUE = đủ bằng chứng đúng · FALSE = đủ bằng chứng sai · UNKNOWN = chưa đánh giá được. Không coi UNKNOWN là FALSE.")
        for title, identifiers in LAYERS:
            identifiers = [identifier for identifier in identifiers if identifier in rules]
            if not identifiers:
                continue
            with st.expander(title, expanded=True):
                for identifier in identifiers:
                    rule = rules[identifier]
                    value = result["rule_results"][identifier] if result else None
                    state = "Chưa chạy" if result is None else "UNKNOWN" if value is None else "TRUE" if value else "FALSE"
                    marker = ""
                    if result and identifier == result["matched_rule_id"]:
                        marker = " · KẾT LUẬN CHÍNH"
                    elif result and identifier in result["blocking_rule_ids"]:
                        marker = " · CHẶN / XUNG ĐỘT"
                    elif result and identifier in result["matched_rule_ids"]:
                        marker = " · KHỚP"
                    st.markdown(f"**{identifier} — {rule['name']}** · `{state}`{marker}")
                    st.caption("Điều kiện cơ sở" if rule.get("is_base_condition") else
                               f"Mức ưu tiên {rule['priority']} · {rule['target_label']}")
                    with st.expander(f"Điều kiện và bằng chứng · {identifier}"):
                        st.json(rule["conditions"])
                        if result:
                            events = [event for event in result["trace"] if event["rule_id"] == identifier]
                            st.dataframe([dict(event, result="UNKNOWN" if event["result"] is None else
                                              "TRUE" if event["result"] else "FALSE") for event in events],
                                         hide_index=True, width="stretch")
        st.caption("INVALID_DATA và OUT_OF_SCOPE cần validator/cohort trong pipeline; demo không tự suy ra hai trạng thái này.")

    with catalog_tab:
        st.subheader("Bảng quy tắc & Mức ưu tiên")
        st.table([{
            "Mã Rule": rule["rule_id"], "Nội dung": rule["name"],
            "Mức ưu tiên": str(rule.get("priority", "Điều kiện tiên quyết")),
            "Kết luận": rule.get("target_label", ""),
        } for rule in engine.rules])
        st.caption("Theo dõi phản vệ có trạng thái THEODOIPV; thiếu dữ kiện có trạng thái INSUFFICIENT_DATA.")
        for label in labels:
            associated = [rule for rule in targets if rule["target_label"] == label]
            with st.expander(label, expanded=label == selected_label):
                for rule in associated:
                    st.write(f"**{rule['rule_id']}** · Mức ưu tiên {rule['priority']} · "
                             f"{STATUS_LABELS[rule.get('target_status', 'CLASSIFIED')]}")
                    st.write(rule.get("decision_trace", ""))
                    st.json(rule["conditions"])

    with layers_tab, st.expander("Workflow & diagram"):
        st.subheader("Workflow đề xuất và phạm vi đang chạy")
        st.write("Demo chạy: chọn mẫu → JSON CANONICAL → engine của mẫu → giải thích. RAW validation, preprocessing, re-check, anonymization và đánh giá batch chưa được nối.")
        diagram_name = st.selectbox("Diagram Archify", ["Luồng phân tầng", "Cây CSU", "Quy trình chuẩn"])
        diagram_files = {
            "Luồng phân tầng": "rule-based-phan-tang.svg",
            "Cây CSU": "rule-based-cay-csu.svg",
            "Quy trình chuẩn": "rule-based-quy-trinh.svg",
        }
        path = ROOT / "docs/diagrams" / diagram_files[diagram_name]
        if path.exists():
            st.image(path.read_text(encoding="utf-8"), width="stretch")
        else:
            st.warning("Không tìm thấy SVG. Xem docs/02_workflow.md để đối chiếu workflow.")
        st.caption("Bản SVG Archify hiện có mô tả workflow; tab Logic suy luận hiển thị kết quả YAML thực tế của ca đang chạy.")


if __name__ == "__main__":
    render()
