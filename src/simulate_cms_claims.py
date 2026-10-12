"""Simulate CMS-style Medicare claims batches (beneficiary ID, claim ID,
HCPCS/CPT code, diagnosis code, service date, submission date, paid
amount) across 3 separate source-file batches -- the real multi-batch
aggregation scenario a repeatable onboarding process has to handle."""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

N_CLAIMS_PER_BATCH = 2000
HCPCS_CODES = ["99213", "99214", "80053", "85025", "71046", "93000", "36415"]
DX_CODES = ["E11.9", "I10", "J44.9", "N18.9", "F33.9"]


def simulate_batch(batch_id: str, n: int = N_CLAIMS_PER_BATCH, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    service_date = [date(2025, 1, 1) + timedelta(days=int(d)) for d in rng.integers(0, 270, n)]
    submission_lag = rng.integers(1, 45, n)
    submission_date = [sd + timedelta(days=int(lag)) for sd, lag in zip(service_date, submission_lag)]

    df = pd.DataFrame({
        "batch_id": batch_id,
        "claim_id": [f"{batch_id}-CLM-{i:05d}" for i in range(n)],
        "beneficiary_id": [f"BENE-{rng.integers(0, 5000):05d}" for _ in range(n)],
        "hcpcs_code": rng.choice(HCPCS_CODES, n),
        "diagnosis_code": rng.choice(DX_CODES, n),
        "service_date": service_date,
        "submission_date": submission_date,
        "paid_amount": np.round(rng.gamma(2, 80, n), 2),
    })

    # realistic injected defects: a small fraction of claims missing a
    # diagnosis code, and a small fraction with an invalid HCPCS code
    # (a real upstream data-entry defect)
    missing_idx = rng.choice(df.index, size=max(1, int(n * 0.01)), replace=False)
    df.loc[missing_idx, "diagnosis_code"] = None
    invalid_idx = rng.choice(df.index, size=max(1, int(n * 0.005)), replace=False)
    df.loc[invalid_idx, "hcpcs_code"] = "INVALID"

    return df


def simulate_all_batches() -> dict:
    return {
        "batch_2025_q1": simulate_batch("Q1", seed=151),
        "batch_2025_q2": simulate_batch("Q2", seed=152),
        "batch_2025_q3": simulate_batch("Q3", seed=153),
    }


if __name__ == "__main__":
    batches = simulate_all_batches()
    for name, df in batches.items():
        print(name, df.shape)
