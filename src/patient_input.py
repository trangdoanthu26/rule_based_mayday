"""Engine-shaped input and explicit, per-visit mapping of HIS exports."""

import ast
import copy
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.classify import ClinicalRuleEngine


ROOT = Path(__file__).resolve().parents[1]
RAW_SECTIONS = ("hanh_chinh", "chan_doan", "dhst", "xet_nghiem", "cdha_tdcn", "thuoc")


def get_value(patient: Dict[str, Any], path: str) -> Any:
    value = patient
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def set_value(patient: Dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    for part in parts[:-1]:
        if not isinstance(patient.get(part), dict):
            patient[part] = {}
        patient = patient[part]
    patient[parts[-1]] = value


def engine_fields(form_type: str, engine: ClinicalRuleEngine) -> List[Dict[str, Any]]:
    if form_type not in {"phan_ve", "cap", "man"}:
        raise ValueError("Mẫu bệnh án không hợp lệ.")
    schema = json.loads((ROOT / "schema" / f"{form_type}_schema.json").read_text(encoding="utf-8"))
    conditions = {}

    def collect(node):
        if isinstance(node, dict):
            if "field" in node:
                conditions.setdefault(node["field"], []).append(node)
            if "formula" in node:
                for name in ast.walk(ast.parse(node["formula"], mode="eval")):
                    if isinstance(name, ast.Name):
                        conditions.setdefault(name.id, []).append({"operator": "<", "value": 0.0})
            for child in node.values():
                collect(child)
        elif isinstance(node, list):
            for child in node:
                collect(child)

    collect(engine.rules)
    fields = []
    for path, nodes in conditions.items():
        prop = schema
        for part in path.split("."):
            prop = prop.get("properties", {}).get(part, {})
        types = prop.get("type", [])
        types = [types] if isinstance(types, str) else types
        item_field = next((n["item_field"] for n in nodes if "item_field" in n), None)
        literals = []
        for node in nodes:
            value = node.get("value")
            literals.extend(value if isinstance(value, list) else [value])
        if "number" in types or "integer" in types or any(type(v) in (int, float) for v in literals):
            kind = "number"
        elif "boolean" in types or any(isinstance(v, bool) for v in literals):
            kind = "boolean"
        elif "array" in types or item_field or any(n.get("operator", "").startswith("contains") for n in nodes):
            kind = "array"
        else:
            kind = "select"
        choice_prop = prop
        if kind == "array":
            choice_prop = prop.get("items", {})
            if item_field:
                choice_prop = choice_prop.get("properties", {}).get(item_field, {})
        choices = []
        for value in list(choice_prop.get("enum", [])) + literals:
            if isinstance(value, str) and value.lower() not in {"unknown", "n/a", ""} and value not in choices:
                choices.append(value)
        fields.append({"path": path, "kind": kind, "choices": choices, "item_field": item_field,
                       "integer": "integer" in types,
                       "minimum": prop.get("minimum", 0)})
    return fields


def empty_patient(form_type: str, engine: ClinicalRuleEngine) -> Dict[str, Any]:
    patient = {}
    for field in engine_fields(form_type, engine):
        set_value(patient, field["path"], None)
    return patient


def merge_form(patient: Dict[str, Any], fields: List[Dict[str, Any]], values: Dict[str, Any]) -> Dict[str, Any]:
    result = copy.deepcopy(patient)
    for field in fields:
        path = field["path"]
        value = values[path]
        if value is not None and field["item_field"]:
            key = field["item_field"]
            previous = get_value(patient, path)
            previous = previous if isinstance(previous, list) else []
            value = [copy.deepcopy(next((row for row in previous if isinstance(row, dict) and row.get(key) == item),
                                         {key: item})) for item in value]
        set_value(result, path, value)
    return result


def is_raw(record: Any) -> bool:
    return isinstance(record, dict) and "du_lieu" not in record and "hanh_chinh" in record


def raw_patients(record: Dict[str, Any]) -> List[str]:
    if not is_raw(record) or not isinstance(record["hanh_chinh"], list):
        raise ValueError("RAW cần bảng hanh_chinh dạng danh sách.")
    patients = []
    for section in RAW_SECTIONS:
        rows = record.get(section, [])
        if not isinstance(rows, list):
            raise ValueError("Các bảng RAW phải là danh sách.")
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("MA_BN_AN_DANH"), str) or not row["MA_BN_AN_DANH"].strip():
                raise ValueError("RAW có dòng thiếu mã liên kết bệnh nhân.")
            patient = row["MA_BN_AN_DANH"]
            if section == "hanh_chinh" and patient not in patients:
                patients.append(patient)
            elif patient not in patients:
                raise ValueError("Có dữ liệu không nối được với bảng hành chính.")
    if not patients:
        raise ValueError("RAW không có bệnh nhân.")
    return patients


def _number(value: Any) -> Any:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return None
    try:
        value = float(value)
    except (ValueError, OverflowError):
        return None
    return value if math.isfinite(value) and value >= 0 else None


def _timestamp(value: Any) -> Any:
    if not isinstance(value, str) or len(value) != 19:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def map_raw(record: Dict[str, Any], patient_id: str, visit_index: int, form_type: str,
            engine: ClinicalRuleEngine, confirm_ige: bool = False) -> Dict[str, Any]:
    patients = raw_patients(record)
    indexed_visits = [(i, r) for i, r in enumerate(record["hanh_chinh"]) if r["MA_BN_AN_DANH"] == patient_id]
    visits = [row for _, row in indexed_visits]
    if patient_id not in patients or type(visit_index) is not int or not 0 <= visit_index < len(visits):
        raise ValueError("Chọn bệnh nhân và lượt khám hợp lệ.")
    admin = visits[visit_index]
    admin_index = indexed_visits[visit_index][0]
    data = empty_patient(form_type, engine)
    data["ma_benh_nhan"] = f"benh_nhan_{patients.index(patient_id) + 1}"
    provenance = []
    warnings = ["Tuổi được sao chép từ tuổi ghi nhận tại lượt khám; cần kiểm tra đơn vị tuổi của HIS."]

    def assign(field, value, source):
        set_value(data, field, value)
        provenance.append({"field": field, "source": source})

    age = _number(admin.get("TUOI_KHI_VAO_VIEN"))
    if age is not None:
        assign("tuoi", age, f"hanh_chinh[{admin_index}].TUOI_KHI_VAO_VIEN")
    if admin.get("GIOI_TINH") in ("Nam", "Nữ"):
        assign("gioi_tinh", admin["GIOI_TINH"], f"hanh_chinh[{admin_index}].GIOI_TINH")
    windows = [(_timestamp(v.get("IN_TIME")), _timestamp(v.get("OUT_TIME"))) for v in visits]

    def belongs(row, time_field):
        if row["MA_BN_AN_DANH"] != patient_id:
            return False
        if admin.get("TREATMENT_ID") and row.get("TREATMENT_ID"):
            return row["TREATMENT_ID"] == admin["TREATMENT_ID"]
        timestamp = _timestamp(row.get(time_field))
        if timestamp is None or any(start is None or end is None or end < start for start, end in windows):
            return False
        matches = [index for index, (start, end) in enumerate(windows) if start <= timestamp <= end]
        return matches == [visit_index]

    if form_type == "phan_ve":
        pressures = [(i, _number(row.get("BLOOD_PRESSURE_MAX"))) for i, row in enumerate(record.get("dhst", []))
                     if belongs(row, "EXECUTE_TIME")]
        pressures = [(i, value) for i, value in pressures if value is not None and value > 0]
        if pressures:
            index, pressure = min(pressures, key=lambda item: item[1])
            assign("huyet_ap_tam_thu_thap_nhat", pressure, f"dhst[{index}].BLOOD_PRESSURE_MAX (min trong lượt khám)")

    candidates = []
    eligible = []
    for index, row in enumerate(record.get("xet_nghiem", [])):
        if row["MA_BN_AN_DANH"] != patient_id or row.get("TEST_INDEX_CODE") != "SHM0027":
            continue
        unit_ok = str(row.get("TEST_INDEX_UNIT_NAME", "")).replace(" ", "").lower() in {"iu/ml", "ui/ml"}
        value = _number(row.get("VALUE"))
        same_visit = belongs(row, "TDL_INTRUCTION_TIME")
        candidates.append({"code": "SHM0027", "name": row.get("TEST_INDEX_NAME", "IgE"),
                           "value": row.get("VALUE"), "unit": row.get("TEST_INDEX_UNIT_NAME"),
                           "time": row.get("TDL_INTRUCTION_TIME"), "same_visit": same_visit,
                           "unit_valid": unit_ok, "source": f"xet_nghiem[{index}]"})
        if unit_ok and same_visit and value is not None:
            eligible.append((index, value))
    target = "ige_toan_phan_uiml" if form_type == "phan_ve" else "ige_toan_phan"
    if confirm_ige and len({value for _, value in eligible}) == 1:
        assign(target, eligible[0][1], f"xet_nghiem[{eligible[0][0]}].VALUE; mã SHM0027 đã được xác nhận IgE toàn phần")
    elif candidates:
        warnings.append("IgE chưa được đưa vào input: cần xác nhận IgE toàn phần, đơn vị, lượt khám và kết quả không xung đột.")
    warnings.append("Các trường không có nguồn giữ null; không suy triệu chứng/test từ ICD hoặc thuốc đã kê.")
    return {"du_lieu": data, "provenance": provenance, "candidates": candidates, "warnings": warnings,
            "visit_context": {"in_time": admin.get("IN_TIME"), "out_time": admin.get("OUT_TIME")}}
