import unittest
import copy
import json
from pathlib import Path
from unittest.mock import Mock

from jsonschema import Draft7Validator

from src.pipeline import classify_form, load_engines


class TestFormRouting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engines = load_engines()
        fixture = json.loads(Path("data/synthetic/rule_logic_cases.json").read_text(encoding="utf-8"))
        cls.cases = {case["id"]: case["du_lieu"] for case in fixture["cases"]}

    def test_selected_form_uses_only_its_engine(self):
        engines = {form: Mock() for form in ("phan_ve", "cap", "man")}
        patient = {"tuoi": 30}
        engines["man"].classify_patient.return_value = {"status": "CLASSIFIED"}

        result = classify_form("man", patient, engines)

        self.assertEqual(result, {"status": "CLASSIFIED"})
        engines["man"].classify_patient.assert_called_once_with(patient)
        engines["phan_ve"].classify_patient.assert_not_called()
        engines["cap"].classify_patient.assert_not_called()

    def test_unknown_form_is_rejected(self):
        with self.assertRaises(ValueError):
            classify_form("", {}, load_engines())

    def test_rule_sets_do_not_cross_forms(self):
        self.assertEqual(set(self.engines), {"phan_ve", "cap", "man"})
        self.assertIn("R-SOC", self.engines["phan_ve"]._rules_by_id)
        self.assertNotIn("R-SOC", self.engines["man"]._rules_by_id)
        self.assertNotIn("R-PV-THEODOI", self.engines["cap"]._rules_by_id)
        self.assertIn("R-DEFAULT", self.engines["man"]._rules_by_id)

    def test_csu_without_pv_fields_is_classified_only_by_chronic_rules(self):
        result = classify_form("man", self.cases["CSU-NO-PV"], self.engines)
        self.assertEqual(result["status"], "CLASSIFIED")
        self.assertTrue(result["matched_rule_id"].startswith("R-CSU"))
        self.assertNotIn("R-PV-THEODOI", result["rule_results"])

    def test_r01_with_low_pressure_is_shock(self):
        result = classify_form("phan_ve", self.cases["PV-07"], self.engines)
        self.assertEqual(result["matched_rule_id"], "R-SOC")
        self.assertIs(result["rule_results"]["R01-PV-KHONG-DI-NGUYEN"], True)

    def test_shock_age_and_pressure_boundaries(self):
        for age, threshold in ((0, 70), (0.05, 70), (0.999, 70),
                               (1, 72), (10.5, 91), (11, 90), (17.5, 90), (18, 90)):
            for pressure, shock in ((threshold - 0.1, True), (threshold, False),
                                    (threshold + 0.1, False)):
                with self.subTest(age=age, pressure=pressure):
                    patient = copy.deepcopy(self.cases["PV-07"])
                    patient["tuoi"] = age
                    patient["huyet_ap_tam_thu_thap_nhat"] = pressure
                    result = classify_form("phan_ve", patient, self.engines)
                    self.assertEqual(result["matched_rule_id"] == "R-SOC", shock)

    def test_follow_up_requires_known_negative_rules(self):
        patient = copy.deepcopy(self.cases["PV-01"])
        for field in ("yeu_to_nghi_ngo_pv_thuc_an", "yeu_to_nghi_ngo_pv_thuoc",
                      "yeu_to_nghi_ngo_pv_con_trung_dot", "yeu_to_nghi_ngo_pv_khac"):
            patient[field] = {"co_khong": "Không"}
        patient["trieu_chung_da_hien_tai_pv"] = {"danh_sach_chon": []}
        result = classify_form("phan_ve", patient, self.engines)
        self.assertEqual(result["status"], "THEODOIPV")
        self.assertEqual(result["matched_rule_id"], "R-PV-THEODOI")
        self.assertEqual(result["missing_fields"], [])

    def test_missing_shock_or_symptom_data_never_becomes_follow_up(self):
        for field in ("tuoi", "huyet_ap_tam_thu_thap_nhat",
                      "trieu_chung_ho_hap_hien_tai_pv"):
            with self.subTest(field=field):
                patient = copy.deepcopy(self.cases["PV-07"])
                patient.pop(field, None)
                result = classify_form("phan_ve", patient, self.engines)
                self.assertEqual(result["status"], "INSUFFICIENT_DATA")
                self.assertTrue(any(path == field or path.startswith(field + ".")
                                    for path in result["missing_fields"]))
                self.assertNotEqual(result["matched_rule_id"], "R-PV-THEODOI")

    def test_acute_severe_branches_and_normal(self):
        for case_id, rule_id in (("CAP-NANG-NGUA", "R01-CAP-NANG-NGUA"),
                                 ("CAP-NANG-PHUMACH", "R02-CAP-NANG-PHUMACH"),
                                 ("CAP-NANG-CHITIET", "R02-CAP-NANG-PHUMACH"),
                                 ("CAP-NANG-BSA", "R03-CAP-NANG-CONLAI"),
                                 ("CAP-THUONG-OBJECT", "R01-CAP-THUONG")):
            with self.subTest(case=case_id):
                result = classify_form("cap", self.cases[case_id], self.engines)
                self.assertEqual(result["matched_rule_id"], rule_id)

    def test_acute_unknown_and_failed_gate_do_not_classify_normal(self):
        patient = copy.deepcopy(self.cases["CAP-THUONG-OBJECT"])
        patient.pop("dau_hieu_nang_chi_tiet")
        result = classify_form("cap", patient, self.engines)
        self.assertEqual(result["status"], "INSUFFICIENT_DATA")
        self.assertIs(result["rule_results"]["R01-CAP-THUONG"], None)
        patient = copy.deepcopy(self.cases["CAP-NANG-BSA"])
        patient["anh_san_phu"] = "Không"
        result = classify_form("cap", patient, self.engines)
        self.assertEqual(result["status"], "UNRESOLVED")
        self.assertFalse(any(rule.startswith("R0") and "CAP" in rule
                             for rule in result["matched_rule_ids"]))

    def test_acute_other_severe_branch_requires_skin_wheal(self):
        patient = copy.deepcopy(self.cases["CAP-NANG-BSA"])
        patient["trieu_chung_da_hien_tai"]["danh_sach_chon"] = []
        result = classify_form("cap", patient, self.engines)
        self.assertIs(result["rule_results"]["R03-CAP-NANG-CONLAI"], False)

    def test_schema_shaped_acute_record_reaches_rule(self):
        patient = copy.deepcopy(self.cases["CAP-THUONG-OBJECT"])
        patient.update({"ma_benh_nhan": "SYN-001", "ho_ten": "Synthetic",
                        "so_dien_thoai": "0000000000",
                        "chan_doan_xac_dinh_cap": {"danh_sach_chon": "Mày đay cấp thông thường"}})
        patient["so_luong_san_phu"] = "20-50 nốt"
        patient["muc_do_lan_rong_va_phan_bo_ton_thuong"]["muc_do_lan_rong"] = "≤50% BSA"
        schema = json.loads(Path("schema/cap_schema.json").read_text(encoding="utf-8"))
        self.assertEqual(list(Draft7Validator(schema).iter_errors(patient)), [])
        result = classify_form("cap", patient, self.engines)
        self.assertEqual(result["matched_rule_id"], "R01-CAP-THUONG")

    def test_schema_shaped_anaphylaxis_record_reaches_rule(self):
        patient = copy.deepcopy(self.cases["PV-07"])
        patient.update({"ma_benh_nhan": "SYN-002", "ho_ten": "Synthetic",
                        "so_dien_thoai": "0000000000"})
        schema = json.loads(Path("schema/phan_ve_schema.json").read_text(encoding="utf-8"))
        self.assertEqual(list(Draft7Validator(schema).iter_errors(patient)), [])
        result = classify_form("phan_ve", patient, self.engines)
        self.assertEqual(result["matched_rule_id"], "R-SOC")
