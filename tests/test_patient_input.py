import copy
import json
import unittest
from pathlib import Path

from src.pipeline import load_engines


class TestPatientInput(unittest.TestCase):
    def api(self):
        try:
            from src import patient_input
        except ImportError:
            self.fail("Missing engine input and RAW mapper module")
        return patient_input

    def test_field_specs_cover_formula_dependencies_and_array_objects(self):
        api = self.api()
        engines = load_engines()
        fields = {f["path"]: f for f in api.engine_fields("phan_ve", engines["phan_ve"])}
        self.assertEqual(fields["huyet_ap_tam_thu_nen"]["kind"], "number")
        self.assertEqual(fields["tuoi"]["kind"], "number")
        fields = {f["path"]: f for f in api.engine_fields("cap", engines["cap"])}
        self.assertEqual(fields["dac_diem_san_phu_cap"]["item_field"], "dang_ton_thuong")
        self.assertIn("Ngứa nhiều", fields["trieu_chung_da_hien_tai.danh_sach_chon"]["choices"])

    def test_blank_template_never_asserts_negative_or_fabricated_measurements(self):
        api = self.api()
        for form, engine in load_engines().items():
            template = api.empty_patient(form, engine)
            self.assertIsNone(template["tuoi"] if "tuoi" in template else None)
            self.assertFalse(any(v is False or v == [] or v == 0 for v in template.values()))
            self.assertEqual(engine.classify_patient(template)["status"], "INSUFFICIENT_DATA")

    def test_merge_form_preserves_other_data_and_array_object_attributes(self):
        api = self.api()
        fields = api.engine_fields("cap", load_engines()["cap"])
        original = {"custom_note": "synthetic", "dac_diem_san_phu_cap": [
            {"dang_ton_thuong": "Hình tròn (bờ rõ)", "kich_thuoc_mm": 7}]}
        before = copy.deepcopy(original)
        values = {f["path"]: None for f in fields}
        values["dac_diem_san_phu_cap"] = ["Hình tròn (bờ rõ)"]
        values["trieu_chung_da_hien_tai.danh_sach_chon"] = ["Sẩn phù"]
        result = api.merge_form(original, fields, values)
        self.assertEqual(original, before)
        self.assertEqual(result["custom_note"], "synthetic")
        self.assertEqual(result["dac_diem_san_phu_cap"][0]["kich_thuoc_mm"], 7)
        self.assertEqual(result["trieu_chung_da_hien_tai"]["danh_sach_chon"], ["Sẩn phù"])

    def raw(self):
        return {
            "hanh_chinh": [
                {"MA_BN_AN_DANH": "SYN-A", "TUOI_KHI_VAO_VIEN": 30, "GIOI_TINH": "Nữ",
                 "IN_TIME": "2025-01-01 09:00:00", "OUT_TIME": "2025-01-02 18:00:00"},
                {"MA_BN_AN_DANH": "SYN-A", "TUOI_KHI_VAO_VIEN": 31, "GIOI_TINH": "Nữ",
                 "IN_TIME": "2026-01-01 09:00:00", "OUT_TIME": "2026-01-02 18:00:00"},
                {"MA_BN_AN_DANH": "SYN-B", "TUOI_KHI_VAO_VIEN": 40,
                 "IN_TIME": "2026-01-01 09:00:00", "OUT_TIME": "2026-01-02 18:00:00"}],
            "dhst": [
                {"MA_BN_AN_DANH": "SYN-A", "EXECUTE_TIME": "2025-01-01 10:00:00", "BLOOD_PRESSURE_MAX": 60},
                {"MA_BN_AN_DANH": "SYN-A", "EXECUTE_TIME": "2026-01-01 10:00:00", "BLOOD_PRESSURE_MAX": 110},
                {"MA_BN_AN_DANH": "SYN-B", "EXECUTE_TIME": "2026-01-01 10:00:00", "BLOOD_PRESSURE_MAX": 50}],
            "xet_nghiem": [
                {"MA_BN_AN_DANH": "SYN-A", "TDL_INTRUCTION_TIME": "2026-01-01 11:00:00",
                 "TEST_INDEX_CODE": "SHM0027", "TEST_INDEX_NAME": "IgE", "TEST_INDEX_UNIT_NAME": "IU/mL", "VALUE": "35"}],
            "chan_doan": [{"MA_BN_AN_DANH": "SYN-A", "IN_TIME": "2026-01-01 09:00:00", "ICD_NAME": "Synthetic diagnosis"}],
            "cdha_tdcn": [], "thuoc": [],
        }

    def test_raw_mapping_is_per_patient_and_visit_without_diagnosis_leakage(self):
        api = self.api()
        raw = self.raw()
        before = copy.deepcopy(raw)
        mapped = api.map_raw(raw, "SYN-A", 1, "phan_ve", load_engines()["phan_ve"])
        self.assertEqual(mapped["du_lieu"]["tuoi"], 31)
        self.assertEqual(mapped["du_lieu"]["huyet_ap_tam_thu_thap_nhat"], 110)
        self.assertEqual(mapped["du_lieu"]["ma_benh_nhan"], "benh_nhan_1")
        self.assertNotIn("ICD_NAME", json.dumps(mapped["du_lieu"]))
        self.assertIsNone(mapped["du_lieu"]["huyet_ap_tam_thu_nen"])
        self.assertIsNone(mapped["du_lieu"]["yeu_to_nghi_ngo_pv_thuc_an"]["co_khong"])
        self.assertEqual(raw, before)
        mapped_b = api.map_raw(raw, "SYN-B", 0, "phan_ve", load_engines()["phan_ve"])
        self.assertIn({"field": "tuoi", "source": "hanh_chinh[2].TUOI_KHI_VAO_VIEN"}, mapped_b["provenance"])

    def test_ige_requires_code_confirmation_and_correct_unit(self):
        api = self.api()
        engine = load_engines()["man"]
        raw = self.raw()
        mapped = api.map_raw(raw, "SYN-A", 1, "man", engine)
        self.assertIsNone(mapped["du_lieu"]["ige_toan_phan"])
        self.assertTrue(mapped["candidates"])
        mapped = api.map_raw(raw, "SYN-A", 1, "man", engine, confirm_ige=True)
        self.assertEqual(mapped["du_lieu"]["ige_toan_phan"], 35)
        raw["xet_nghiem"][0]["TEST_INDEX_UNIT_NAME"] = "unconfirmed-unit"
        mapped = api.map_raw(raw, "SYN-A", 1, "man", engine, confirm_ige=True)
        self.assertIsNone(mapped["du_lieu"]["ige_toan_phan"])

    def test_ambiguous_dates_invalid_numbers_and_conflicting_tests_stay_missing(self):
        api = self.api()
        raw = self.raw()
        raw["hanh_chinh"][1]["IN_TIME"] = "2026-01-01"
        raw["dhst"][1]["BLOOD_PRESSURE_MAX"] = True
        engine = load_engines()["phan_ve"]
        mapped = api.map_raw(raw, "SYN-A", 1, "phan_ve", engine, confirm_ige=True)
        self.assertIsNone(mapped["du_lieu"]["huyet_ap_tam_thu_thap_nhat"])
        raw = self.raw()
        raw["hanh_chinh"].append(copy.deepcopy(raw["hanh_chinh"][1]))
        mapped = api.map_raw(raw, "SYN-A", 1, "phan_ve", engine)
        self.assertIsNone(mapped["du_lieu"]["huyet_ap_tam_thu_thap_nhat"])
        raw = self.raw()
        raw["xet_nghiem"].append(dict(raw["xet_nghiem"][0], VALUE="50"))
        mapped = api.map_raw(raw, "SYN-A", 1, "man", load_engines()["man"], confirm_ige=True)
        self.assertIsNone(mapped["du_lieu"]["ige_toan_phan"])

    def test_raw_shape_and_selection_are_checked(self):
        api = self.api()
        self.assertFalse(api.is_raw({"tuoi": 30}))
        self.assertTrue(api.is_raw(self.raw()))
        for patient, visit in (("missing", 0), ("SYN-A", -1), ("SYN-A", 9)):
            with self.subTest(patient=patient, visit=visit), self.assertRaises(ValueError):
                api.map_raw(self.raw(), patient, visit, "man", load_engines()["man"])
        invalid = self.raw()
        invalid["dhst"][0].pop("MA_BN_AN_DANH")
        with self.assertRaises(ValueError):
            api.raw_patients(invalid)

    def test_oversized_or_nonfinite_raw_numbers_do_not_crash_or_become_measurements(self):
        api = self.api()
        raw = self.raw()
        raw["hanh_chinh"][1]["TUOI_KHI_VAO_VIEN"] = 10 ** 400
        raw["dhst"][1]["BLOOD_PRESSURE_MAX"] = float("inf")
        mapped = api.map_raw(raw, "SYN-A", 1, "phan_ve", load_engines()["phan_ve"])
        self.assertIsNone(mapped["du_lieu"]["tuoi"])
        self.assertIsNone(mapped["du_lieu"]["huyet_ap_tam_thu_thap_nhat"])


if __name__ == "__main__":
    unittest.main()
