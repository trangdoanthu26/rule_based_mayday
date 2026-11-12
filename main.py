import csv
import hashlib
import io
import json
import math
import re
from html import escape
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st

from src.pipeline import classify_form, load_engines
from src.patient_input import empty_patient, engine_fields, get_value, is_raw, map_raw, merge_form, raw_patients


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


def render_engine_entry(form_type: str, engine: Any) -> None:
    st.subheader("Nhập bệnh án theo mẫu engine")
    st.caption("Điền trực tiếp hoặc bổ sung sau khi tải file. Để trống nếu chưa biết; chọn nhiều mục khi đã ghi nhận triệu chứng.")
    try:
        patient = parse_patient(st.session_state["patient_json"])
    except (ValueError, RecursionError):
        patient = {}
        st.info("JSON hiện tại chưa hợp lệ. Có thể tạo lại bệnh án bằng các ô bên dưới.")
    signature = (form_type, st.session_state["source_mode"], st.session_state["patient_json"])
    if st.session_state.get("entry_signature") != signature:
        for key in list(st.session_state):
            if key.startswith(("entry_value::", "entry_known::")):
                del st.session_state[key]
        st.session_state["entry_signature"] = signature
    labels = clinical_field_labels()
    fields = engine_fields(form_type, engine)
    values = {}
    with st.form(f"engine_entry_{form_type}"):
        columns = st.columns(2)
        for index, field in enumerate(fields):
            path = field["path"]
            value = get_value(patient, path)
            label = " › ".join(labels.get(part, part) for part in path.split("."))
            key = f"entry_value::{form_type}:{path}"
            with columns[index % 2]:
                if field["kind"] == "number":
                    try:
                        valid = type(value) in (int, float) and math.isfinite(value) and value >= field["minimum"]
                    except OverflowError:
                        valid = False
                    if field["integer"]:
                        value = int(value) if valid and float(value).is_integer() and value <= 2 ** 53 - 1 else None
                        minimum, step = int(field["minimum"]), 1
                    else:
                        value = float(value) if valid else None
                        minimum, step = float(field["minimum"]), 0.1
                    values[path] = st.number_input(label, min_value=minimum, value=value, step=step,
                                                  key=key, help=path, placeholder="Chưa có dữ liệu")
                elif field["kind"] == "array":
                    previous = value if isinstance(value, list) else []
                    if field["item_field"]:
                        previous = [row.get(field["item_field"]) for row in previous if isinstance(row, dict)]
                    previous = [item for item in previous if isinstance(item, str)]
                    choices = list(dict.fromkeys(field["choices"] + previous))
                    selected = st.multiselect(label, choices, default=previous, key=key, help=path)
                    known = st.checkbox("Đã đánh giá mục này (kể cả khi không chọn)", value=isinstance(value, list),
                                        key=f"entry_known::{form_type}:{path}", help=label)
                    values[path] = selected if selected or known else None
                else:
                    choices = [True, False] if field["kind"] == "boolean" else field["choices"]
                    if value not in choices or type(value) not in (str, bool):
                        value = None
                    options = [None] + choices
                    values[path] = st.selectbox(
                        label, options, index=options.index(value), key=key, help=path,
                        format_func=lambda item: "Chưa có dữ liệu" if item is None else
                                                "Có" if item is True else "Không" if item is False else item,
                    )
        submitted = st.form_submit_button("Áp dụng vào bệnh án", key="apply_engine_form", type="primary")
    if submitted:
        st.session_state["patient_json"] = json.dumps(merge_form(patient, fields, values), ensure_ascii=False, indent=2)
        clear_result()
        st.rerun()
    st.download_button("Tải bệnh án JSON theo mẫu", json.dumps({"form_type": form_type, "du_lieu": patient},
                       ensure_ascii=False, indent=2), file_name=f"benh_an_{form_type}.json", mime="application/json")
    st.caption("Bấm Áp dụng để cập nhật ô JSON và bản tải xuống; sau đó chạy phân loại tại tab Bệnh án & kết quả.")


def render_raw_mapping(raw: Dict[str, Any], form_type: str, engine: Any, upload_id: str, filename: str) -> None:
    patients = raw_patients(raw)
    if st.session_state.get("raw_patient") not in patients:
        st.session_state["raw_patient"] = patients[0]
    patient = st.sidebar.selectbox("Bệnh nhân trong RAW", patients, key="raw_patient",
                                   format_func=lambda value: f"Bệnh nhân {patients.index(value) + 1}", on_change=clear_result)
    visits = [row for row in raw["hanh_chinh"] if row["MA_BN_AN_DANH"] == patient]
    if st.session_state.get("raw_visit") not in range(len(visits)):
        st.session_state["raw_visit"] = 0
    visit = st.sidebar.selectbox("Lượt khám trong RAW", list(range(len(visits))), key="raw_visit", on_change=clear_result,
                                format_func=lambda index: f"Lượt {index + 1} · {visits[index].get('IN_TIME', 'Chưa có thời điểm')}")
    context = (upload_id, patient, visit, form_type)
    if st.session_state.get("raw_context") != context:
        st.session_state["raw_ige_confirm"] = False
        st.session_state["raw_context"] = context
    has_ige = any(row.get("MA_BN_AN_DANH") == patient and row.get("TEST_INDEX_CODE") == "SHM0027"
                  for row in raw.get("xet_nghiem", []))
    confirm = st.sidebar.checkbox("Xác nhận mã SHM0027 là IgE toàn phần", key="raw_ige_confirm", on_change=clear_result) if has_ige else False
    signature = (context, confirm)
    if st.session_state.get("applied_raw") != signature:
        mapped = map_raw(raw, patient, visit, form_type, engine, confirm_ige=confirm)
        if len(patients) == 1 and re.fullmatch(r"benh_nhan_[1-9][0-9]*\.json", filename):
            mapped["du_lieu"]["ma_benh_nhan"] = Path(filename).stem
        st.session_state["patient_json"] = json.dumps(mapped["du_lieu"], ensure_ascii=False, indent=2)
        st.session_state["raw_mapping_report"] = mapped
        st.session_state["applied_raw"] = signature
        clear_result()


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
    with st.expander("Cách sử dụng web · Cách đọc kết quả", expanded=True):
        st.markdown(
            "1. Chọn mẫu bệnh án, nhập tại tab Nhập bệnh án hoặc tải file JSON/CSV; bấm **Phân loại và giải thích**.\n"
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
        "Chọn nguồn bệnh án", ["Ca giả định mẫu", "Tải file mới (.json, .csv)", "Nhập theo mẫu engine"],
        key="source_mode", on_change=clear_result,
    )
    if data_source_mode == "Ca giả định mẫu":
        st.warning("Dữ liệu giả định · Các khác biệt CIndU/CSU vẫn cần rà soát. Xem lưu ý theo ca.")
    else:
        st.info("Bệnh án nhập ngoài · Dữ kiện chưa biết được giữ trống; bổ sung tại tab Nhập bệnh án.")
    if st.session_state.get("active_source") != data_source_mode:
        st.session_state["loaded_case"] = None
        st.session_state["loaded_upload"] = None
        st.session_state["patient_json"] = "{}"
        st.session_state["uploaded_raw"] = None
        st.session_state["raw_mapping_report"] = None
        st.session_state["applied_raw"] = None
        st.session_state["manual_form"] = None
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
                st.session_state["uploaded_raw"] = None
                st.session_state["raw_mapping_report"] = None
                st.session_state["applied_raw"] = None
                clear_result()
                try:
                    if uploaded_file.name.lower().endswith(".json"):
                        text = uploaded_file.getvalue().decode("utf-8-sig")
                        decoded = json.loads(text, parse_constant=reject_constant)
                        if is_raw(decoded):
                            raw_patients(decoded)
                            st.session_state["uploaded_raw"] = decoded
                            patient_data = {}
                        else:
                            patient_data = parse_patient(text)
                    else:
                        patient_data = parse_patient(json.dumps(
                            parse_csv_patient(uploaded_file.getvalue()), allow_nan=False,
                        ))
                    st.session_state["patient_json"] = json.dumps(patient_data, ensure_ascii=False, indent=2)
                    st.sidebar.success(f"Đã nạp file: {case_id}")
                except (ValueError, UnicodeError, RecursionError, csv.Error) as exc:
                    st.sidebar.error(f"Không đọc được bệnh án ({type(exc).__name__}). Kiểm tra JSON/CSV.")
            if st.session_state.get("uploaded_raw") is not None:
                try:
                    render_raw_mapping(st.session_state["uploaded_raw"], form_type, engine,
                                       hashlib.sha256(uploaded_file.getvalue()).hexdigest(), uploaded_file.name)
                except ValueError:
                    st.session_state["patient_json"] = ""
                    st.sidebar.error("Không xác định được bệnh nhân/lượt khám trong RAW. Kiểm tra mã liên kết và các bảng dữ liệu.")
                    clear_result()
        elif st.session_state.get("loaded_upload") is not None:
            st.session_state["loaded_upload"] = None
            st.session_state["patient_json"] = "{}"
            st.session_state["uploaded_raw"] = None
            st.session_state["raw_mapping_report"] = None
            st.session_state["applied_raw"] = None
            clear_result()
    elif data_source_mode == "Nhập theo mẫu engine":
        case_id = {"phan_ve": "Phản vệ", "cap": "Mày đay cấp", "man": "Mày đay mạn"}[form_type]
        selected_case = {"mo_ta": f"Bệnh án nhập trực tiếp · {case_id}", "du_lieu": {},
                         "workflow_gap": None, "expected_engine": {}}
        if st.session_state.get("manual_form") != form_type:
            st.session_state["patient_json"] = json.dumps(empty_patient(form_type, engine), ensure_ascii=False, indent=2)
            st.session_state["manual_form"] = form_type
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
    st.sidebar.caption("Chỉ engine của mẫu đã chọn được chạy.")

    input_tab, layers_tab, catalog_tab, entry_tab = st.tabs([
        "Bệnh án & kết quả", "Logic suy luận", "Bảng quy tắc & Mức ưu tiên", "Nhập bệnh án",
    ])
    with entry_tab:
        render_engine_entry(form_type, engine)
    try:
        current_patient = parse_patient(st.session_state["patient_json"])
    except (ValueError, RecursionError):
        current_patient = None
    input_changed = current_patient != selected_case["du_lieu"]

    with input_tab:
        st.write(selected_case["mo_ta"])
        report = st.session_state.get("raw_mapping_report")
        if report:
            st.info("RAW đã được mapping sang trường engine theo bệnh nhân/lượt khám đã chọn. Bổ sung dữ kiện còn thiếu tại tab Nhập bệnh án.")
            with st.expander("Nguồn dữ liệu và kết quả mapping RAW"):
                if report["provenance"]:
                    st.table(report["provenance"])
                if report["candidates"]:
                    st.write("Xét nghiệm IgE cần đối chiếu:")
                    st.dataframe(report["candidates"], hide_index=True)
                for warning in report["warnings"]:
                    st.write("• " + warning)
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
