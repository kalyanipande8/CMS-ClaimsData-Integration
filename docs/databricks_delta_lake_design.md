# CMS Claims Aggregation — Databricks & Delta Lake Design

**Status: an authored architecture design — no Databricks workspace or
Delta Lake tables are provisioned in this environment.**

## Intended pattern
Each quarterly CMS claims batch would land as a new Delta table version;
a Delta `MERGE INTO` (upsert on `claim_id`) would replace this
repository's `aggregation.py` concatenation + de-duplication, giving ACID
transactional guarantees and full time-travel audit history for every
batch onboarded — exactly the repeatability this repository's
`demonstrate_repeatability()` function verifies in Python.

## Honest disclosure
No Databricks workspace or Delta Lake table exists here; `src/
aggregation.py` and `src/onboarding_process.py` run locally with pandas,
standing in for what a Databricks job against Delta tables would do.
