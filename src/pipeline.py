"""Route a selected clinical form to its own rule set."""

from pathlib import Path
from typing import Any, Dict

from src.classify import ClinicalRuleEngine


ROOT = Path(__file__).resolve().parents[1]
RULE_FILES = {
    "phan_ve": "phan_ve_rules.yaml",
    "cap": "cap_rules.yaml",
    "man": "man_rules.yaml",
}


def load_engines() -> Dict[str, ClinicalRuleEngine]:
    return {form: ClinicalRuleEngine(str(ROOT / "rules" / filename))
            for form, filename in RULE_FILES.items()}


def classify_form(
    form_type: str, patient_data: Dict[str, Any], engines: Dict[str, ClinicalRuleEngine]
) -> Dict[str, Any]:
    if form_type not in RULE_FILES:
        raise ValueError(f"Unknown form type: {form_type}")
    return engines[form_type].classify_patient(patient_data)
