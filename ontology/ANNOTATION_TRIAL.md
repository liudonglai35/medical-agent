# 100-case Ontology Annotation Trial V0.1

## Objective

Evaluate whether Dermatology Ontology V0.1.1 can represent the intended clinical facts consistently. This is an ontology/annotation-quality exercise, **not a model-performance study**.

## Protocol

1. Generate 100 deterministic synthetic cases.
2. Annotator A independently maps source facts into ontology concepts and state fields.
3. Annotator B independently performs the same task without seeing A's labels.
4. Compare field-level agreement.
5. Adjudicate disagreements with a third expert or documented consensus rule.
6. Convert recurring disagreements into explicit terminology/annotation rules.
7. Revise ontology to V0.1.2 only when a representation gap or ambiguity is demonstrated.

## Required agreement outputs

- exact agreement for status/negation;
- concept-level agreement for lesion, distribution, symptom and diagnosis fields;
- Cohen's kappa for binary/two-rater categorical fields where applicable;
- Fleiss' kappa when >2 raters are analyzed;
- disagreement matrix and adjudication reason;
- unresolved ontology gaps.

## Safety acceptance gates

- critical negation reversal: **0**;
- source provenance loss: **0** for required provenance fields;
- original fact and AI inference must never overwrite each other;
- `NOT_DOCUMENTED` must not be converted into `ABSENT` without explicit evidence;
- synthetic results must never be presented as real-world clinical performance.
