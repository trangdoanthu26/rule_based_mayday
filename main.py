"""Streamlit demo of the existing engine, not the unimplemented RAW pipeline."""

import json
import re
from html import escape
from pathlib import Path
from typing import Any, Dict, Optional

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
    "CLASSIFIED": "Hệ thống đã xác định nhóm phân loại từ dữ liệu đã nhập.",
    "INSUFFICIENT_DATA": "Thiếu dữ kiện hoặc chưa đủ thời gian; xem rule chặn và trường cần bổ sung.",
    "NEEDS_REVIEW": "Chưa có kết luận bệnh: có xung đột hoặc dữ liệu cần rà soát; xem điều kiện và trace của các rule chặn.",
    "UNRESOLVED": "Không có rule đích phù hợp sau đánh giá hiện tại.",
}
STATUS_LABELS = {
    "CLASSIFIED": "ĐÃ PHÂN LOẠI",
    "INSUFFICIENT_DATA": "CHƯA ĐỦ DỮ KIỆN",
    "NEEDS_REVIEW": "CẦN RÀ SOÁT",
    "UNRESOLVED": "CHƯA XÁC ĐỊNH PHÂN LOẠI",
}
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
    st.set_page_config(page_title="Rule-based · Mề đay", page_icon="🔎", layout="wide")
    st.title("Hệ thốngRule-based mề đay")
    st.caption("Chọn bệnh án giả định, phân loại và đối chiếu dữ kiện với kết luận.")
    st.warning("Dữ liệu giả định · Còn lỗi F-01 (cấp thường), F-12 (huyết áp). Xem lưu ý theo ca.")
    with st.expander("Cách đọc kết quả và check logic"):
        st.markdown(
            "1. Chọn đầu ra và ca giả định; bấm **Phân loại và giải thích**.\n"
            "2. Xem trạng thái, rule được chọn và rule chặn; mở **6 tầng phân loại** để đối chiếu điều kiện.\n"
            "3. Sửa một biến mỗi lần, thử trước/tại/sau ngưỡng hoặc xóa một trường rồi chạy lại.\n"
            "4. Kết quả kỳ vọng chỉ thuộc **ca gốc**; JSON đã sửa có thể có kết quả riêng. Ghi ca sai lệch (lưu **JSON đã sửa + kết quả mong đợi + kết quả thực tế**) để re-check."
        )
        st.table([{"Trạng thái": STATUS_LABELS[status], "Ý nghĩa": explanation}
                  for status, explanation in STATUS_HELP.items()])
        st.caption("TRUE/FALSE/UNKNOWN là trạng thái điều kiện, không phải nhãn bệnh. Ưu tiên số nhỏ hơn được xét trước.")
        st.caption("INVALID_DATA / OUT_OF_SCOPE thuộc pipeline chưa triển khai; JSON sai hiện được demo báo lỗi nhập.")
        st.caption("Hướng dẫn và nhật ký thay đổi: docs/05_changelog.md. Phân tích đầy đủ: docs/06_rule_logic_review.md.")
    try:
        engine = ClinicalRuleEngine(str(ROOT / "rules/classification_rules.yaml"))
        fixture = json.loads((ROOT / "data/synthetic/rule_logic_cases.json").read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        st.error(f"Không nạp được cấu hình demo ({type(exc).__name__}). Kiểm tra YAML và bộ ca giả định.")
        return

    rules = {rule["rule_id"]: rule for rule in engine.rules}
    targets = [rule for rule in engine.rules if "target_label" in rule]
    labels = list(dict.fromkeys(rule["target_label"] for rule in targets))
    st.sidebar.header("Chọn nội dung minh họa")
    selected_label = st.sidebar.selectbox(
        "Đầu ra cần minh họa", ["Tất cả"] + labels, key="output_label", on_change=clear_result,
    )
    selected_rules = {rule["rule_id"] for rule in targets if rule["target_label"] == selected_label}
    cases = [case for case in fixture["cases"] if selected_label == "Tất cả"
             or case["expected_engine"].get("matched_rule_id") in selected_rules
             or selected_rules.intersection(case["expected_engine"].get("rule_results", {}))]
    if not cases:
        st.warning("Chưa có ca minh họa cho đầu ra này trong bộ dữ liệu hiện tại.")
        return
    by_id = {case["id"]: case for case in cases}
    if st.session_state.get("case_id") not in by_id:
        st.session_state["case_id"] = cases[0]["id"]
    case_id = st.sidebar.selectbox(
        "Bệnh án giả định", list(by_id), key="case_id", on_change=clear_result,
        format_func=lambda identifier: f"{identifier} · {by_id[identifier]['mo_ta']}",
    )
    selected_case = by_id[case_id]
    if st.session_state.get("loaded_case") != case_id:
        st.session_state["patient_json"] = json.dumps(selected_case["du_lieu"], ensure_ascii=False, indent=2)
        st.session_state["loaded_case"] = case_id
        clear_result()
    st.session_state.setdefault("result", None)
    st.session_state.setdefault("run_error", None)
    st.sidebar.caption(f"{len(fixture['cases'])} ca · YAML {engine.rules_version}")
    st.sidebar.caption("Chỉ sử dụng bệnh án giả định trong demo này.")

    input_tab, editor_tab, layers_tab, catalog_tab, diagrams_tab = st.tabs([
        "Bệnh án & kết quả", "Chỉnh sửa dữ liệu (tùy chọn)", "6 tầng phân loại",
        "14 mặt bệnh & điều kiện", "Workflow & diagram",
    ])
    with editor_tab:
        st.subheader("Chỉnh sửa JSON bệnh án")
        st.text_area("JSON bệnh án · có thể sửa để thử ca biên", height=380,
                     key="patient_json", on_change=clear_result)
        st.caption("Sửa JSON rồi nhấn Ctrl+Enter/⌘+Enter hoặc bấm ra ngoài để cập nhật. "
                   "Quay về tab Bệnh án & kết quả và chạy phân loại lại.")
    try:
        current_patient = parse_patient(st.session_state["patient_json"])
    except (ValueError, RecursionError):
        current_patient = None
    input_changed = current_patient != selected_case["du_lieu"]
    with editor_tab:
        with st.expander("Kỳ vọng của ca gốc — để đối chiếu sau suy diễn"):
            if input_changed:
                st.warning("JSON hiện tại đã khác ca gốc: kỳ vọng bên dưới không tự cập nhật; hãy xác định kỳ vọng cho biến thể mới.")
            st.json(selected_case["expected_engine"])
            st.caption("Kỳ vọng mô tả hành vi hiện tại, không phải nhãn chuẩn lâm sàng; không truyền vào engine.")

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
                    st.session_state["result"] = engine.classify_patient(patient)
                except (TypeError, ValueError, OverflowError, RecursionError) as exc:
                    # F-12 remains in the engine; the demo must show the failure, not invent a label.
                    st.session_state["run_error"] = (
                        f"Engine không hoàn tất ({type(exc).__name__}). Kiểm tra kiểu dữ liệu; "
                        "lỗi công thức HATT F-12 đã được ghi nhận. Không có kết luận bệnh."
                    )
        result = st.session_state["result"]
        highlights = evidence_highlights(result, rules) if result else {}
        st.caption("Xanh: khớp điều kiện · Vàng: cần bổ sung · Đỏ: cần rà soát. "
                   "Các dữ kiện được đánh dấu được đưa lên trước để dễ đối chiếu.")
        left, right = st.columns([1.1, 1], gap="large")
        with left, st.container(height=500, border=True):
            st.subheader("Bệnh án đang kiểm tra")
            st.caption("Bản đọc của JSON hiện tại. Trường không có trong JSON không được tự bổ sung.")
            if current_patient is None:
                st.warning("Không thể hiển thị bệnh án: JSON chưa hợp lệ. Mở tab “Chỉnh sửa dữ liệu” để sửa dữ liệu.")
            else:
                try:
                    st.html(patient_html(current_patient, highlights))
                except RecursionError:
                    st.warning("Không thể hiển thị bệnh án: cấu trúc JSON lồng quá nhiều tầng.")

        with right, st.container(height=500, border=True):
            st.subheader("Kết quả hệ thống")
            if st.session_state["run_error"]:
                st.error(st.session_state["run_error"])
            elif result is None:
                st.info("Bấm Phân loại và giải thích để xem kết quả cho JSON hiện tại.")
            else:
                st.subheader("KẾT LUẬN: " + (result["predicted_label"] or "Chưa kết luận bệnh").upper())
                st.markdown(f"**Trạng thái:** {STATUS_LABELS[result['status']]}")
                st.caption(f"Mức ưu tiên: {result['priority']}")
                explanation = f"**{STATUS_LABELS[result['status']]}** — {STATUS_HELP[result['status']]}"
                if result["status"] == "NEEDS_REVIEW":
                    st.error(explanation)
                elif result["status"] in {"INSUFFICIENT_DATA", "UNRESOLVED"}:
                    st.warning(explanation)
                if current_patient and isinstance(current_patient.get("huyet_ap_tam_thu_thap_nhat"), bool):
                    st.error("**F-12 · HATT boolean: nhãn bên dưới không đáng tin cậy.** Engine có thể coi true/false là số khi tính công thức; cần sửa kiểu dữ liệu và chạy lại.")
                if not result["missing_fields"]:
                    st.write(result["decision_trace"])
                if result["missing_fields"]:
                    st.write("**Trường cần bổ sung:**")
                    field_labels = clinical_field_labels()
                    for field in result["missing_fields"]:
                        st.write("• " + " › ".join(field_labels.get(part, part) for part in field.split(".")))
                with st.expander("Kết quả và trace đầy đủ"):
                    st.write("**Rule được chọn:**", result["matched_rule_id"] or "Không có")
                    st.write("**Rule cùng khớp:**", ", ".join(result["matched_rule_ids"]) or "Không có")
                    st.write("**Rule chặn / xung đột:**", ", ".join(result["blocking_rule_ids"]) or "Không có")
                    st.caption(f"YAML {result['rules_version']} · SHA-256 {result['rules_sha256']}")
                    st.json(result)
                st.download_button("Tải kết quả JSON", json.dumps(result, ensure_ascii=False, indent=2),
                                   file_name="rule_result.json", mime="application/json")
            if selected_case["workflow_gap"]:
                issue_id = selected_case["workflow_gap"]
                st.warning(
                    f"**Ca gốc · {issue_id}** — {ISSUE_HELP[issue_id]} "
                    "Đây là chú thích của ca gốc; JSON đã sửa có thể có vấn đề khác."
                )

    with layers_tab:
        st.subheader("Pha 1 · Đánh giá điều kiện và phụ thuộc")
        st.markdown(
            "**Mục tiêu của pha này là biết từng rule TRUE, FALSE hay UNKNOWN; chưa chọn nhãn bệnh.**\n\n"
            "Ví dụ `R-SOC` (sốc phản vệ) cần kết quả `R02-PV` hoặc `R03-PV` (phản vệ):\n\n"
            "1. Khi gặp một rule được tham chiếu nhưng chưa tính, engine tính rule đó trước.\n"
            "2. Kết quả được lưu vào **cache — bảng nhớ tạm**, chẳng hạn `R02-PV = TRUE`.\n"
            "3. `R-SOC` lấy kết quả đã lưu, kết hợp điều kiện huyết áp để đánh giá sốc. "
            "Rule khác cần `R02-PV` cũng dùng lại kết quả, không tính lại trong lần chạy đó.\n"
            "4. Engine tiếp tục tính các rule còn lại: phản vệ, cấp, CIndU, CSU và theo dõi; "
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
        st.subheader("Mỗi output và các rule liên quan tới output đó")
        st.caption("Hai nhãn theo dõi có target_status INSUFFICIENT_DATA; predicted_label của kết quả không phải nhãn bệnh.")
        for label in labels:
            associated = [rule for rule in targets if rule["target_label"] == label]
            with st.expander(label, expanded=label == selected_label):
                for rule in associated:
                    st.write(f"**{rule['rule_id']}** · Mức ưu tiên {rule['priority']} · "
                             f"{STATUS_LABELS[rule.get('target_status', 'CLASSIFIED')]}")
                    st.write(rule.get("decision_trace", ""))
                    st.json(rule["conditions"])
                if label == "Mày đay cấp thông thường":
                    st.warning("F-01: chưa có ca JSON thỏa rule cấp thường; danh mục này mô tả rule đang có, không xác nhận nhánh đã hoạt động.")

    with diagrams_tab:
        st.subheader("Workflow đề xuất và phạm vi đang chạy")
        st.write("Demo chạy: JSON CANONICAL → engine → giải thích. RAW validation, preprocessing, re-check, anonymization và đánh giá batch chưa được nối.")
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
        st.caption("Bản SVG Archify hiện có mô tả workflow; tab Sáu tầng hiển thị kết quả YAML thực tế của ca đang chạy.")


if __name__ == "__main__":
    render()
