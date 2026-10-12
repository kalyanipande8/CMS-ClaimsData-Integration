# CMS and Claims Data Integration Pipeline

Aggregates 3 simulated quarterly CMS Medicare claims batches (6,000
claims total) through a real, repeatable onboarding process, validated
against completeness, accuracy, and timeliness criteria — plus a
Databricks/Delta Lake architecture design.

> Designed and coordinated CMS/claims data aggregation across 3 quarterly
> batches (6,000 claims); 99.8% completeness, 99.5% accuracy, 100% within
> submission-lag SLA — all measured. Developed a repeatable onboarding
> process, demonstrated identically handling a cold-start batch and 2
> incremental batches.

## What's real vs. synthetic — read this first

**Real:** the aggregation logic (`src/aggregation.py`, concatenation +
claim-ID de-duplication), the 3-dimension validation criteria (`src/
validation_criteria.py`: completeness, accuracy, timeliness — all
genuinely computed), and the repeatable onboarding process (`src/
onboarding_process.py`) are all executed. Repeatability is demonstrated,
not just claimed: the same `onboard_batch()` function runs on the cold-
start batch and then on each incremental batch, with claim counts
verified to accumulate monotonically and every report well-formed at
every step.

**Synthetic:** there is no real Databricks workspace, Delta Lake table, or
CMS claims feed in this environment (see `docs/
databricks_delta_lake_design.md` for the authored architecture design).
`src/simulate_cms_claims.py` generates 3 quarterly batches of 2,000 claims
each, with realistic injected defects (1% missing diagnosis codes, 0.5%
invalid HCPCS codes).

## Scientific approach

1. **Claims simulation** (`src/simulate_cms_claims.py`): CMS-style claim
   fields (beneficiary ID, HCPCS/diagnosis codes, service/submission
   dates, paid amount), 3 quarterly batches, realistic defects.

2. **Aggregation** (`src/aggregation.py`): concatenates batches and
   de-duplicates on `claim_id` — the pandas-local stand-in for a Delta
   Lake `MERGE INTO` upsert (see the architecture doc).

3. **Validation criteria** (`src/validation_criteria.py`):
   - **Completeness**: % non-null per required field.
   - **Accuracy**: % of HCPCS/diagnosis codes in the valid code set, % of
     paid amounts non-negative.
   - **Timeliness**: mean submission lag (service date → submission date)
     and % of claims within a 45-day SLA.

4. **Repeatable onboarding** (`src/onboarding_process.py`): one function
   handling both the cold-start batch and every incremental batch
   identically, demonstrated across all 3 batches in sequence.

## Results (real, from `run_all.py`, seeds 151/152/153)

```
3 batches onboarded, 6,000 total claims (no real duplicates found, as expected)

Completeness: 99.833%  (1% of diagnosis codes missing, injected)
Accuracy:     99.5%    (0.5% invalid HCPCS codes, injected)
Timeliness:   100% within the 45-day SLA; mean submission lag 22.8 days

Onboarding repeatability: claim counts accumulate correctly at every step
  (2,000 -> 4,000 -> 6,000), same validation report structure every time.
```

`tests/test_pipeline.py` (6 tests, all passing) checks: 3 batches
simulated, aggregation de-duplicates correctly, no real duplicates are
dropped, the validation report covers all 3 required dimensions, injected
defects are detected by completeness/accuracy, and onboarding is
repeatable across all 3 batches with monotonically accumulating counts.

## Usage

```bash
pip install -r requirements.txt
python3 run_all.py            # simulates batches, demonstrates onboarding, reports validation
python3 -m pytest tests/ -v    # run the test suite
```

Outputs are written to `data/*.csv` and `results/summary.json`.

## Project structure

```
src/
  simulate_cms_claims.py      # 3-batch, 6,000-claim CMS claims simulation
  aggregation.py                 # concatenation + de-duplication
  validation_criteria.py            # completeness, accuracy, timeliness
  onboarding_process.py                # repeatable onboarding function
docs/
  databricks_delta_lake_design.md        # authored Databricks/Delta Lake design
run_all.py                                  # end-to-end pipeline
tests/test_pipeline.py                        # pytest suite
```

## Tech stack

Python 3.11, pandas, numpy, pytest (executed pipeline); Databricks/Delta
Lake architecture described in design documentation, not deployed.

## Limitations

- No Databricks workspace or Delta Lake tables exist in this environment.
- No real CMS claims feed is used.
- The validation criteria cover 3 standard dimensions at a representative
  level of depth; a production CMS data-quality framework would likely add
  more granular rule coverage per field.
