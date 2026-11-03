# Dermatology Ontology

## V0.1.1 engineering baseline

This directory contains the machine-readable baseline for the Dermatology Clinical Intelligence Platform.

### Core principles

1. Clinical facts and AI inference are never silently overwritten or conflated.
2. `ABSENT` means the finding was explicitly negated; `NOT_DOCUMENTED` means it was not mentioned.
3. Every clinical fact carries source provenance.
4. Clinical patterns are intermediate representations, not direct disease diagnoses.
5. Diagnosis assessments explicitly separate supporting facts, contradicting facts, and missing information.
6. Ontology and enum changes must be versioned.

### Current schema

- `dermatology_ontology.schema.json`: JSON Schema baseline for V0.1.1.

### Next engineering gates

- 100-case expert annotation trial
- field-level agreement analysis
- V0.1.2 terminology/rule revision
- schema validation tests
- database migration
- medical-record structuring integration
