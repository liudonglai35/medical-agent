#!/usr/bin/env python3
"""Deterministically generate the 100-case synthetic dermatology annotation trial.

These cases are engineering fixtures only. They are not clinical validation data and
must never be reported as real-world diagnostic performance.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PATTERNS = [
    ("eczematous", "atopic_dermatitis", "papule", "flexural", "pruritus", "pain"),
    ("psoriasiform", "psoriasis", "plaque", "scalp", "pruritus", "pain"),
    ("annular_scaly", "tinea_corporis", "patch", "trunk", "pruritus", "pain"),
    ("acneiform", "acne_vulgaris", "papule", "face", "pain", "pruritus"),
    ("urticarial", "urticaria", "wheal", "lower_leg", "pruritus", "pain"),
    ("grouped_vesicular", "herpes_zoster", "vesicle", "dermatomal", "pain", "pruritus"),
    ("purpuric_vasculitic", "cutaneous_vasculitis", "purpura", "acral", "pain", "pruritus"),
    ("tumor_like", "basal_cell_carcinoma", "papule", "sun_exposed", "pain", "pruritus"),
]


def make_case(index: int) -> dict:
    pattern, diagnosis, lesion, site, symptom, absent_symptom = PATTERNS[index % len(PATTERNS)]
    prefix = f"C{index + 1}"
    source = f"synthetic-case-{index + 1}"
    return {
        "case_id": f"SYN-DERM-{index + 1:03d}",
        "clinical_facts": [
            {"fact_id": f"{prefix}-F1", "domain": "primary_lesion", "concept_id": lesion,
             "value": True, "status": "PRESENT", "certainty": "CONFIRMED", "temporality": "CURRENT",
             "source_type": "CLINICIAN_OBSERVATION", "source_ref": source},
            {"fact_id": f"{prefix}-F2", "domain": "distribution", "concept_id": site,
             "value": True, "status": "PRESENT", "certainty": "CONFIRMED", "temporality": "CURRENT",
             "source_type": "CLINICIAN_OBSERVATION", "source_ref": source},
            {"fact_id": f"{prefix}-F3", "domain": "symptoms", "concept_id": symptom,
             "value": True, "status": "PRESENT", "certainty": "PROBABLE", "temporality": "CURRENT",
             "source_type": "PATIENT_REPORT", "source_ref": source},
            {"fact_id": f"{prefix}-F4", "domain": "symptoms", "concept_id": absent_symptom,
             "value": False, "status": "ABSENT", "certainty": "CONFIRMED", "temporality": "CURRENT",
             "source_type": "PATIENT_REPORT", "source_ref": source},
            {"fact_id": f"{prefix}-F5", "domain": "treatment_response", "concept_id": "prior_topical_therapy",
             "value": None, "status": "NOT_DOCUMENTED", "certainty": "UNKNOWN", "temporality": "HISTORICAL",
             "source_type": "UNKNOWN", "source_ref": source},
        ],
        "patterns": [{
            "pattern_id": f"P-{index + 1}", "name": pattern,
            "supporting_facts": [f"{prefix}-F1", f"{prefix}-F2"], "certainty": "PROBABLE"
        }],
        "diagnoses": [{
            "diagnosis_id": f"D-{index + 1}", "concept_id": diagnosis,
            "status": "WORKING", "rank": 1, "certainty": "PROBABLE",
            "supporting_facts": [f"{prefix}-F1", f"{prefix}-F2", f"{prefix}-F3"],
            "contradicting_facts": [], "missing_information": [f"{prefix}-F5"]
        }],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("data/synthetic/dermatology_annotation_trial_v0.1.json"))
    args = parser.parse_args()
    if args.count < 1:
        raise SystemExit("count must be >= 1")
    cases = [make_case(i) for i in range(args.count)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"dataset_id": "synthetic-derm-annotation-v0.1", "cases": cases}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"generated={len(cases)} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
