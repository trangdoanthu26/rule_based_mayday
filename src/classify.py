"""
Bộ máy suy diễn Rule-based (Clinical Inference Engine).
Nạp quy tắc từ rules/classification_rules.yaml và đánh giá từng bản ghi bệnh nhân.
"""

from typing import Any, Dict, List, Optional
import yaml


class ClinicalRuleEngine:
    def __init__(self, rules_file_path: str):
        with open(rules_file_path, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
            self.rules = content.get("rules", [])
            # Sắp xếp luật theo độ ưu tiên tăng dần (Priority 1 là khẩn cấp nhất)
            self.rules.sort(key=lambda x: x.get("priority", 99))
            self.cached_results: Dict[str, bool] = {}

    def _get_nested_field(self, data: Dict[str, Any], field_path: str) -> Any:
        """Truy xuất giá trị từ dict lồng nhau qua dấu chấm (VD: 'a.b.c')."""
        parts = field_path.split(".")
        cur = data
        for p in parts:
            if isinstance(cur, dict):
                cur = cur.get(p)
            else:
                return None
        return cur

    def _eval_condition(self, cond: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Đánh giá 1 điều kiện cơ bản hoặc điều kiện lồng nhau."""
        if "all_of" in cond:
            return all(self._eval_condition(c, data) for c in cond["all_of"])

        if "any_of" in cond:
            return any(self._eval_condition(c, data) for c in cond["any_of"])

        if "not" in cond:
            return not self._eval_condition(cond["not"], data)

        if "ref_rule" in cond:
            ref_id = cond["ref_rule"]
            return self.cached_results.get(ref_id, False)

        op = cond.get("operator")

        # Toán tử đếm số hệ cơ quan tổn thương (Dành riêng cho Phản vệ R02-PV)
        if op == "count_matching_systems_gte":
            min_count = cond.get("min_count", 2)
            matched_systems = 0
            for _, sys_cond in cond.get("systems", {}).items():
                if self._eval_condition(sys_cond, data):
                    matched_systems += 1
            return matched_systems >= min_count

        field_name = cond.get("field")
        actual_val = self._get_nested_field(data, field_name)
        expected_val = cond.get("value")

        if op == "==":
            return actual_val == expected_val
        elif op == "!=":
            return actual_val != expected_val
        elif op == "<":
            return actual_val is not None and float(actual_val) < float(expected_val)
        elif op == "<=":
            return actual_val is not None and float(actual_val) <= float(expected_val)
        elif op == ">":
            return actual_val is not None and float(actual_val) > float(expected_val)
        elif op == ">=":
            return actual_val is not None and float(actual_val) >= float(expected_val)
        elif op == "contains":
            if isinstance(actual_val, list):
                return expected_val in actual_val
            return expected_val in str(actual_val)
        elif op == "contains_any":
            if isinstance(actual_val, list):
                return any(item in actual_val for item in expected_val)
            return any(item in str(actual_val) for item in expected_val)
        elif op == "<_formula":
            formula = cond.get("formula", "")
            if "70 + 2 * tuoi" in formula:
                tuoi = float(data.get("tuoi", 1))
                return actual_val is not None and float(actual_val) < (70.0 + 2.0 * tuoi)
            elif "0.7 * huyet_ap_tam_thu_nen" in formula:
                ha_nen = float(data.get("huyet_ap_tam_thu_nen", 120))
                return actual_val is not None and float(actual_val) < (0.7 * ha_nen)

        return False

    def classify_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phân loại ca bệnh theo thứ tự ưu tiên."""
        self.cached_results.clear()

        # Bước 1: Đánh giá trước các luật cơ sở/sàng lọc
        for rule in self.rules:
            rule_id = rule.get("rule_id")
            conds = rule.get("conditions", {})
            is_matched = self._eval_condition(conds, patient_data)
            self.cached_results[rule_id] = is_matched

            # Nếu là luật đích (có target_label) và thỏa mãn điều kiện
            if is_matched and "target_label" in rule:
                return {
                    "patient_token_id": patient_data.get("patient_token_id", "UNKNOWN"),
                    "predicted_label": rule.get("target_label"),
                    "matched_rule_id": rule_id,
                    "priority": rule.get("priority"),
                    "decision_trace": rule.get("decision_trace", ""),
                    "status": "CLASSIFIED"
                }

        # Nếu không thỏa mãn bất kỳ luật nào
        return {
            "patient_token_id": patient_data.get("patient_token_id", "UNKNOWN"),
            "predicted_label": "Chưa xác định",
            "matched_rule_id": None,
            "priority": 99,
            "decision_trace": "Dữ liệu không khớp bất kỳ tiêu chuẩn nào của Phản vệ hay Mày đay cấp.",
            "status": "UNRESOLVED"
        }