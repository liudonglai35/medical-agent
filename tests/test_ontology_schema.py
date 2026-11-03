#!/usr/bin/env python3
"""Schema and safety-semantics tests for the Dermatology Ontology baseline."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "ontology/dermatology_ontology.schema.json"
DATA = ROOT / "data/synthetic/dermatology_annotation_trial_v0.1.json"


def test_schema_and_100_cases() -> None:
    subprocess.run([sys.executable, "scripts/generate_synthetic_cases.py", "--count", "100", "--output", str(DATA)], cwd=ROOT, check=True)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    dataset = json.loads(DATA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    assert len(dataset["cases"]) == 100
    errors = []
    for case in dataset["cases"]:
        errors.extend(f"{case['case_id']}: {e.message}" for e in validator.iter_errors(case))
    assert not errors, "\n".join(errors)


def test_negation_and_missingness_are_distinct() -> None:
    dataset = json.loads(DATA.read_text(encoding="utf-8"))
    facts = {f["fact_id"]: f for f in dataset["cases"][0]["clinical_facts"]}
    assert facts["C1-F4"]["status"] == "ABSENT"
    assert facts["C1-F5"]["status"] == "NOT_DOCUMENTED"
    assert facts["C1-F4"]["source_type"] == "PATIENT_REPORT"
    assert facts["C1-F5"]["source_type"] == "UNKNOWN"


def test_no_ai_inference_in_synthetic_gold_facts() -> None:
    dataset = json.loads(DATA.read_text(encoding="utf-8"))
    for case in dataset["cases"]:
        for fact in case["clinical_facts"]:
            assert fact["source_type"] != "AI_INFERENCE"


if __name__ == "__main__":
    raise SystemExit(__import__("pytest").main([__file__, "-q"]))
