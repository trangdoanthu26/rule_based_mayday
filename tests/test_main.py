import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

import main as demo


ROOT = Path(__file__).resolve().parents[1]


class TestStreamlitDemo(unittest.TestCase):
    def test_json_editor_and_preview_share_the_clinical_tab(self):
        app = self.start_app()
        self.assertEqual([tab.label for tab in app.tabs],
                         ["Bệnh án & kết quả", "Logic suy luận", "Bảng quy tắc & Mức ưu tiên"])
        self.assertEqual(len(app.tabs[0].text_area), 1)
        self.assertEqual(len(app.tabs[0].columns[0].get("html")), 1)
        app.button(key="classify").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["result"]["predicted_label"], "Phản vệ")
        self.assertTrue(any(item.value == "**Trạng thái:** ĐÃ PHÂN LOẠI"
                            for item in app.tabs[0].markdown))

    def test_highlight_includes_referenced_rules_and_clears_after_edit(self):
        app = self.start_app()
        app.selectbox(key="form_type").select("man").run()
        app.selectbox(key="case_id").select("CSU-T1-GD1").run()
        app.button(key="classify").click().run()
        html = app.get("html")[0].proto.body
        self.assertIn('data-field="asst_ket_qua" data-evidence="matched"', html)
        self.assertIn('data-field="ige_khang_il24_ket_qua" data-evidence="matched"', html)
        self.assertNotIn('data-field="da_ve_noi_ket_qua" data-evidence="matched"', html)
        app.text_area(key="patient_json").set_value('{"tuoi": 47}').run()
        self.assertIsNone(app.session_state["result"])
        self.assertNotIn('data-evidence="matched">', app.get("html")[0].proto.body)

    def test_missing_fields_are_highlighted_without_filling_input(self):
        app = self.start_app()
        app.text_area(key="patient_json").set_value('{"tuoi": 47}').run()
        app.button(key="classify").click().run()
        html = app.get("html")[0].proto.body
        self.assertIn('data-field="huyet_ap_tam_thu_thap_nhat" data-evidence="missing"', html)
        self.assertIn("Chưa có trong JSON", html)
        self.assertEqual(json.loads(app.session_state["patient_json"]), {"tuoi": 47})

    def test_patient_preview_preserves_values_and_escapes_untrusted_html(self):
        renderer = getattr(demo, "patient_html", None)
        self.assertTrue(callable(renderer), "Cần bản bệnh án HTML bên cạnh JSON")
        preview = renderer({
            "tuoi": 30,
            "trieu_chung_da_hien_tai_pv": {"danh_sach_chon": ["Sẩn phù", "<img src=x onerror=alert(1)>"]},
            "asst_ket_qua": None, "test_unknown": "unknown", "test_na": "N/A",
            "stella_dat": True,
            "<script>field</script>": False,
        })
        self.assertIn("Tuổi", preview)
        self.assertIn("Sẩn phù", preview)
        self.assertIn("Triệu chứng da đợt hiện tại (phản vệ)", preview)
        self.assertIn("Đạt tiêu chuẩn Stella", preview)
        self.assertIn("Chưa cung cấp", preview)
        self.assertIn("Không rõ", preview)
        self.assertIn("Không áp dụng", preview)
        self.assertNotIn("<img", preview)
        self.assertNotIn("<script>", preview)
        self.assertIn("&lt;img", preview)

    def test_doctor_result_and_preview_follow_edited_json(self):
        app = self.start_app()
        app.selectbox(key="case_id").select("PV-01").run()
        app.button(key="classify").click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any(item.value == "KẾT LUẬN: PHẢN VỆ" for item in app.subheader))
        self.assertTrue(any(item.value == "**Trạng thái:** ĐÃ PHÂN LOẠI" for item in app.markdown))
        self.assertTrue(any(item.value == "Mức ưu tiên: 2" for item in app.caption))
        self.assertFalse(any("Có nhãn theo YAML hiện tại" in item.value for item in app.info))
        app.text_area(key="patient_json").set_value('{"tuoi": 47, "huyet_ap_tam_thu_nen": null}').run()
        self.assertFalse(app.exception)
        self.assertIsNone(app.session_state["result"])
        html = app.get("html")[0].proto.body
        self.assertIn("47", html)
        self.assertIn("Chưa cung cấp", html)
        app.text_area(key="patient_json").set_value("{").run()
        self.assertFalse(app.get("html"))
        self.assertTrue(any("Không thể hiển thị bệnh án" in item.value for item in app.warning))

    def start_app(self):
        return AppTest.from_file(str(ROOT / "main.py"), default_timeout=15).run()

    def test_shock_and_only_selected_form_layers_are_displayed(self):
        app = self.start_app()
        app.selectbox(key="case_id").select("SOC-NEN-NOTNEEDED").run()
        app.button(key="classify").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["result"]["matched_rule_id"], "R-SOC")
        self.assertEqual(app.session_state["result"]["predicted_label"], "Sốc phản vệ")
        self.assertEqual(len(app.selectbox(key="output_label").options), 4)
        self.assertTrue(any("T1" in item.label for item in app.expander))
        self.assertFalse(any("T6" in item.label for item in app.expander))

    def test_csu_and_cindu_use_the_real_engine(self):
        app = self.start_app()
        app.selectbox(key="form_type").select("man").run()
        for case_id, expected_rule in (
            ("CSU-T1-GD1", "R-CSU-T1-01"),
            ("CINDU-da_ve_noi", "R-CindU-01"),
            ("CINDU-TIE", None),
        ):
            with self.subTest(case=case_id):
                app.selectbox(key="case_id").select(case_id).run()
                app.button(key="classify").click().run()
                self.assertFalse(app.exception)
                self.assertEqual(app.session_state["result"]["matched_rule_id"], expected_rule)
        self.assertEqual(app.session_state["result"]["status"], "NEEDS_REVIEW")

    def test_wrong_pressure_type_is_reported_without_crashing_app(self):
        app = self.start_app()
        app.selectbox(key="case_id").select("SOC-MISSING-80").run()
        app.button(key="classify").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["result"]["status"], "NEEDS_REVIEW")
        self.assertIsNone(app.session_state["run_error"])

    def test_json_envelope_does_not_leak_expected_label_into_inference(self):
        app = self.start_app()
        app.selectbox(key="form_type").select("man").run()
        fixture = json.loads((ROOT / "data/synthetic/rule_logic_cases.json").read_text(encoding="utf-8"))
        case = next(case for case in fixture["cases"] if case["id"] == "CSU-T1-GD1")
        app.text_area(key="patient_json").set_value(json.dumps({
            "du_lieu": case["du_lieu"], "nhan": "Sốc phản vệ",
            "expected_engine": {"predicted_label": "Sốc phản vệ"},
        })).run()
        app.button(key="classify").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["result"]["predicted_label"], "Mày đay CSU type 1")

    def test_invalid_json_and_changed_input_clear_old_result(self):
        app = self.start_app()
        app.button(key="classify").click().run()
        self.assertIsNotNone(app.session_state["result"])
        for text in ("{", "[]", '{"du_lieu": []}', '{"tuoi": NaN}'):
            with self.subTest(text=text):
                app.text_area(key="patient_json").set_value(text).run()
                self.assertIsNone(app.session_state["result"])
                app.button(key="classify").click().run()
                self.assertFalse(app.exception)
                self.assertIsNone(app.session_state["result"])
                self.assertIn("JSON không hợp lệ", app.session_state["run_error"])
                self.assertTrue(any("JSON không hợp lệ" in message.value for message in app.error))

    def test_acute_normal_catalog_classifies_schema_shaped_case(self):
        app = self.start_app()
        app.selectbox(key="form_type").select("cap").run()
        app.selectbox(key="output_label").select("Mày đay cấp thông thường").run()
        app.button(key="classify").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["result"]["matched_rule_id"], "R01-CAP-THUONG")

    def test_form_specific_scope_is_visible_before_classification(self):
        app = self.start_app()
        self.assertEqual(app.selectbox(key="form_type").value, "phan_ve")
        self.assertTrue(any("Cách đọc kết quả" in item.label for item in app.expander))

    def test_selected_case_issue_has_an_explanation(self):
        app = self.start_app()
        app.selectbox(key="form_type").select("man").run()
        app.selectbox(key="case_id").select("CSU-STELLA-False-39.9").run()
        messages = "\n".join(message.value for message in app.warning)
        self.assertIn("F-08", messages)
        self.assertIn("Stella", messages)
        self.assertIn("IgE", messages)

    def test_boolean_pressure_error_is_highlighted_for_edited_json(self):
        app = self.start_app()
        fixture = json.loads((ROOT / "data/synthetic/rule_logic_cases.json").read_text(encoding="utf-8"))
        data = next(case["du_lieu"] for case in fixture["cases"] if case["id"] == "PV-01")
        data["huyet_ap_tam_thu_thap_nhat"] = True
        app.text_area(key="patient_json").set_value(json.dumps(data)).run()
        app.button(key="classify").click().run()
        self.assertFalse(app.exception)
        self.assertNotEqual(app.session_state["result"]["matched_rule_id"], "R-SOC")
        self.assertEqual(app.session_state["result"]["status"], "NEEDS_REVIEW")
        self.assertTrue(any("đã khác ca gốc" in message.value for message in app.warning))

    def test_status_explanation_and_conflict_warning_are_visible(self):
        app = self.start_app()
        app.selectbox(key="form_type").select("man").run()
        app.selectbox(key="case_id").select("CINDU-TIE").run()
        app.button(key="classify").click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any("CẦN RÀ SOÁT" in message.value and "kết luận" in message.value
                            for message in app.error))


    def test_uploaded_json_uses_selected_engine_and_preserves_editor_changes(self):
        fixture = json.loads((ROOT / "data/synthetic/rule_logic_cases.json").read_text(encoding="utf-8"))
        data = next(case["du_lieu"] for case in fixture["cases"] if case["id"] == "CSU-NO-PV")
        envelope = {"du_lieu": data, "form_type": "phan_ve",
                    "nhan": "Sốc phản vệ", "expected_engine": {"status": "CLASSIFIED"}}
        uploaded = SimpleNamespace(
            name="synthetic-man.json",
            getvalue=lambda: json.dumps(envelope).encode("utf-8"),
        )
        app = self.start_app()
        app.selectbox(key="form_type").select("man").run()
        with patch("streamlit.delta_generator.DeltaGenerator.file_uploader", return_value=uploaded):
            app.radio(key="source_mode").set_value("Tải file mới (.json, .csv)").run()
            self.assertFalse(app.exception)
            self.assertEqual(json.loads(app.session_state["patient_json"]), data)
            app.button(key="classify").click().run()
            self.assertFalse(app.exception)
            result = app.session_state["result"]
            self.assertEqual(result["predicted_label"], "Mày đay CSU unknown")
            self.assertNotIn("R-PV-THEODOI", result["rule_results"])
            self.assertNotIn("R-SANGLOC-CAP", result["rule_results"])
            app.text_area(key="patient_json").set_value('{"tuoi": 47}').run()
            app.button(key="classify").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(json.loads(app.session_state["patient_json"]), {"tuoi": 47})
            self.assertEqual(app.session_state["result"]["status"], "INSUFFICIENT_DATA")
            app.selectbox(key="form_type").select("phan_ve").run()
            self.assertIsNone(app.session_state["result"])
            app.button(key="classify").click().run()
            self.assertEqual(app.session_state["result"]["status"], "INSUFFICIENT_DATA")
            self.assertTrue(app.session_state["result"]["missing_fields"])
            self.assertNotIn("R-CSU-00", app.session_state["result"]["rule_results"])
        app.radio(key="source_mode").set_value("Ca giả định mẫu").run()
        self.assertEqual(app.session_state["patient_json"],
                         json.dumps(demo.filter_patient_by_engine(fixture["cases"][0]["du_lieu"], demo.load_engines()["phan_ve"]), ensure_ascii=False, indent=2))
        self.assertIsNone(app.session_state["result"])

    def test_invalid_upload_clears_previous_result_and_patient(self):
        app = self.start_app()
        app.button(key="classify").click().run()
        self.assertIsNotNone(app.session_state["result"])
        uploaded = SimpleNamespace(name="synthetic-invalid.json", getvalue=lambda: b'{"du_lieu": []}')
        with patch("streamlit.delta_generator.DeltaGenerator.file_uploader", return_value=uploaded):
            app.radio(key="source_mode").set_value("Tải file mới (.json, .csv)").run()
            self.assertFalse(app.exception)
            self.assertIsNone(app.session_state["result"])
            self.assertEqual(app.session_state["patient_json"], "")
            app.button(key="classify").click().run()
            self.assertIsNone(app.session_state["result"])
            self.assertIn("JSON không hợp lệ", app.session_state["run_error"])

    def test_csv_upload_preserves_scalar_types_and_selected_form(self):
        self.assertEqual(demo.parse_csv_patient(b"tuoi,stella_dat,ghi_chu\n10.5,true,synthetic\n"),
                         {"tuoi": 10.5, "stella_dat": True, "ghi_chu": "synthetic"})
        for content in (b"tuoi\n", b"tuoi\n10,20\n"):
            with self.subTest(content=content), self.assertRaises(ValueError):
                demo.parse_csv_patient(content)
        app = self.start_app()
        uploaded = SimpleNamespace(name="synthetic-missing.csv", getvalue=lambda: b"tuoi\n30\n")
        with patch("streamlit.delta_generator.DeltaGenerator.file_uploader", return_value=uploaded):
            app.radio(key="source_mode").set_value("Tải file mới (.json, .csv)").run()
            app.button(key="classify").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(json.loads(app.session_state["patient_json"]), {"tuoi": 30})
            result = app.session_state["result"]
            self.assertEqual(result["status"], "INSUFFICIENT_DATA")
            self.assertIn("huyet_ap_tam_thu_thap_nhat", result["missing_fields"])
            self.assertNotIn("R-CSU-00", result["rule_results"])

    def test_followup_and_unknown_are_not_displayed_as_exclusion(self):
        app = self.start_app()
        app.selectbox(key="case_id").select("PV-03").run()
        app.button(key="classify").click().run()
        self.assertEqual(app.session_state["result"]["status"], "THEODOIPV")
        self.assertTrue(any(item.value == "KẾT LUẬN: THEO DÕI PHẢN VỆ" for item in app.subheader))
        app.text_area(key="patient_json").set_value('{"tuoi": 30}').run()
        app.button(key="classify").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["result"]["status"], "INSUFFICIENT_DATA")
        self.assertIsNone(app.session_state["result"]["rule_results"]["R-SOC"])
        self.assertFalse(any("Loại trừ Sốc phản vệ" in item.value for item in app.markdown))


if __name__ == "__main__":
    unittest.main()
