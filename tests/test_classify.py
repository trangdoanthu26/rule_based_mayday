import hashlib
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List

import yaml

from src.classify import ClinicalRuleEngine


class RuleEngineTestCase(unittest.TestCase):
    def make_engine(self, rules: List[Dict[str, Any]]) -> ClinicalRuleEngine:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "rules.yaml"
        path.write_text(
            yaml.safe_dump({"version": "test-core", "rules": rules}, allow_unicode=True),
            encoding="utf-8",
        )
        return ClinicalRuleEngine(str(path))


class TestRuleConfiguration(RuleEngineTestCase):
    def test_project_yaml_loads(self):
        engine = ClinicalRuleEngine("rules/phan_ve_rules.yaml")
        ids = [rule["rule_id"] for rule in engine.rules]

        self.assertEqual(len(ids), 5)
        self.assertEqual(len(set(ids)), 5)
        self.assertTrue({"R-SOC", "R01-PV", "R02-PV"}.issubset(ids))
        self.assertEqual(engine.rules_version, "1.3.0")
        self.assertEqual(engine._rules_by_id["R-PV-THEODOI"]["target_status"], "THEODOIPV")
        self.assertEqual(engine.rules_sha256, hashlib.sha256(
            Path("rules/phan_ve_rules.yaml").read_bytes()
        ).hexdigest())

    def test_invalid_config_is_rejected(self):
        base = {"rule_id": "BASE", "conditions": {"field": "x", "operator": "==", "value": 1}}
        cases = [
            ("empty document", ""),
            ("non-object root", [base]),
            ("rules is not a list", {"rules": {}}),
            ("missing ID", {"rules": [{"conditions": {}}]}),
            ("duplicate ID", {"rules": [base, base]}),
            ("dangling reference", {"rules": [{"rule_id": "A", "conditions": {"ref_rule": "B"}}]}),
            ("nested reference cycle", {"rules": [
                {"rule_id": "A", "conditions": {"not": {"all_of": [{"ref_rule": "B"}]}}},
                {"rule_id": "B", "conditions": {"any_of": [{"ref_rule": "A"}]}},
            ]}),
            ("empty all_of", {"rules": [{"rule_id": "A", "conditions": {"all_of": []}}]}),
            ("empty any_of", {"rules": [{"rule_id": "A", "conditions": {"any_of": []}}]}),
            ("unsupported operator", {"rules": [{"rule_id": "A", "conditions": {
                "field": "x", "operator": "approx", "value": 1,
            }}]}),
            ("unsupported formula", {"rules": [{"rule_id": "A", "conditions": {
                "field": "x", "operator": "<_formula", "formula": "x + 1",
            }}]}),
            ("unsupported status", {"rules": [{
                "rule_id": "A", "target_label": "A", "priority": 1,
                "target_status": "DONE", "conditions": {"field": "x", "operator": "==", "value": 1},
            }]}),
            ("unhashable status", {"rules": [{
                "rule_id": "A", "target_label": "A", "priority": 1,
                "target_status": [], "conditions": {"field": "x", "operator": "==", "value": 1},
            }]}),
            ("unhashable operator", {"rules": [{
                "rule_id": "A", "conditions": {"field": "x", "operator": [], "value": 1},
            }]}),
            ("missing comparison value", {"rules": [{
                "rule_id": "A", "conditions": {"field": "x", "operator": "=="},
            }]}),
            ("non-finite expected value", {"rules": [{
                "rule_id": "A", "conditions": {"field": "x", "operator": "==", "value": float("nan")},
            }]}),
            ("non-positive count", {"rules": [{"rule_id": "A", "conditions": {
                "operator": "count_matching_systems_gte", "min_count": 2,
                "systems": {"one": {"field": "x", "operator": "==", "value": True}},
            }}]}),
            ("target has no priority", {"rules": [{
                "rule_id": "A", "target_label": "A", "conditions": {"field": "x", "operator": "==", "value": True},
            }]}),
            ("boolean target priority", {"rules": [{
                "rule_id": "A", "target_label": "A", "priority": True,
                "conditions": {"field": "x", "operator": "==", "value": True},
            }]}),
            ("base and target", {"rules": [{
                "rule_id": "A", "is_base_condition": True, "target_label": "A", "priority": 1,
                "conditions": {"field": "x", "operator": "==", "value": True},
            }]}),
        ]
        for name, document in cases:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "bad.yaml"
                    if document == "":
                        path.write_text("", encoding="utf-8")
                    else:
                        path.write_text(yaml.safe_dump(document, allow_unicode=True), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        ClinicalRuleEngine(str(path))

    def test_unsafe_yaml_tag_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unsafe.yaml"
            path.write_text("!!python/object/apply:builtins.print ['unsafe']", encoding="utf-8")
            with self.assertRaises(ValueError):
                ClinicalRuleEngine(str(path))


class TestRuleEvaluation(RuleEngineTestCase):
    def test_missing_value_is_unknown(self):
        engine = self.make_engine([{
            "rule_id": "BASE",
            "conditions": {"field": "x", "operator": ">=", "value": 1},
        }])
        for value in (None, -1, "unknown", "N/A", "", True, float("nan"), float("inf"), "80"):
            with self.subTest(value=value):
                self.assertIsNone(engine._eval_rule("BASE", {"x": value}, {}, []))
        self.assertIsNone(engine._eval_rule("BASE", {}, {}, []))
        self.assertIs(engine._eval_rule("BASE", {"x": 0}, {}, []), False)
        self.assertIs(engine._eval_rule("BASE", {"x": 1}, {}, []), True)

    def test_three_valued_boolean_operators(self):
        for condition, data, expected in (
            ({"all_of": [{"field": "a", "operator": "==", "value": True},
                          {"field": "b", "operator": "==", "value": True}]}, {}, None),
            ({"all_of": [{"field": "a", "operator": "==", "value": False},
                          {"field": "b", "operator": "==", "value": True}]}, {"a": True}, False),
            ({"any_of": [{"field": "a", "operator": "==", "value": True},
                          {"field": "b", "operator": "==", "value": True}]}, {}, None),
            ({"any_of": [{"field": "a", "operator": "==", "value": True},
                          {"field": "b", "operator": "==", "value": True}]}, {"a": True}, True),
            ({"not": {"field": "a", "operator": "==", "value": True}}, {}, None),
            ({"not": {"field": "a", "operator": "==", "value": True}}, {"a": True}, False),
        ):
            with self.subTest(condition=condition, expected=expected):
                engine = self.make_engine([{"rule_id": "BASE", "conditions": condition}])
                self.assertIs(engine._eval_rule("BASE", data, {}, []), expected)

    def test_nested_path_distinguishes_missing_from_wrong_shape(self):
        engine = self.make_engine([{
            "rule_id": "BASE",
            "conditions": {"field": "a.b", "operator": ">=", "value": 1},
        }])
        trace = []
        self.assertIsNone(engine._eval_rule("BASE", {}, {}, trace))
        self.assertEqual(trace[-1]["reason"], "MISSING_VALUE")
        trace = []
        self.assertIsNone(engine._eval_rule("BASE", {"a": None}, {}, trace))
        self.assertEqual(trace[-1]["reason"], "MISSING_VALUE")
        trace = []
        self.assertIsNone(engine._eval_rule("BASE", {"a": []}, {}, trace))
        self.assertEqual(trace[-1]["reason"], "INVALID_TYPE")
        trace = []
        self.assertIs(engine._eval_rule("BASE", {"a": {"b": 1}}, {}, trace), True)
        self.assertIsNone(trace[-1]["reason"])

    def test_contains_requires_list_and_exact_membership(self):
        engine = self.make_engine([{
            "rule_id": "BASE",
            "conditions": {"field": "items", "operator": "contains", "value": "rash"},
        }])
        self.assertIs(engine._eval_rule("BASE", {"items": ["rash"]}, {}, []), True)
        self.assertIs(engine._eval_rule("BASE", {"items": []}, {}, []), False)
        trace = []
        self.assertIsNone(engine._eval_rule("BASE", {"items": "rash"}, {}, trace))
        self.assertEqual(trace[-1]["reason"], "INVALID_TYPE")

    def test_null_comparison_is_presence_check_but_sentinels_stay_unknown(self):
        for operator, value, absent, explicit_null, present in (
            ("==", None, True, True, False),
            ("!=", None, False, False, True),
        ):
            engine = self.make_engine([{
                "rule_id": "BASE",
                "conditions": {"field": "x", "operator": operator, "value": value},
            }])
            self.assertIs(engine._eval_rule("BASE", {}, {}, []), absent)
            self.assertIs(engine._eval_rule("BASE", {"x": None}, {}, []), explicit_null)
            self.assertIsNone(engine._eval_rule("BASE", {"x": "unknown"}, {}, []))
            self.assertIs(engine._eval_rule("BASE", {"x": 2}, {}, []), present)

    def test_forward_reference_ignores_yaml_order(self):
        first = {"rule_id": "A", "conditions": {"ref_rule": "B"}}
        second = {"rule_id": "B", "conditions": {"field": "x", "operator": "==", "value": 1}}
        for rules in ([first, second], [second, first]):
            engine = self.make_engine(rules)
            self.assertIs(engine._eval_rule("A", {"x": 1}, {}, []), True)

    def test_unknown_dependency_is_cached_once(self):
        engine = self.make_engine([
            {"rule_id": "A", "conditions": {"all_of": [{"ref_rule": "B"}, {"ref_rule": "B"}]}},
            {"rule_id": "B", "conditions": {"field": "x", "operator": ">=", "value": 1}},
        ])
        trace = []
        self.assertIsNone(engine._eval_rule("A", {}, {}, trace))
        self.assertEqual(sum(event["rule_id"] == "B" and event["operator"] == ">=" for event in trace), 1)

    def test_count_bounds(self):
        engine = self.make_engine([{
            "rule_id": "BASE",
            "conditions": {"operator": "count_matching_systems_gte", "min_count": 2, "systems": {
                "a": {"field": "a", "operator": "==", "value": True},
                "b": {"field": "b", "operator": "==", "value": True},
                "c": {"field": "c", "operator": "==", "value": True},
            }},
        }])
        self.assertIs(engine._eval_rule("BASE", {"a": True, "b": True}, {}, []), True)
        self.assertIs(engine._eval_rule("BASE", {"a": False, "b": False}, {}, []), False)
        self.assertIsNone(engine._eval_rule("BASE", {"a": True, "b": False}, {}, []))
        trace = []
        self.assertIsNone(engine._eval_rule("BASE", {"a": True, "b": False, "c": "bad"}, {}, trace))
        count_event = next(event for event in trace if event["operator"] == "count_matching_systems_gte")
        self.assertEqual(count_event["reason"], "INVALID_TYPE")

    def test_formula_requires_measured_inputs(self):
        age_rule = self.make_engine([{"rule_id": "BASE", "conditions": {
            "field": "sbp", "operator": "<_formula", "formula": "70 + 2 * tuoi",
        }}])
        self.assertIsNone(age_rule._eval_rule("BASE", {"sbp": 79}, {}, []))
        self.assertIs(age_rule._eval_rule("BASE", {"sbp": 79, "tuoi": 5}, {}, []), True)
        self.assertIsNone(age_rule._eval_rule("BASE", {"sbp": 79, "tuoi": True}, {}, []))
        trace = []
        self.assertIsNone(age_rule._eval_rule("BASE", {"sbp": 1, "tuoi": 10 ** 1000}, {}, trace))
        self.assertEqual(trace[-1]["reason"], "NON_FINITE")
        trace = []
        self.assertIsNone(age_rule._eval_rule("BASE", {"sbp": 1, "tuoi": 1.7e308}, {}, trace))
        self.assertEqual(trace[-1]["reason"], "NON_FINITE")
        baseline_rule = self.make_engine([{"rule_id": "BASE", "conditions": {
            "field": "sbp", "operator": "<_formula", "formula": "0.7 * huyet_ap_tam_thu_nen",
        }}])
        self.assertIsNone(baseline_rule._eval_rule("BASE", {"sbp": 80}, {}, []))
        self.assertIs(baseline_rule._eval_rule(
            "BASE", {"sbp": 80, "huyet_ap_tam_thu_nen": 120}, {}, []
        ), True)

    def test_boolean_is_not_numeric_equal(self):
        engine = self.make_engine([{
            "rule_id": "BASE", "conditions": {"field": "x", "operator": "==", "value": 1},
        }])
        trace = []
        self.assertIsNone(engine._eval_rule("BASE", {"x": True}, {}, trace))
        self.assertEqual(trace[-1]["reason"], "INVALID_TYPE")

    def test_evaluation_state_is_local_and_input_is_not_mutated(self):
        engine = self.make_engine([{
            "rule_id": "BASE", "conditions": {"field": "x", "operator": ">=", "value": 1},
        }])
        data = {"x": 1, "untouched": ["value"]}
        original = {"x": 1, "untouched": ["value"]}
        first_trace = []
        second_trace = []
        self.assertIs(engine._eval_rule("BASE", data, {}, first_trace), True)
        self.assertIsNone(engine._eval_rule("BASE", {"x": None}, {}, second_trace))
        self.assertNotEqual(first_trace, second_trace)
        self.assertEqual(data, original)


class TestRuleSelection(RuleEngineTestCase):
    def test_priority_is_not_dependency_order(self):
        rules = [
            {"rule_id": "SHOCK", "priority": 1, "target_label": "Sốc",
             "conditions": {"ref_rule": "PV"}},
            {"rule_id": "PV", "priority": 2, "target_label": "Phản vệ",
             "conditions": {"field": "flag", "operator": "==", "value": True}},
        ]
        for ordered in (rules, list(reversed(rules))):
            result = self.make_engine(ordered).classify_patient({"flag": True})
            self.assertEqual(result["matched_rule_id"], "SHOCK")
            self.assertEqual(result["status"], "CLASSIFIED")
            self.assertEqual(result["rule_results"], {"PV": True, "SHOCK": True})

    def test_base_without_priority_is_evaluated_before_target_selection(self):
        engine = self.make_engine([
            {"rule_id": "TARGET", "target_label": "Kết luận", "priority": 1,
             "conditions": {"ref_rule": "BASE"}},
            {"rule_id": "BASE", "conditions": {"field": "flag", "operator": "==", "value": True}},
        ])
        result = engine.classify_patient({"flag": True})
        self.assertEqual(result["predicted_label"], "Kết luận")
        self.assertIs(result["rule_results"]["BASE"], True)

    def test_higher_priority_unknown_blocks_lower_true(self):
        engine = self.make_engine([
            {"rule_id": "HIGH", "target_label": "Nguy hiểm", "priority": 1,
             "conditions": {"field": "high", "operator": "==", "value": True}},
            {"rule_id": "LOW", "target_label": "Nhẹ", "priority": 2,
             "conditions": {"field": "low", "operator": "==", "value": True}},
        ])
        result = engine.classify_patient({"low": True})
        self.assertEqual(result["status"], "INSUFFICIENT_DATA")
        self.assertIsNone(result["predicted_label"])
        self.assertIsNone(result["matched_rule_id"])
        self.assertEqual(result["blocking_rule_ids"], ["HIGH"])
        self.assertEqual(result["missing_fields"], ["high"])

    def test_lower_priority_unknown_does_not_block_higher_true(self):
        engine = self.make_engine([
            {"rule_id": "HIGH", "target_label": "Nguy hiểm", "priority": 1,
             "conditions": {"field": "high", "operator": "==", "value": True}},
            {"rule_id": "LOW", "target_label": "Nhẹ", "priority": 2,
             "conditions": {"field": "low", "operator": "==", "value": True}},
        ])
        result = engine.classify_patient({"high": True})
        self.assertEqual(result["status"], "CLASSIFIED")
        self.assertEqual(result["predicted_label"], "Nguy hiểm")
        self.assertEqual(result["matched_rule_id"], "HIGH")
        self.assertEqual(result["blocking_rule_ids"], [])

    def test_same_priority_conflict_and_deterministic_same_pair_tie(self):
        conflict = self.make_engine([
            {"rule_id": "A", "target_label": "A", "priority": 1,
             "conditions": {"field": "x", "operator": "==", "value": True}},
            {"rule_id": "B", "target_label": "B", "priority": 1,
             "conditions": {"field": "y", "operator": "==", "value": True}},
        ]).classify_patient({"x": True, "y": True})
        self.assertEqual(conflict["status"], "NEEDS_REVIEW")
        self.assertIsNone(conflict["predicted_label"])
        self.assertIsNone(conflict["matched_rule_id"])

        same_pair = self.make_engine([
            {"rule_id": "Z", "target_label": "A", "priority": 1,
             "conditions": {"field": "x", "operator": "==", "value": True}},
            {"rule_id": "A", "target_label": "A", "priority": 1,
             "conditions": {"field": "y", "operator": "==", "value": True}},
        ]).classify_patient({"x": True, "y": True})
        self.assertEqual(same_pair["status"], "CLASSIFIED")
        self.assertEqual(same_pair["matched_rule_id"], "A")
        self.assertEqual(same_pair["matched_rule_ids"], ["A", "Z"])

        status_conflict = self.make_engine([
            {"rule_id": "A", "target_label": "Cùng nhãn", "priority": 1,
             "target_status": "CLASSIFIED",
             "conditions": {"field": "x", "operator": "==", "value": True}},
            {"rule_id": "B", "target_label": "Cùng nhãn", "priority": 1,
             "target_status": "INSUFFICIENT_DATA",
             "conditions": {"field": "y", "operator": "==", "value": True}},
        ]).classify_patient({"x": True, "y": True})
        self.assertEqual(status_conflict["status"], "NEEDS_REVIEW")
        self.assertIsNone(status_conflict["predicted_label"])

    def test_same_priority_unknown_that_can_change_conclusion_blocks(self):
        engine = self.make_engine([
            {"rule_id": "A", "target_label": "A", "priority": 1,
             "conditions": {"field": "x", "operator": "==", "value": True}},
            {"rule_id": "B", "target_label": "B", "priority": 1,
             "conditions": {"field": "y", "operator": "==", "value": True}},
        ])
        result = engine.classify_patient({"x": True})
        self.assertEqual(result["status"], "INSUFFICIENT_DATA")
        self.assertIsNone(result["predicted_label"])
        self.assertEqual(result["blocking_rule_ids"], ["B"])

    def test_same_priority_unknown_with_same_conclusion_does_not_block(self):
        engine = self.make_engine([
            {"rule_id": "A", "target_label": "A", "priority": 1,
             "conditions": {"field": "x", "operator": "==", "value": True}},
            {"rule_id": "B", "target_label": "A", "priority": 1,
             "conditions": {"field": "y", "operator": "==", "value": True}},
        ])
        result = engine.classify_patient({"x": True})
        self.assertEqual(result["status"], "CLASSIFIED")
        self.assertEqual(result["predicted_label"], "A")
        self.assertEqual(result["blocking_rule_ids"], [])

    def test_invalid_type_in_blocking_rule_requires_review(self):
        for invalid in ("not-a-number", float("inf")):
            with self.subTest(invalid=invalid):
                engine = self.make_engine([{
                    "rule_id": "A", "target_label": "A", "priority": 1,
                    "conditions": {"field": "x", "operator": ">=", "value": 1},
                }])
                result = engine.classify_patient({"x": invalid})
                self.assertEqual(result["status"], "NEEDS_REVIEW")
                self.assertEqual(result["blocking_rule_ids"], ["A"])

    def test_all_targets_false_is_unresolved(self):
        result = self.make_engine([{
            "rule_id": "A", "target_label": "A", "priority": 1,
            "conditions": {"field": "x", "operator": "==", "value": True},
        }]).classify_patient({"x": False})
        self.assertEqual(result["status"], "UNRESOLVED")
        self.assertEqual(result["predicted_label"], None)
        self.assertEqual(result["matched_rule_id"], None)
        self.assertEqual(result["priority"], 99)

    def test_true_target_can_set_nonclassified_status(self):
        result = self.make_engine([{
            "rule_id": "FOLLOWUP", "target_label": "Theo dõi", "priority": 1,
            "target_status": "INSUFFICIENT_DATA",
            "conditions": {"field": "flag", "operator": "==", "value": True},
        }]).classify_patient({"flag": True})
        self.assertEqual(result["status"], "INSUFFICIENT_DATA")
        self.assertIsNone(result["predicted_label"])
        self.assertEqual(result["matched_rule_id"], "FOLLOWUP")

    def test_project_shock_examples(self):
        engine = ClinicalRuleEngine("rules/phan_ve_rules.yaml")
        cases = [
            {"tuoi": 28, "huyet_ap_tam_thu_thap_nhat": 80,
             "yeu_to_nghi_ngo_pv_thuc_an": {"co_khong": "Có"},
             "trieu_chung_da_hien_tai_pv": {"danh_sach_chon": ["Sẩn phù"]},
             "trieu_chung_tuan_hoan_hien_tai_pv": {"danh_sach_chon": ["Tụt huyết áp / sốc"]}},
            {"tuoi": 5, "huyet_ap_tam_thu_thap_nhat": 75,
             "yeu_to_nghi_ngo_pv_thuoc": {"co_khong": "Có"},
             "trieu_chung_tuan_hoan_hien_tai_pv": {"danh_sach_chon": ["Ngất"]}},
        ]
        for data in cases:
            with self.subTest(age=data["tuoi"]):
                result = engine.classify_patient(data)
                self.assertEqual(result["matched_rule_id"], "R-SOC")
                self.assertEqual(result["predicted_label"], "Sốc phản vệ")

    def test_trace_does_not_include_record_values_and_repeat_is_deterministic(self):
        engine = ClinicalRuleEngine("rules/phan_ve_rules.yaml")
        data = {
            "tuoi": 28, "huyet_ap_tam_thu_thap_nhat": 80,
            "yeu_to_nghi_ngo_pv_thuc_an": {"co_khong": "Có"},
            "trieu_chung_da_hien_tai_pv": {"danh_sach_chon": ["Sẩn phù"]},
            "trieu_chung_tuan_hoan_hien_tai_pv": {"danh_sach_chon": ["Tụt huyết áp / sốc"]},
            "ten_benh_nhan": "PRIVATE-NAME-MARKER",
            "so_dien_thoai": "PRIVATE-PHONE-MARKER",
        }
        first = engine.classify_patient(data)
        second = engine.classify_patient(data)
        self.assertEqual(first, second)
        next_record = engine.classify_patient({"flag": False})
        fresh_result = ClinicalRuleEngine("rules/phan_ve_rules.yaml").classify_patient({"flag": False})
        self.assertEqual(next_record, fresh_result)
        self.assertEqual(len(first["rule_results"]), 5)
        self.assertEqual(first["rules_version"], "1.3.0")
        self.assertEqual(len(first["rules_sha256"]), 64)
        serialized = str(first)
        self.assertNotIn("PRIVATE-NAME-MARKER", serialized)
        self.assertNotIn("PRIVATE-PHONE-MARKER", serialized)

    def test_non_object_input_is_rejected_without_echoing_payload(self):
        engine = ClinicalRuleEngine("rules/phan_ve_rules.yaml")
        with self.assertRaises(ValueError):
            engine.classify_patient(["PRIVATE-MARKER"])
