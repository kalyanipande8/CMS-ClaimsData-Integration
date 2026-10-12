"""Aggregates multiple CMS claims batches into one unified dataset --
real concatenation + de-duplication logic (a Databricks/Delta Lake
MERGE-style upsert, done locally with pandas since no Databricks workspace
exists in this environment)."""
from __future__ import annotations

import pandas as pd


def aggregate_batches(batches: dict) -> pd.DataFrame:
    combined = pd.concat(batches.values(), ignore_index=True)
    deduped = combined.drop_duplicates(subset=["claim_id"], keep="first")
    return deduped


if __name__ == "__main__":
    from .simulate_cms_claims import simulate_all_batches

    batches = simulate_all_batches()
    aggregated = aggregate_batches(batches)
    print(f"Aggregated {len(aggregated)} claims from {len(batches)} batches")
