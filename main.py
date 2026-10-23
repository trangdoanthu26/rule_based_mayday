import csv
import io
import json
import re
from html import escape
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import streamlit as st

from src.pipeline import classify_form, load_engines


ROOT = Path(__file__).resolve().parent
FORM_NAMES = {
    "phan_ve": "Bệnh án Phản vệ (Sốc & Phản vệ)",
    "cap": "Mày đay cấp (< 6 tuần)",
    "man": "Mày đay mạn (CIndU & CSU)",
}
FORM_SHORT_NAMES = {
    "phan_ve": "Bệnh án Phản vệ",
    "cap": "Mày đay cấp",
    "man": "Mày đay mạn (CIndU & CSU)",
}
FORM_FULL_TITLES = {
    "phan_ve": "Bệnh án Phản vệ",
    "cap": "Mày đay cấp tính",
    "man": "Mày đay mạn tính (CIndU & CSU)",
}
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


def extract_engine_fields(engine: Any) -> Set[str]:
    """Trích xuất tập hợp các trường gốc (root fields) được sử dụng bởi các rule trong engine."""
    fields: Set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            field_name = node.get("field")
            if isinstance(field_name, str) and field_name.strip():
                fields.add(field_name.split(".")[0])
            formula = node.get("formula")
            if isinstance(formula, str):
                if "tuoi" in formula:
                    fields.add("tuoi")
                if "huyet_ap_tam_thu_nen" in formula:
                    fields.add("huyet_ap_tam_thu_nen")
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    for rule in engine.rules:
        walk(rule.get("conditions", {}))
    return fields


def filter_patient_by_engine(data: Dict[str, Any], engine: Any) -> Dict[str, Any]:
    """Lọc bản ghi bệnh án chỉ giữ lại các trường liên quan đến bộ quy tắc của engine hiện tại."""
    relevant_fields = extract_engine_fields(engine)
    return {k: v for k, v in data.items() if k in relevant_fields}


def resolve_condition_node(conditions: Dict[str, Any], path: str) -> Optional[Dict[str, Any]]:
    """Phân giải condition_path trong trace đến đúng node điều kiện trong cây conditions của file YAML."""
    if not path or not path.startswith("conditions"):
        return None
    sub = path[len("conditions"):]
    cur = conditions
    tokens = re.findall(r'\.([a-zA-Z0-9_]+)(?:\[(\d+)\])?', sub)
    for key, idx in tokens:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
            if idx:
                idx_int = int(idx)
                if isinstance(cur, list) and 0 <= idx_int < len(cur):
                    cur = cur[idx_int]
                else:
                    return None
        else:
            return None
    return cur if isinstance(cur, dict) else None


def get_nested_val(data: Any, path: str) -> Any:
    """Lấy an toàn giá trị từ dictionary lồng nhau theo dot-notation."""
    if not isinstance(data, dict) or not path:
        return None
    parts = path.split(".")
    cur = data
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur


def format_trace_events(events: list, labels: Dict[str, str], engine: Any = None, patient_data: Optional[Dict[str, Any]] = None) -> list:
    """Chuyển đổi các sự kiện trace kỹ thuật sang bảng đối chiếu lâm sàng cụ thể có số liệu thực tế."""
    op_map = {
        "==": "Yêu cầu bằng",
        "!=": "Yêu cầu khác",
        "<": "Nhỏ hơn",
        "<=": "Không quá",
        ">": "Lớn hơn",
        ">=": "Từ",
        "contains": "Có triệu chứng",
        "contains_any": "Có ít nhất một triệu chứng",
        "count_matching_systems_gte": "Tổn thương từ 2 hệ cơ quan",
        "<_formula": "Tụt huyết áp theo tuổi / HA nền",
    }
    rules_by_id = engine._rules_by_id if engine else {}
    rows = []
    
    patient_age = patient_data.get("tuoi") if patient_data else None

    for event in events:
        rule_id = event.get("rule_id", "")
        cond_path = event.get("condition_path", "")
        op = event.get("operator", "")
        field_path = event.get("field_path")
        res = event.get("result")
        
        rule_def = rules_by_id.get(rule_id, {})
        cond_node = resolve_condition_node(rule_def.get("conditions", {}), cond_path) if rule_def else None
        
        # Nếu đang kiểm tra R-SOC và đã có tuổi bệnh nhân: ẩn bớt các nhánh tuổi không thuộc nhóm của bệnh nhân
        if rule_id == "R-SOC" and patient_age is not None and cond_node and cond_node.get("field") == "tuoi":
            val = cond_node.get("value")
            if cond_node.get("operator") == "<" and val is not None and patient_age >= val:
                continue
            if cond_node.get("operator") == ">=" and val is not None:
                if val == 18 and patient_age < 18:
                    continue
                elif val == 11 and (patient_age < 11 or patient_age >= 18):
                    continue
                elif val == 1 and (patient_age < 1 or patient_age >= 11):
                    continue
                elif val == 0 and (patient_age < 0 or patient_age >= 1):
                    continue

        ref_id = cond_node.get("ref_rule") if cond_node else None

        if ref_id:
            ref_obj = rules_by_id.get(ref_id, {})
            ref_name = ref_obj.get("display_name") or ref_obj.get("name") or ref_id
            field_name = f"Tham chiếu quy tắc: {ref_name} ({ref_id})"
            op_text = f"Đạt quy tắc {ref_id}"
            actual_text = "Đạt quy tắc" if res is True else "Không thỏa mãn" if res is False else "Chưa có thông tin"
        elif field_path:
            field_name = " › ".join(labels.get(part, part) for part in field_path.split("."))
            actual_val = get_nested_val(patient_data, field_path) if patient_data else None
            
            if actual_val is None:
                actual_text = "Chưa cung cấp"
            elif isinstance(actual_val, bool):
                actual_text = "Có" if actual_val else "Không"
            elif isinstance(actual_val, list):
                actual_text = ", ".join(str(x) for x in actual_val) if actual_val else "Không có"
            else:
                actual_text = str(actual_val)
                
            expected_val = cond_node.get("value") if cond_node else None
            formula = cond_node.get("formula") if cond_node else None
            
            if formula == "70 + 2 * tuoi":
                calc_val = f"70 + 2*{patient_age} = {70 + 2*patient_age} mmHg" if isinstance(patient_age, (int, float)) else "70 + 2*tuổi"
                op_text = f"Tụt huyết áp: < {calc_val}"
            elif formula == "0.7 * huyet_ap_tam_thu_nen":
                ha_nen = patient_data.get("huyet_ap_tam_thu_nen") if patient_data else None
                calc_val = f"0.7 * {ha_nen} = {0.7*ha_nen:.0f} mmHg" if isinstance(ha_nen, (int, float)) else "Giảm > 30% HA nền"
                op_text = f"Tụt huyết áp: < {calc_val}"
            elif expected_val is not None:
                if op == "==":
                    op_text = f"Yêu cầu: {expected_val}"
                elif op == "!=":
                    op_text = f"Khác: {expected_val}"
                elif op in {">=", ">", "<=", "<"}:
                    op_text = f"{op_map.get(op, op)} {expected_val}"
                elif op in {"contains", "contains_any"}:
                    exp_str = ", ".join(expected_val) if isinstance(expected_val, list) else str(expected_val)
                    op_text = f"Có triệu chứng: {exp_str}"
                else:
                    op_text = f"{op} {expected_val}"
            else:
                op_text = op_map.get(op, op)
        elif op == "count_matching_systems_gte":
            field_name = "Tổn thương từ 2/4 hệ cơ quan (Da, Hô hấp, Tuần hoàn, Tiêu hóa)"
            op_text = "Yêu cầu ≥ 2 trong 4 hệ cơ quan"
            actual_text = "Đạt ≥ 2 hệ" if res is True else "Chưa đủ 2 hệ"
        else:
            field_name = "Điều kiện lâm sàng tổng hợp"
            op_text = op_map.get(op, op)
            actual_text = "Đạt" if res is True else "Không đạt"
            
        res_text = "ĐẠT" if res is True else "Không đạt" if res is False else "Chưa có thông tin"
        
        rows.append({
            "Dữ kiện kiểm tra": field_name,
            "Số liệu thực tế của ca bệnh": actual_text,
            "Tiêu chuẩn ngưỡng theo luật": op_text,
            "Đánh giá lâm sàng": res_text,
        })
    return rows


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
    ("T2 · Phản vệ và theo dõi", ("R01-PV-KHONG-DI-NGUYEN", "R02-PV-2/4-CO-QUAN", "R03-PV-DUONG-HIT", "R-PV-THEODOI", "R01-PV", "R02-PV", "R03-PV")),
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


def get_engine_layers(engine: Any) -> list:
    """Tự động trích xuất các tầng (layers) từ metadata của các rule trong file YAML.
    Đảm bảo khi thêm/sửa/xóa rule trong YAML, giao diện tự động cập nhật theo mà không cần sửa code."""
    layers_dict: Dict[str, list] = {}
    for rule in engine.rules:
        layer_name = rule.get("layer")
        if not layer_name:
            if rule.get("priority") == 1:
                layer_name = "T1 · Sốc phản vệ"
            elif rule.get("priority") == 2:
                layer_name = "T2 · Phản vệ và theo dõi"
            elif "CAP" in rule["rule_id"]:
                layer_name = "T3 · Mày đay cấp"
            elif "CindU" in rule["rule_id"]:
                layer_name = "T4 · Mày đay cảm ứng mạn tính — CIndU"
            elif "CSU" in rule["rule_id"] or "GD" in rule["rule_id"]:
                layer_name = "T5 · Mày đay tự phát mạn tính — CSU"
            else:
                layer_name = "T6 · Chưa đủ dữ kiện / ngoại lệ"
        layers_dict.setdefault(layer_name, []).append(rule["rule_id"])
    return list(layers_dict.items())


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
        '<style>'
        '.patient-sheet{padding:0.6rem 0.8rem;font-size:0.875rem;color:#1e293b;height:380px;max-height:380px;overflow-y:auto;border:1px solid #cbd5e1;border-radius:8px;background:#ffffff;box-sizing:border-box;scrollbar-width:thin}'
        '.patient-sheet::-webkit-scrollbar{width:6px}'
        '.patient-sheet::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:3px}'
        '.patient-sheet dl{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:.4rem .8rem;margin:.4rem 0}'
        '.patient-sheet dt{font-weight:600;color:#334155;overflow-wrap:anywhere}'
        '.patient-sheet dd{margin:0;color:#0f172a;overflow-wrap:anywhere}'
        '.patient-sheet ul{padding-left:1.1rem;margin:0}'
        '.patient-sheet dd dl{grid-template-columns:1fr;gap:.1rem}'
        '.patient-sheet>dl>dt,.patient-sheet>dl>dd{border-bottom:1px solid #e2e8f0;padding:.35rem 0}'
        '.patient-sheet [data-evidence="matched"]{background:#ecfdf5;border-left:3px solid #10b981;padding-left:4px}'
        '.patient-sheet [data-evidence="missing"]{background:#fffbeb;border-left:3px solid #f59e0b;padding-left:4px}'
        '.patient-sheet [data-evidence="review"]{background:#fef2f2;border-left:3px solid #ef4444;padding-left:4px}'
        '.patient-sheet small{display:block;font-size:.7rem;font-weight:normal;color:#64748b}'
        '.patient-sheet p[data-evidence="missing"]{background:#fffbeb;border:1px dashed #f59e0b;padding:.4rem .6rem;border-radius:6px;margin:.3rem 0;font-size:0.8rem}'
        '@media(max-width:600px){.patient-sheet dl{grid-template-columns:1fr;gap:.2rem}}'
        '</style>' + missing + content + '</section>'
    )


def check_cross_form_mismatch(form_type: str, patient: Dict[str, Any]) -> Optional[str]:
    """Cảnh báo nhẹ nhàng nếu người dùng tải nhầm hồ sơ của phân hệ khác."""
    chronic_keys = {"asst_ket_qua", "stella_dat", "igg_khang_fceria_ket_qua", "da_ve_noi_ket_qua"}
    anaphylaxis_keys = {"trieu_chung_da_hien_tai_pv", "tac_nhan_hit_vao_pv", "yeu_to_nghi_ngo_pv_thuc_an"}
    acute_keys = {"dac_diem_san_phu_cap", "thoi_gian_khoi_phat_gio"}

    keys = set(patient.keys())
    if form_type == "phan_ve" and keys.intersection(chronic_keys):
        return "Hồ sơ vừa nạp có các chỉ số của Mày đay mạn tính. Nếu đây là ca mạn, hãy chuyển sang màn Mày đay mạn."
    if form_type == "man" and keys.intersection(anaphylaxis_keys) and not keys.intersection(chronic_keys):
        return "Hồ sơ vừa nạp có các dấu hiệu cấp cứu phản vệ. Hãy kiểm tra nếu cần chuyển sang màn Phản vệ."
    if form_type == "cap" and keys.intersection(chronic_keys):
        return "Hồ sơ vừa nạp có các chỉ số của Mày đay mạn tính. Hãy kiểm tra nếu cần chuyển sang màn Mày đay mạn."
    return None


def generate_dynamic_reasoning_steps(form_type: str, engine: Any, result: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Tạo các bước suy luận động cho bác sĩ dựa trên kết quả trace và rule_results thực tế."""
    if not result:
        if form_type == "phan_ve":
            return [
                {
                    "num": 1,
                    "title": "Kiểm tra Sốc phản vệ",
                    "prio": "Ưu tiên 1",
                    "desc": "Công thức: Sốc phản vệ = Đạt tiêu chí phản vệ VÀ Tụt huyết áp theo tuổi. Bệnh nhân có biểu hiện phản vệ kèm tụt huyết áp nghiêm trọng sẽ được kết luận SỐC PHẢN VỆ ngay lập tức.",
                },
                {
                    "num": 2,
                    "title": "Phản vệ thường",
                    "prio": "Ưu tiên 2",
                    "desc": "Kiểm tra các kịch bản phản vệ: Không rõ dị nguyên, Dị nguyên nghi ngờ (tổn thương >= 2/4 hệ), hoặc Dị nguyên đã biết. Nếu huyết áp bình thường chưa tụt thì kết luận PHẢN VỆ.",
                },
                {
                    "num": 3,
                    "title": "Theo dõi phản vệ",
                    "prio": "Ưu tiên 3",
                    "desc": "Tự động kích hoạt khi có yếu tố nghi ngờ nhưng không đủ tiêu chí xác định Sốc phản vệ hoặc Phản vệ (chuyển diện theo dõi sát).",
                },
            ]
        elif form_type == "cap":
            return [
                {
                    "num": 0,
                    "title": "Sàng lọc tiên quyết (R-SANGLOC-CAP)",
                    "prio": "Tiên quyết",
                    "desc": "Kiểm tra hiện tại có sẩn phù bờ rõ (tròn/vòng/bản đồ) + có ảnh chụp sẩn phù + thời gian khởi phát <= 1008 giờ (6 tuần).",
                },
                {
                    "num": 1,
                    "title": "Kiểm tra Dấu hiệu nặng",
                    "prio": "Ưu tiên cấp nặng",
                    "desc": "Kiểm tra ngứa nhiều (R01), phù mạch nguy hiểm hoặc từng nhập viện (R02), hoặc triệu chứng tiêu hóa/hô hấp/lan rộng (R03) -> Kết luận Mày đay cấp có dấu hiệu nặng.",
                },
                {
                    "num": 2,
                    "title": "Mày đay cấp thông thường",
                    "prio": "Ưu tiên cấp thường",
                    "desc": "Có sẩn phù VÀ phủ định toàn bộ các tiêu chí nặng ở Bước 1 -> Kết luận Mày đay cấp thông thường.",
                },
            ]
        elif form_type == "man":
            return [
                {
                    "num": 1,
                    "title": "Điều kiện tiên quyết Mày đay mạn (CIndU / CSU)",
                    "prio": "Tiên quyết",
                    "desc": "Kiểm tra thời gian bệnh kéo dài > 6 tuần và bối cảnh xuất hiện triệu chứng (khi có yếu tố kích thích cơ học/nhiệt độ hay xuất hiện tự phát ngẫu nhiên).",
                },
                {
                    "num": 2,
                    "title": "Khảo sát Mày đay cảm ứng (CIndU)",
                    "prio": "Nhóm CIndU",
                    "desc": "Đánh giá các nghiệm pháp kích thích thực nghiệm: Da vẽ nổi (FricTest), Cholinergic (vận động/nóng), Test cục đá do lạnh, Áp lực chậm, Ánh sáng, Nước...",
                },
                {
                    "num": 3,
                    "title": "Khảo sát Mày đay tự phát CSU & Tự kháng thể",
                    "prio": "Nhóm CSU",
                    "desc": "Phân nhánh xét nghiệm huyết thanh ASST: (+) vào GĐ1 hoặc (-) đạt chuẩn Stella vào GĐ2. Định lượng tự kháng thể ELISA (IgG, IgE anti-IL24) để xác định Type I, Type IIb, Overlap hoặc Unknown.",
                },
                {
                    "num": 4,
                    "title": "Chưa đủ dữ liệu / Tiếp tục theo dõi",
                    "prio": "Ngoại lệ",
                    "desc": "Hồ sơ thiếu kết quả bắt buộc (ASST trống, chưa theo dõi đủ 60 ngày hoặc thiếu ELISA) sẽ chuyển diện Chưa phân loại (Tiếp tục theo dõi).",
                },
            ]
        return []

    rules_by_id = engine._rules_by_id
    rule_results = result.get("rule_results", {})
    matched_id = result.get("matched_rule_id")
    status = result.get("status")
    decision_trace = result.get("decision_trace", "")

    steps: List[Dict[str, Any]] = []

    if form_type == "phan_ve":
        # Tìm tất cả rule phản vệ thường (priority == 2 hoặc target_label == "Phản vệ")
        pv_rules = [r["rule_id"] for r in engine.rules if r.get("priority") == 2 or r.get("target_label") == "Phản vệ"]
        r_soc = rule_results.get("R-SOC")
        pv_sub_trues = [r for r in pv_rules if rule_results.get(r) is True]

        # Bước 1: Kiểm tra Sốc phản vệ (Ưu tiên 1)
        if r_soc is True:
            sub_id = pv_sub_trues[0] if pv_sub_trues else ""
            sub_name = rules_by_id.get(sub_id, {}).get("display_name") or sub_id
            desc_1 = (
                f"Bệnh nhân có biểu hiện phản vệ ({sub_name}) VÀ tụt huyết áp nghiêm trọng theo độ tuổi "
                f"-> **KẾT LUẬN: SỐC PHẢN VỆ** (Mức ưu tiên 1)."
            )
        elif r_soc is False:
            if pv_sub_trues:
                desc_1 = (
                    "Huyết áp trong giới hạn bình thường (không bị tụt theo độ tuổi) "
                    "-> Loại trừ Sốc phản vệ, chuyển tiếp sang Bước 2."
                )
            else:
                desc_1 = (
                    "Không có tụt huyết áp theo tuổi và chưa đạt tiêu chí phản vệ "
                    "-> Loại trừ Sốc phản vệ, chuyển tiếp sang Bước 2."
                )
        else:
            desc_1 = "Chưa đủ dữ liệu huyết áp hoặc lâm sàng để xác định Sốc phản vệ."

        steps.append({
            "num": 1,
            "title": "Kiểm tra Sốc phản vệ",
            "prio": "Ưu tiên 1",
            "desc": desc_1,
        })

        # Bước 2: Phản vệ thường (Ưu tiên 2)
        if matched_id == "R-SOC":
            desc_2 = "Bệnh nhân đạt tiêu chuẩn phản vệ, nhưng ưu tiên chẩn đoán Sốc phản vệ ở Bước 1 do có kèm tụt huyết áp."
        elif matched_id in pv_rules:
            r_obj = rules_by_id.get(matched_id, {})
            r_name = r_obj.get("display_name") or r_obj.get("name") or matched_id
            crit = r_obj.get("criteria_text") or r_obj.get("decision_trace") or ""
            desc_2 = f"Thỏa mãn tiêu chuẩn **{r_name}**: {crit} (huyết áp không tụt) -> **KẾT LUẬN: PHẢN VỆ**."
        elif any(rule_results.get(r) is True for r in pv_rules):
            true_pvs = [r for r in pv_rules if rule_results.get(r) is True]
            desc_2 = f"Thỏa mãn tiêu chuẩn phản vệ ({', '.join(true_pvs)}), nhưng bị ảnh hưởng bởi trạng thái chẩn đoán chung ({status})."
        elif matched_id == "R-PV-THEODOI" or status == "THEODOIPV":
            desc_2 = "Không thỏa mãn các kịch bản phản vệ (chưa đủ 2 hệ cơ quan hoặc không có biểu hiện da cấp tính kết hợp suy hô hấp/tuần hoàn)."
        else:
            desc_2 = "Chưa đủ dữ kiện để khẳng định phản vệ."

        steps.append({
            "num": 2,
            "title": "Phản vệ thường",
            "prio": "Ưu tiên 2",
            "desc": desc_2,
        })

        # Bước 3: Theo dõi phản vệ (Ưu tiên 3)
        if status == "THEODOIPV" or matched_id == "R-PV-THEODOI":
            desc_3 = "Bệnh nhân có yếu tố nghi ngờ nhưng không đủ tiêu chuẩn xác định Sốc phản vệ hoặc Phản vệ -> **KẾT LUẬN: TIẾP TỤC THEO DÕI SÁT PHẢN VỆ**."
        elif matched_id == "R-SOC" or matched_id in pv_rules:
            pred = result.get("predicted_label", "Phản vệ")
            desc_3 = f"Đã xác định rõ chẩn đoán **{pred}** ở mức ưu tiên cao hơn, không cần chuyển diện theo dõi."
        elif status == "INSUFFICIENT_DATA":
            desc_3 = "Bệnh án thiếu các trường thông tin bắt buộc để đưa ra kết luận."
        elif status == "NEEDS_REVIEW":
            desc_3 = "Có mâu thuẫn hoặc kiểu dữ liệu bất thường giữa các triệu chứng lâm sàng cần bác sĩ rà soát."
        else:
            desc_3 = "Không thỏa mãn tiêu chí theo dõi phản vệ."

        steps.append({
            "num": 3,
            "title": "Theo dõi phản vệ",
            "prio": "Ưu tiên 3",
            "desc": desc_3,
        })

    elif form_type == "cap":
        # Bước 0: Điều kiện tiên quyết sàng lọc cấp
        r_base = rule_results.get("R-SANGLOC-CAP")
        if r_base is True:
            desc_0 = "Sẩn phù bờ rõ (tròn / vòng / bản đồ) + Có ảnh sẩn phù + Khởi phát trong vòng 6 tuần (<= 1008 giờ) -> ĐẠT điều kiện tiên quyết vào phân hệ Mày đay cấp."
        elif r_base is False:
            desc_0 = "Không thỏa mãn điều kiện sàng lọc cấp tính: Sẩn phù không rõ bờ, thiếu ảnh hoặc thời gian khởi phát vượt quá 6 tuần (> 1008 giờ)."
        else:
            desc_0 = "Thiếu thông tin đặc điểm sẩn phù, ảnh chụp hoặc thời gian khởi phát để hoàn thành sàng lọc tiên quyết."
        steps.append({
            "num": 0,
            "title": "Sàng lọc tiên quyết (R-SANGLOC-CAP)",
            "prio": "Tiên quyết",
            "desc": desc_0,
        })

        # Bước 1: Kiểm tra Dấu hiệu nặng
        ngua = rule_results.get("R01-CAP-NANG-NGUA")
        phumach = rule_results.get("R02-CAP-NANG-PHUMACH")
        conlai = rule_results.get("R03-CAP-NANG-CONLAI")

        if ngua is True:
            desc_1 = "Phát hiện triệu chứng da ngứa dữ dội (`Ngứa nhiều`) thỏa mãn R01-CAP-NANG-NGUA -> KẾT LUẬN MÀY ĐAY CẤP CÓ DẤU HIỆU NẶNG ngay lập tức, không xét các bước sau."
        elif phumach is True:
            desc_1 = "Phát hiện phù mạch đáng kể tại vị trí nguy hiểm (mi mắt, lưỡi, thanh quản, môi) hoặc từng vào viện thỏa mãn R02-CAP-NANG-PHUMACH -> KẾT LUẬN MÀY ĐAY CẤP CÓ DẤU HIỆU NẶNG."
        elif conlai is True:
            desc_1 = "Phát hiện sẩn phù kèm dấu hiệu tiêu hóa (nôn, đau bụng), hô hấp (khò khè, nghẹn họng) hoặc diện tích lan rộng (> 50% BSA, > 50 nốt) thỏa mãn R03-CAP-NANG-CONLAI -> KẾT LUẬN MÀY ĐAY CẤP CÓ DẤU HIỆU NẶNG."
        elif ngua is False and phumach is False and conlai is False:
            desc_1 = "Loại trừ toàn bộ các dấu hiệu nặng: Không ngứa nhiều, không phù mạch nguy hiểm, không có triệu chứng hô hấp/tiêu hóa toàn thân và diện tích không lan rộng."
        else:
            desc_1 = "Đang kiểm tra các dấu hiệu nặng: Có một số chỉ số chưa được cung cấp đầy đủ."
        steps.append({
            "num": 1,
            "title": "Kiểm tra Dấu hiệu nặng",
            "prio": "Ưu tiên cấp nặng",
            "desc": desc_1,
        })

        # Bước 2: Mày đay cấp thông thường
        r_thuong = rule_results.get("R01-CAP-THUONG")
        if r_thuong is True:
            desc_2 = "Thỏa mãn đầy đủ tiêu chuẩn có sẩn phù cấp VÀ đã loại trừ toàn bộ các dấu hiệu nặng ở Bước 1 -> KẾT LUẬN MÀY ĐAY CẤP THÔNG THƯỜNG."
        elif matched_id in ["R01-CAP-NANG-NGUA", "R02-CAP-NANG-PHUMACH", "R03-CAP-NANG-CONLAI"]:
            desc_2 = "Quy tắc cấp thông thường bị chặn (loại trừ) do bệnh nhân đã xuất hiện dấu hiệu nặng ở bước trước."
        elif r_thuong is False:
            desc_2 = "Không thỏa mãn quy tắc cấp thông thường do chưa đạt điều kiện cơ sở hoặc còn nghi vấn triệu chứng."
        else:
            desc_2 = "Chưa đủ dữ kiện để khẳng định mày đay cấp thông thường."
        steps.append({
            "num": 2,
            "title": "Mày đay cấp thông thường",
            "prio": "Ưu tiên cấp thường",
            "desc": desc_2,
        })

    elif form_type == "man":
        # Bước 1: Điều kiện tiên quyết CIndU & CSU
        r_cindu_00 = rule_results.get("R-CindU-00")
        r_csu_00 = rule_results.get("R-CSU-00")
        if r_cindu_00 is True:
            desc_1 = "Khởi phát > 6 tuần và triệu chứng xuất hiện khi có yếu tố kích thích -> ĐẠT điều kiện tiên quyết nhóm Mày đay cảm ứng (CIndU)."
        elif r_csu_00 is True:
            desc_1 = "Khởi phát > 6 tuần tự phát, tuổi >= 16, đã lưu mẫu huyết thanh, ngừng kháng H1 >= 8 ngày và corticoid >= 30 ngày -> ĐẠT điều kiện tiên quyết CSU."
        else:
            desc_1 = "Kiểm tra thời gian kéo dài trên 6 tuần và bối cảnh khởi phát (khi có yếu tố kích thích cơ học/nhiệt độ hay xuất hiện tự phát)."
        steps.append({
            "num": 1,
            "title": "Điều kiện tiên quyết Mày đay mạn (CIndU / CSU)",
            "prio": "Tiên quyết",
            "desc": desc_1,
        })

        # Bước 2: Khảo sát Mày đay cảm ứng mạn tính CIndU
        cindu_trues = [r for r in ["R-CindU-01", "R-CindU-02", "R-CindU-03", "R-CindU-04"] if rule_results.get(r) is True]
        if cindu_trues:
            c_rule = rules_by_id.get(cindu_trues[0], {})
            r_name = c_rule.get("display_name") or c_rule.get("name", cindu_trues[0])
            desc_2 = f"Test kích thích dương tính thỏa mãn {cindu_trues[0]} ({r_name}): {decision_trace} -> KẾT LUẬN {c_rule.get('target_label', '').upper()}."
        elif r_cindu_00 is True:
            desc_2 = "Bệnh nhân có hoàn cảnh kích thích nhưng các test thực nghiệm (FricTest, Cholinergic, nhiệt độ...) chưa có kết quả dương tính rõ."
        else:
            desc_2 = "Các test kích thích vật lý âm tính hoặc không có yếu tố kích thích -> Chuyển sang khảo sát phân hệ mày đay tự phát (CSU)."
        steps.append({
            "num": 2,
            "title": "Khảo sát Mày đay cảm ứng (CIndU)",
            "prio": "Nhóm CIndU",
            "desc": desc_2,
        })

        # Bước 3: Khảo sát Mày đay tự phát mạn tính CSU & Tự kháng thể
        r_gd1 = rule_results.get("R-GD-01")
        r_gd2 = rule_results.get("R-GD-02")
        csu_trues = [r for r in ["R-CSU-T1-01", "R-CSU-T1-02", "R-CSU-T2-01", "R-CSU-OVL-01", "R-CSU-UNK-01", "R-CSU-UNK-02"] if rule_results.get(r) is True]

        if csu_trues:
            c_rule = rules_by_id.get(csu_trues[0], {})
            r_name = c_rule.get("display_name") or c_rule.get("name", csu_trues[0])
            asst_text = "Giai đoạn 1 (ASST +)" if r_gd1 else "Giai đoạn 2 (ASST -, chuẩn Stella)"
            desc_3 = f"Phân nhánh {asst_text}. Kết quả ELISA thỏa mãn {csu_trues[0]} ({r_name}): {decision_trace} -> KẾT LUẬN {c_rule.get('target_label', '').upper()}."
        elif r_gd1 is True:
            desc_3 = "ASST dương tính (+) -> Vào GĐ1: Theo dõi đủ 60 ngày và định lượng tự kháng thể (IgG kháng FcεRIα/IgE, IgE kháng IL-24)."
        elif r_gd2 is True:
            desc_3 = "ASST âm tính (−) đạt chuẩn Stella -> Vào GĐ2: Định lượng IgE kháng IL-24."
        else:
            desc_3 = "Chưa hoàn thành phân nhánh ASST hoặc chưa có đủ xét nghiệm tự kháng thể chuyên sâu."
        steps.append({
            "num": 3,
            "title": "Khảo sát Mày đay tự phát CSU & Tự kháng thể",
            "prio": "Nhóm CSU",
            "desc": desc_3,
        })

        # Bước 4: Chưa đủ dữ liệu / Ngoại lệ
        if matched_id == "R-DEFAULT" or status == "INSUFFICIENT_DATA":
            desc_4 = "Hồ sơ chưa đủ điều kiện phân loại chuyên sâu (thiếu kết quả ASST, chưa theo dõi đủ 60 ngày hoặc thiếu xét nghiệm ELISA) -> CHƯA PHÂN LOẠI, TIẾP TỤC THEO DÕI."
        elif cindu_trues or csu_trues:
            desc_4 = "Đã đầy đủ dữ kiện và chẩn đoán xác định rõ ở các bước trên, không chuyển sang diện chưa phân loại."
        else:
            desc_4 = "Đánh giá tình trạng hoàn thiện của hồ sơ bệnh án mạn tính."
        steps.append({
            "num": 4,
            "title": "Chưa đủ dữ liệu / Tiếp tục theo dõi",
            "prio": "Ngoại lệ",
            "desc": desc_4,
        })

    return steps


def render() -> None:
    st.set_page_config(page_title="Rule-based Mày đay", page_icon="🩺", layout="wide")

    # Header trang nhã, đơn giản
    header_col, mode_col = st.columns([1.6, 1.4], gap="medium")
    with header_col:
        st.markdown(
            "<div style='padding: 0.2rem 0;'>"
            "<h2 style='margin:0; font-weight:800; color:#0f172a; font-size:1.65rem; letter-spacing:-0.02em;'>"
            "🩺 HỆ THỐNG RULE-BASED MÀY ĐAY</h2>"
            "<p style='margin:0.25rem 0 0 0; color:#64748b; font-size:0.85rem;'>"
            "Hỗ trợ chẩn đoán phân hệ 3 bệnh án độc lập: Phản vệ, Mày đay cấp và Mày đay mạn</p>"
            "</div>",
            unsafe_allow_html=True,
        )
    with mode_col:
        # Bộ chọn 3 phân hệ bệnh án độc lập
        form_type = st.selectbox(
            "Phân hệ bệnh án đang làm việc",
            ["phan_ve", "cap", "man"],
            format_func=lambda value: FORM_NAMES[value],
            key="form_type",
            on_change=clear_result,
            help="Chuyển đổi giữa 3 phân hệ bệnh án độc lập. Mỗi phân hệ áp dụng bộ quy tắc y khoa riêng biệt.",
        )

    st.markdown("<hr style='margin:0.5rem 0 0.8rem 0; border:0; border-top:1px solid #e2e8f0;'>", unsafe_allow_html=True)

    # Khối Hướng dẫn sử dụng & Cách đọc kết quả
    with st.expander("Hướng dẫn sử dụng hệ thống · Cách đọc kết quả", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                "**1. Chọn bệnh án & Ca mẫu**  \n"
                "Chọn phân hệ bệnh án ở trên, sau đó chọn ca giả định hoặc tải file ở cột trái rồi bấm **Phân loại**."
            )
        with c2:
            st.markdown(
                "**2. Xem kết quả chẩn đoán**  \n"
                "Xem kết luận bệnh to rõ, lý do lâm sàng và bảng đối chiếu các quy tắc y khoa vừa được kích hoạt."
            )
        with c3:
            st.markdown(
                "**3. Mở tab Logic suy luận**  \n"
                "Xem quá trình máy tính phân giải từ ưu tiên cao đến thấp theo đúng phân hệ bệnh án đã chọn."
            )
        with c4:
            st.markdown(
                "**4. Thử nghiệm ca biên**  \n"
                "Sửa trực tiếp số đo ô JSON bên cạnh (trước/tại/sau ngưỡng) rồi bấm chạy lại để đối chiếu kết quả."
            )

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.markdown("**Ý nghĩa các trạng thái chẩn đoán:**")
        st.table([{"Trạng thái": STATUS_LABELS[status], "Ý nghĩa": explanation}
                  for status, explanation in STATUS_HELP.items()])
        st.caption("TRUE/FALSE/UNKNOWN là trạng thái điều kiện y khoa, không phải nhãn bệnh. Ưu tiên số nhỏ hơn được xét trước.")

    try:
        engines = load_engines()
        fixture = json.loads((ROOT / "data/synthetic/rule_logic_cases.json").read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        st.error(f"Không nạp được cấu hình ({type(exc).__name__}). Kiểm tra YAML và bộ ca giả định.")
        return

    engine = engines[form_type]
    rules = {rule["rule_id"]: rule for rule in engine.rules}
    targets = [rule for rule in engine.rules if "target_label" in rule]
    labels = list(dict.fromkeys(rule["target_label"] for rule in targets))

    st.session_state.setdefault("result", None)
    st.session_state.setdefault("run_error", None)
    st.session_state.setdefault("patient_json", "{}")

    # Sidebar: Cột chọn nội dung minh họa của riêng phân hệ đang chọn
    st.sidebar.markdown(f"### 📋 Chọn nội dung minh họa\n**Phân hệ:** {FORM_SHORT_NAMES[form_type]}")
    data_source_mode = st.sidebar.radio(
        "Nguồn bệnh án", ["Ca giả định mẫu", "Tải file mới (.json, .csv)"],
        key="source_mode", on_change=clear_result,
    )
    if st.session_state.get("active_source") != data_source_mode:
        st.session_state["loaded_case"] = None
        st.session_state["loaded_upload"] = None
        st.session_state["patient_json"] = "{}"
        st.session_state["active_source"] = data_source_mode
        clear_result()

    selected_label = "Tất cả"
    mismatch_warning = None

    if data_source_mode == "Tải file mới (.json, .csv)":
        uploaded_file = st.sidebar.file_uploader(
            f"Tải file hồ sơ ({FORM_SHORT_NAMES[form_type]})", type=["json", "csv"],
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
                    mismatch_warning = check_cross_form_mismatch(form_type, patient_data)
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
            filtered_du_lieu = filter_patient_by_engine(selected_case["du_lieu"], engine)
            st.session_state["patient_json"] = json.dumps(filtered_du_lieu, ensure_ascii=False, indent=2)
            st.session_state["loaded_case"] = case_id
            clear_result()

    st.sidebar.markdown(
        f"<div style='margin-top:0.8rem; padding:0.6rem 0.8rem; background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0; font-size:0.75rem; color:#475569;'>"
        f"<strong>Phạm vi:</strong> {FORM_SHORT_NAMES[form_type]}<br>"
        f"<strong>Bộ máy xử lý:</strong> Phân hệ {form_type} độc lập<br>"
        f"<strong>Cơ sở tri thức:</strong> Rules v{engine.rules_version}"
        f"</div>",
        unsafe_allow_html=True,
    )

    if mismatch_warning:
        st.warning(f"⚠️ **Khuyến nghị:** {mismatch_warning}")

    # Khu vực nội dung chính: 3 Tabs chuẩn
    input_tab, layers_tab, catalog_tab = st.tabs([
        "Bệnh án & kết quả", "Logic suy luận", "Bảng quy tắc & Mức ưu tiên",
    ])

    try:
        current_patient = parse_patient(st.session_state["patient_json"])
    except (ValueError, RecursionError):
        current_patient = None
    expected_patient = filter_patient_by_engine(selected_case["du_lieu"], engine)
    input_changed = current_patient != expected_patient

    # ==========================================
    # TAB 1: BỆNH ÁN & KẾT QUẢ
    # ==========================================
    with input_tab:
        st.markdown(f"<div style='font-size:0.9rem; color:#475569; margin-bottom:0.5rem;'><strong>Mô tả ca:</strong> {selected_case['mo_ta']}</div>", unsafe_allow_html=True)
        
        result = st.session_state["result"]
        highlights = evidence_highlights(result, rules) if result else {}

        left, right = st.columns([1.35, 1], gap="large")

        # Cột trái: Dữ liệu bệnh án (Phiếu khám & Mã JSON)
        with left:
            st.markdown("#### Dữ liệu bệnh án (Phiếu khám lâm sàng & Mã JSON)")
            st.caption("Xem thông tin định dạng phiếu khám bên trái; chỉnh sửa biến bên phải rồi bấm Phân loại.")

            preview_col, editor_col = st.columns(2, gap="small")
            with preview_col:
                st.markdown(
                    f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>"
                    f"<strong style='font-size:0.8rem; color:#1e40af;'>PHIẾU KHÁM: {case_id}</strong>"
                    f"<span style='font-size:0.7rem; color:#64748b;'>{FORM_SHORT_NAMES[form_type]}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                if current_patient is None:
                    st.warning("Không thể hiển thị bệnh án: JSON chưa hợp lệ. Sửa dữ liệu ở ô JSON.")
                else:
                    try:
                        display_patient = filter_patient_by_engine(current_patient, engine)
                        st.html(patient_html(display_patient, highlights))
                    except RecursionError:
                        st.warning("Không thể hiển thị bệnh án: cấu trúc JSON lồng quá nhiều tầng.")

            with editor_col:
                st.markdown(
                    "<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>"
                    "<strong style='font-size:0.8rem; color:#334155;'>Mã JSON (Chỉnh sửa tùy ý):</strong>"
                    "</div>",
                    unsafe_allow_html=True,
                )
                st.text_area(
                    "Mã JSON bệnh án", height=380, key="patient_json", on_change=clear_result,
                    label_visibility="collapsed",
                )
                st.caption("Sửa trực tiếp số đo để thử ca biên. Dữ liệu thay đổi sẽ xóa kết quả cũ.")

            # Nút bấm hành động chính: Rõ ràng, nổi bật
            if st.button("⚡ Phân loại và giải thích", key="classify", type="primary", use_container_width=True):
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
                st.rerun()

            if selected_case["expected_engine"]:
                with st.expander("Kỳ vọng của ca gốc — để đối chiếu sau suy diễn"):
                    if input_changed:
                        st.warning("JSON hiện tại đã khác ca gốc: kỳ vọng bên dưới không tự cập nhật.")
                    exp = selected_case["expected_engine"]
                    expected_rows = []
                    if "status" in exp:
                        expected_rows.append({"Chỉ số y khoa": "Trạng thái chẩn đoán", "Kỳ vọng ca gốc": STATUS_LABELS.get(exp["status"], exp["status"])})
                    if "predicted_label" in exp:
                        expected_rows.append({"Chỉ số y khoa": "Kết luận bệnh", "Kỳ vọng ca gốc": exp["predicted_label"] or "Chưa kết luận"})
                    if "matched_rule_id" in exp:
                        rule_name = rules.get(exp["matched_rule_id"], {}).get("name", "")
                        display_rule = f"{exp['matched_rule_id']} ({rule_name})" if rule_name else exp["matched_rule_id"]
                        expected_rows.append({"Chỉ số y khoa": "Quy tắc (Rule) khớp", "Kỳ vọng ca gốc": display_rule or "Không có"})
                    if "priority" in exp:
                        exp_rule = rules.get(exp.get("matched_rule_id"), {})
                        exp_prio_label = exp_rule.get("priority_label")
                        exp_prio_text = exp_prio_label if exp_prio_label else f"Ưu tiên {exp['priority']}"
                        expected_rows.append({"Chỉ số y khoa": "Mức ưu tiên", "Kỳ vọng ca gốc": exp_prio_text})
                    if expected_rows:
                        st.table(expected_rows)

        # Cột phải: Kết quả chẩn đoán của hệ thống
        with right:
            st.markdown("#### Kết quả chẩn đoán của hệ thống")

            if st.session_state["run_error"]:
                st.error(st.session_state["run_error"])
            elif result is None:
                st.info("Bấm **⚡ Phân loại và giải thích** ở bên trái để xem kết quả chẩn đoán cho dữ liệu hiện tại.")
            else:
                title = "Theo dõi phản vệ" if result["status"] == "THEODOIPV" else (result["predicted_label"] or "Chưa kết luận bệnh")
                st.subheader("KẾT LUẬN: " + title.upper())
                st.markdown(f"**Trạng thái:** {STATUS_LABELS[result['status']]}")
                matched_rule = rules.get(result.get("matched_rule_id"), {})
                prio_label = matched_rule.get("priority_label")
                prio_val = matched_rule.get("priority")
                if prio_label and prio_label.startswith("Ưu tiên "):
                    prio_str = prio_label.replace("Ưu tiên ", "").strip()
                elif prio_label:
                    prio_str = prio_label
                else:
                    prio_str = str(prio_val if prio_val is not None else result.get("priority", ""))
                st.caption(f"Mức ưu tiên: {prio_str}")

                explanation = f"**{STATUS_LABELS[result['status']]}** — {STATUS_HELP[result['status']]}"
                if result["status"] == "NEEDS_REVIEW":
                    st.error(explanation)
                elif result["status"] in {"INSUFFICIENT_DATA", "UNRESOLVED", "THEODOIPV"}:
                    st.warning(explanation)

                st.markdown(
                    f"<div style='background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:0.6rem 0.8rem; margin:0.5rem 0; font-size:0.85rem; color:#1e293b;'>"
                    f"<strong>Lý do lâm sàng:</strong><br>{result['decision_trace']}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                if result["missing_fields"]:
                    st.markdown("**Trường cần bổ sung:**")
                    field_labels = clinical_field_labels()
                    for raw_field in result["missing_fields"]:
                        field = str(raw_field)
                        st.markdown("• " + " › ".join(field_labels.get(part, part) for part in field.split(".")))

                # Bảng đối chiếu các quy tắc y khoa
                st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
                st.markdown("##### Bảng các quy tắc được đối chiếu ca này")
                active_rules_rows = []
                for rule_id, rule in rules.items():
                    value = result["rule_results"][rule_id]
                    if value is True or rule_id in result["blocking_rule_ids"]:
                        role = ("Kết luận chính" if rule_id == result["matched_rule_id"] else
                                "Chặn / xung đột" if rule_id in result["blocking_rule_ids"] else "Khớp")
                        eval_text = "UNKNOWN" if value is None else "TRUE" if value else "FALSE"
                        active_rules_rows.append({
                            "Mã Rule": rule_id,
                            "Nội dung": rule["name"],
                            "Đánh giá": eval_text,
                            "Vai trò": role,
                        })
                if active_rules_rows:
                    st.table(active_rules_rows)
                else:
                    st.caption("Chưa có quy tắc nào đạt hoặc bị chặn trong lần đánh giá này.")

                st.download_button(
                    "Tải kết quả JSON", json.dumps(result, ensure_ascii=False, indent=2),
                    file_name=f"rule_result_{case_id}.json", mime="application/json",
                    use_container_width=True,
                )

            if selected_case["workflow_gap"]:
                issue_id = selected_case["workflow_gap"]
                st.warning(
                    f"**Ca gốc · {issue_id}** — {ISSUE_HELP[issue_id]} "
                    "Đây là chú thích của ca gốc; JSON đã sửa có thể có vấn đề khác."
                )

    # ==========================================
    # TAB 2: LOGIC SUY LUẬN
    # ==========================================
    with layers_tab:
        st.subheader("Logic suy luận của hệ thống")
        st.caption("Dữ liệu được máy tính suy diễn từ mức ưu tiên cao nhất đến thấp nhất theo đúng phân hệ bệnh án được chọn")

        if result:
            if result["status"] == "NEEDS_REVIEW":
                st.error(f"⚠️ **CẦN BÁC SĨ RÀ SOÁT (NEEDS_REVIEW):** {result['decision_trace']}")
            elif result["status"] == "INSUFFICIENT_DATA":
                st.warning(f"⚠️ **THIẾU DỮ LIỆU BỆNH ÁN (INSUFFICIENT_DATA):** {result['decision_trace']}")

            steps = generate_dynamic_reasoning_steps(form_type, engine, result)
        else:
            st.info("Chưa chạy suy luận cho ca bệnh hiện tại. Bấm **⚡ Phân loại và giải thích** ở Tab 1 để đối chiếu dữ liệu. Dưới đây là các bước quy chuẩn của phân hệ này:")
            steps = generate_dynamic_reasoning_steps(form_type, engine, None)

        cards_html = "".join([
            f'<div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:1.1rem; margin-bottom:0.85rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">'
            f'<div style="font-weight:700; color:#1e40af; font-size:0.95rem; margin-bottom:0.35rem;">'
            f'Bước {s["num"]}: {s["title"]} ({s["prio"]})'
            f'</div>'
            f'<div style="color:#334155; font-size:0.85rem; line-height:1.6;">'
            f'{s["desc"]}'
            f'</div>'
            f'</div>'
            for s in steps
        ])
        clean_cards_html = "\n".join(line.strip() for line in cards_html.splitlines())
        st.markdown(clean_cards_html, unsafe_allow_html=True)

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        st.markdown("##### Chi tiết đánh giá lâm sàng theo phân tầng quy tắc:")
        engine_layers = get_engine_layers(engine)
        for title, identifiers in engine_layers:
            identifiers = [identifier for identifier in identifiers if identifier in rules]
            if not identifiers:
                continue
            with st.expander(title, expanded=False):
                for identifier in identifiers:
                    rule = rules[identifier]
                    value = result["rule_results"][identifier] if result else None
                    state = "Chưa đánh giá" if result is None else "Chưa đủ dữ kiện" if value is None else "ĐẠT" if value else "Không đạt"
                    marker = ""
                    if result and identifier == result["matched_rule_id"]:
                        marker = " · ⭐ KẾT LUẬN CHÍNH"
                    elif result and identifier in result["blocking_rule_ids"]:
                        marker = " · ⚠️ BỊ CHẶN"
                    elif result and identifier in result["matched_rule_ids"]:
                        marker = " · 🎯 KHỚP TIÊU CHÍ"
                    display_title = rule.get("display_name") or rule.get("name")
                    st.markdown(f"**{identifier} — {display_title}** · `{state}`{marker}")
                    crit = rule.get("criteria_text") or rule.get("decision_trace")
                    if crit:
                        st.caption(f"Tiêu chuẩn y khoa: {crit}")
                    if result:
                        events = [event for event in result["trace"] if event["rule_id"] == identifier]
                        formatted_events = format_trace_events(events, clinical_field_labels(), engine, current_patient)
                        if formatted_events:
                            with st.expander(f"Dữ kiện đối chiếu lâm sàng · {identifier}", expanded=False):
                                st.table(formatted_events)
                    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

    # ==========================================
    # TAB 3: BẢNG QUY TẮC & MỨC ƯU TIÊN
    # ==========================================
    with catalog_tab:
        form_title = FORM_FULL_TITLES.get(form_type, f"Bệnh án {FORM_SHORT_NAMES[form_type]}")
        header_html = (
            f'<div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">'
            f'<div>'
            f'<h3 style="margin:0; font-size:1.15rem; font-weight:800; color:#0f172a;">Bảng quy tắc phân hệ {form_title}</h3>'
            f'<p style="margin:0.25rem 0 0 0; font-size:0.8rem; color:#64748b;">Mức độ ưu tiên và điều kiện y khoa được áp dụng riêng cho phân hệ này, viết bằng ngôn ngữ dễ hiểu</p>'
            f'</div>'
            f'<span style="font-size:0.75rem; font-weight:600; padding:0.25rem 0.65rem; background:#f1f5f9; color:#475569; border-radius:8px; border:1px solid #e2e8f0;">'
            f'Nội dung quy chuẩn'
            f'</span>'
            f'</div>'
        )
        clean_header_html = "\n".join(line.strip() for line in header_html.splitlines())
        st.markdown(clean_header_html, unsafe_allow_html=True)

        catalog_rows = []
        for rule in engine.rules:
            prio = rule.get("priority_label") or (f"Ưu tiên {rule['priority']}" if rule.get("priority") is not None else "Tiên quyết")
            r_id = rule.get("rule_id", "")
            name = rule.get("display_name") or rule.get("target_label") or rule.get("name", "")
            crit = rule.get("criteria_text") or rule.get("decision_trace") or rule.get("name", "")
            catalog_rows.append({
                "Mức ưu tiên": prio,
                "Mã Rule": r_id,
                "Kết luận bệnh": name,
                "Tiêu chí chẩn đoán (Ngôn ngữ thường, không dùng code)": crit,
            })

        table_rows = "".join([
            f'<tr style="border-bottom: 1px solid #f1f5f9;">'
            f'<td style="padding: 0.75rem 1rem; font-weight: 700; color: #1e293b; white-space: nowrap;">{row["Mức ưu tiên"]}</td>'
            f'<td style="padding: 0.75rem 1rem; font-family: monospace; font-weight: 700; color: #2563eb; white-space: nowrap;">{row["Mã Rule"]}</td>'
            f'<td style="padding: 0.75rem 1rem; font-weight: 600; color: #0f172a;">{row["Kết luận bệnh"]}</td>'
            f'<td style="padding: 0.75rem 1rem; color: #334155; line-height: 1.5;">{row["Tiêu chí chẩn đoán (Ngôn ngữ thường, không dùng code)"]}</td>'
            f'</tr>'
            for row in catalog_rows
        ])
        table_html = (
            f'<div style="overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 12px; margin-top: 0.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">'
            f'<table style="width: 100%; border-collapse: collapse; font-size: 0.825rem; text-align: left; background: #ffffff;">'
            f'<thead>'
            f'<tr style="background: #f8fafc; color: #334155; font-weight: 700; border-bottom: 1px solid #e2e8f0;">'
            f'<th style="padding: 0.75rem 1rem; width: 14%;">Mức ưu tiên</th>'
            f'<th style="padding: 0.75rem 1rem; width: 15%;">Mã Rule</th>'
            f'<th style="padding: 0.75rem 1rem; width: 25%;">Kết luận bệnh</th>'
            f'<th style="padding: 0.75rem 1rem; width: 46%;">Tiêu chí chẩn đoán (Ngôn ngữ thường, không dùng code)</th>'
            f'</tr>'
            f'</thead>'
            f'<tbody>'
            f'{table_rows}'
            f'</tbody>'
            f'</table>'
            f'</div>'
        )
        clean_table_html = "\n".join(line.strip() for line in table_html.splitlines())
        st.markdown(clean_table_html, unsafe_allow_html=True)


if __name__ == "__main__":
    render()
