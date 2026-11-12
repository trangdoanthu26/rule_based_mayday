import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class TestPatientEntryUI(unittest.TestCase):
    def start(self):
        app = AppTest.from_file(str(ROOT / "main.py"), default_timeout=20).run()
        self.assertFalse(app.exception)
        self.assertIn("Nhập bệnh án", [tab.label for tab in app.tabs])
        return app

    def key(self, form, path):
        return f"entry_value::{form}:{path}"

    def test_manual_empty_form_keeps_missing_instead_of_false(self):
        app = self.start()
        app.radio(key="source_mode").set_value("Nhập theo mẫu engine").run()
        self.assertIsNone(app.number_input(key=self.key("phan_ve", "tuoi")).value)
        app.button(key="apply_engine_form").click().run()
        app.button(key="classify").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["result"]["status"], "INSUFFICIENT_DATA")
        self.assertIsNone(json.loads(app.session_state["patient_json"])["yeu_to_nghi_ngo_pv_thuc_an"]["co_khong"])

    def test_panel_handles_numbers_outside_widget_limits_without_changing_json(self):
        app = self.start()
        app.toggle(key="toggle_compare_json").set_value(True).run()
        for data in ({"tuoi": 10 ** 400}, {"trieu_chung_tieu_hoa_hien_tai_pv": {"non_so_lan": 10 ** 20}}):
            with self.subTest(field=list(data)):
                app.text_area(key="patient_json").set_value(json.dumps(data)).run()
                self.assertFalse(app.exception)
                self.assertEqual(json.loads(app.session_state["patient_json"]), data)

    def test_manual_panel_builds_r01_shock_input_and_downloadable_json(self):
        app = self.start()
        app.radio(key="source_mode").set_value("Nhập theo mẫu engine").run()
        for field in ("yeu_to_nghi_ngo_pv_thuc_an", "yeu_to_nghi_ngo_pv_thuoc",
                      "yeu_to_nghi_ngo_pv_con_trung_dot", "yeu_to_nghi_ngo_pv_khac"):
            app.selectbox(key=self.key("phan_ve", field + ".co_khong")).select("Không")
        app.number_input(key=self.key("phan_ve", "tuoi")).set_value(30.0)
        app.number_input(key=self.key("phan_ve", "huyet_ap_tam_thu_thap_nhat")).set_value(80.0)
        app.multiselect(key=self.key("phan_ve", "trieu_chung_da_hien_tai_pv.danh_sach_chon")).set_value(["Sẩn phù"])
        app.multiselect(key=self.key("phan_ve", "trieu_chung_ho_hap_hien_tai_pv.danh_sach_chon")).set_value(["Khó thở"])
        app.button(key="apply_engine_form").click().run()
        app.button(key="classify").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["result"]["matched_rule_id"], "R-SOC")
        app.selectbox(key="form_type").select("man").run()
        self.assertIsNone(app.session_state["result"])
        self.assertIsNone(app.number_input(key=self.key("man", "tuoi")).value)

    def test_acute_array_object_input_reaches_severe_rule(self):
        app = self.start()
        app.radio(key="source_mode").set_value("Nhập theo mẫu engine").run()
        app.selectbox(key="form_type").select("cap").run()
        for field in ("hien_tai_co_san_phu", "anh_san_phu"):
            app.selectbox(key=self.key("cap", field)).select("Có")
        app.number_input(key=self.key("cap", "thoi_gian_khoi_phat_gio")).set_value(24.0)
        app.multiselect(key=self.key("cap", "dac_diem_san_phu_cap")).set_value(["Hình tròn (bờ rõ)"])
        app.multiselect(key=self.key("cap", "trieu_chung_da_hien_tai.danh_sach_chon")).set_value(["Ngứa nhiều"])
        app.button(key="apply_engine_form").click().run()
        app.button(key="classify").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["result"]["matched_rule_id"], "R01-CAP-NANG-NGUA")
        self.assertEqual(json.loads(app.session_state["patient_json"])["dac_diem_san_phu_cap"],
                         [{"dang_ton_thuong": "Hình tròn (bờ rõ)"}])

    def test_raw_upload_maps_selected_visit_and_preserves_manual_edits(self):
        raw = {"hanh_chinh": [
            {"MA_BN_AN_DANH": "SYN", "TUOI_KHI_VAO_VIEN": 30, "IN_TIME": "2025-01-01 10:00:00", "OUT_TIME": "2025-01-02 10:00:00"},
            {"MA_BN_AN_DANH": "SYN", "TUOI_KHI_VAO_VIEN": 31, "IN_TIME": "2026-01-01 10:00:00", "OUT_TIME": "2026-01-02 10:00:00"}],
            "dhst": [{"MA_BN_AN_DANH": "SYN", "EXECUTE_TIME": "2026-01-01 12:00:00", "BLOOD_PRESSURE_MAX": 115}],
            "xet_nghiem": [], "chan_doan": [], "cdha_tdcn": [], "thuoc": []}
        uploaded = SimpleNamespace(name="synthetic-raw.json", getvalue=lambda: json.dumps(raw).encode())
        app = self.start()
        with patch("streamlit.delta_generator.DeltaGenerator.file_uploader", return_value=uploaded):
            app.radio(key="source_mode").set_value("Tải file mới (.json, .csv)").run()
            app.selectbox(key="raw_visit").select(1).run()
            self.assertFalse(app.exception)
            data = json.loads(app.session_state["patient_json"])
            self.assertEqual(data["tuoi"], 31)
            self.assertEqual(data["huyet_ap_tam_thu_thap_nhat"], 115)
            self.assertNotIn("hanh_chinh", data)
            app.toggle(key="toggle_compare_json").set_value(True).run()
            app.text_area(key="patient_json").set_value('{"tuoi": 45}').run()
            app.toggle(key="toggle_compare_json").set_value(False).run()
            app.run()
            self.assertEqual(json.loads(app.session_state["patient_json"]), {"tuoi": 45})
            app.toggle(key="toggle_compare_json").set_value(True).run()
            self.assertEqual(json.loads(app.text_area(key="patient_json").value), {"tuoi": 45})
            app.button(key="classify").click().run()
            self.assertEqual(json.loads(app.session_state["patient_json"]), {"tuoi": 45})
            app.selectbox(key="raw_visit").select(0).run()
            self.assertEqual(json.loads(app.session_state["patient_json"])["tuoi"], 30)
            self.assertIsNone(app.session_state["result"])

    def test_manual_input_survives_json_editor_toggle_and_classification(self):
        app = self.start()
        app.radio(key="source_mode").set_value("Nhập theo mẫu engine").run()
        app.number_input(key=self.key("phan_ve", "tuoi")).set_value(37.0)
        app.button(key="apply_engine_form").click().run()
        expected = json.loads(app.session_state["patient_json"])
        self.assertEqual(expected["tuoi"], 37)
        app.toggle(key="toggle_compare_json").set_value(True).run()
        self.assertEqual(json.loads(app.text_area(key="patient_json").value), expected)
        app.toggle(key="toggle_compare_json").set_value(False).run()
        app.run()
        app.button(key="classify").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(json.loads(app.session_state["patient_json"]), expected)
        self.assertEqual(app.session_state["result"]["status"], "INSUFFICIENT_DATA")
        app.toggle(key="toggle_compare_json").set_value(True).run()
        self.assertEqual(json.loads(app.text_area(key="patient_json").value), expected)

    def test_raw_ige_confirmation_is_explicit_and_resets_with_form(self):
        raw = {"hanh_chinh": [{"MA_BN_AN_DANH": "SYN", "TUOI_KHI_VAO_VIEN": 30,
               "IN_TIME": "2026-01-01 10:00:00", "OUT_TIME": "2026-01-02 10:00:00"}],
               "xet_nghiem": [{"MA_BN_AN_DANH": "SYN", "TEST_INDEX_CODE": "SHM0027",
                    "TEST_INDEX_NAME": "IgE", "TEST_INDEX_UNIT_NAME": "IU/mL", "VALUE": "35",
                    "TDL_INTRUCTION_TIME": "2026-01-01 12:00:00"}],
               "dhst": [], "chan_doan": [], "cdha_tdcn": [], "thuoc": []}
        uploaded = SimpleNamespace(name="benh_nhan_8.json", getvalue=lambda: json.dumps(raw).encode())
        app = self.start()
        app.selectbox(key="form_type").select("man").run()
        with patch("streamlit.delta_generator.DeltaGenerator.file_uploader", return_value=uploaded):
            app.radio(key="source_mode").set_value("Tải file mới (.json, .csv)").run()
            data = json.loads(app.session_state["patient_json"])
            self.assertEqual(data["ma_benh_nhan"], "benh_nhan_8")
            self.assertIsNone(data["ige_toan_phan"])
            app.checkbox(key="raw_ige_confirm").check().run()
            self.assertFalse(app.exception)
            self.assertEqual(json.loads(app.session_state["patient_json"])["ige_toan_phan"], 35)
            app.selectbox(key="form_type").select("phan_ve").run()
            self.assertFalse(app.checkbox(key="raw_ige_confirm").value)
            self.assertIsNone(json.loads(app.session_state["patient_json"]).get("ige_toan_phan_uiml"))


if __name__ == "__main__":
    unittest.main()
