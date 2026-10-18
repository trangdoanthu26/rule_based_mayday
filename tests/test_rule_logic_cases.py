"""Regression evidence for current YAML, including explicitly documented workflow gaps."""

import copy
import json
import unittest
from pathlib import Path

from src.pipeline import classify_form, load_engines


ROOT = Path(__file__).resolve().parents[1]


class TestSyntheticRuleLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(
            (ROOT / 'data/synthetic/rule_logic_cases.json').read_text(encoding='utf-8')
        )
        cls.engines = load_engines()
        cls.cases = cls.fixture['cases']

    def test_case_identifiers_and_rule_version(self):
        ids = [case['id'] for case in self.cases]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual({self.fixture['rules_version']}, {engine.rules_version for engine in self.engines.values()})
        self.assertGreaterEqual(len(ids), 20)

    def test_current_engine_expectations(self):
        for case in self.cases:
            with self.subTest(case=case['id'], description=case['mo_ta']):
                expected = case['expected_engine']
                result = classify_form(case['form_type'], case['du_lieu'], self.engines)
                self.assertEqual(result['status'], expected['status'])
                self.assertEqual(result['matched_rule_id'], expected['matched_rule_id'])
                self.assertEqual(result['predicted_label'], expected['predicted_label'])
                for rule_id, value in expected['rule_results'].items():
                    self.assertIs(result['rule_results'][rule_id], value)
                if result['status'] != 'CLASSIFIED':
                    self.assertIsNone(result['predicted_label'])

    def test_repeated_results_and_input_immutability(self):
        for case in self.cases:
            with self.subTest(case=case['id']):
                data = copy.deepcopy(case['du_lieu'])
                first = classify_form(case['form_type'], data, self.engines)
                self.assertEqual(data, case['du_lieu'])
                self.assertEqual(first, classify_form(case['form_type'], data, self.engines))

    def test_acute_normal_and_all_three_severe_rules_are_reachable(self):
        matched = set()
        for case in self.cases:
            result = classify_form(case['form_type'], case['du_lieu'], self.engines)
            matched.update(result['matched_rule_ids'])
        self.assertTrue({'R01-CAP-THUONG', 'R01-CAP-NANG-NGUA',
                         'R02-CAP-NANG-PHUMACH', 'R03-CAP-NANG-CONLAI'} <= matched)

    def test_formula_wrong_type_should_return_review_without_crashing(self):
        case = next(case for case in self.cases if case['id'] == 'SOC-MISSING-80')
        result = classify_form(case['form_type'], case['du_lieu'], self.engines)
        self.assertEqual(result['status'], 'NEEDS_REVIEW')

    def test_formula_boolean_pressure_should_not_classify_shock(self):
        case = next(case for case in self.cases if case['id'] == 'SOC-INVALID-BOOL-TRUE')
        result = classify_form(case['form_type'], case['du_lieu'], self.engines)
        self.assertEqual(result['status'], 'NEEDS_REVIEW')


if __name__ == '__main__':
    unittest.main()
