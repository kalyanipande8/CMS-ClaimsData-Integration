"""Real validation criteria across the 3 standard data-quality
dimensions named in the resume bullet: Completeness, Accuracy, Timeliness
-- each a genuinely computed metric against the aggregated claims data."""
from __future__ import annotations

import pandas as pd

from .simulate_cms_claims import HCPCS_CODES, DX_CODES


def completeness(df: pd.DataFrame) -> dict:
    required = ["claim_id", "beneficiary_id", "hcpcs_code", "diagnosis_code", "service_date", "paid_amount"]
    rates = {f: round(100 * df[f].notna().mean(), 3) for f in required}
    return {"by_field": rates, "overall_pct": round(sum(rates.values()) / len(rates), 3)}


def accuracy(df: pd.DataFrame) -> dict:
    valid_hcpcs = df["hcpcs_code"].isin(HCPCS_CODES).mean()
    valid_dx = df["diagnosis_code"].isin(DX_CODES).mean()
    valid_amount = (df["paid_amount"] >= 0).mean()
    return {
        "valid_hcpcs_pct": round(100 * valid_hcpcs, 3),
        "valid_diagnosis_pct": round(100 * valid_dx, 3),
        "valid_paid_amount_pct": round(100 * valid_amount, 3),
        "overall_pct": round(100 * (valid_hcpcs + valid_dx + valid_amount) / 3, 3),
    }


def timeliness(df: pd.DataFrame, max_lag_days: int = 45) -> dict:
    lag = (pd.to_datetime(df["submission_date"]) - pd.to_datetime(df["service_date"])).dt.days
    on_time = (lag <= max_lag_days).mean()
    return {"mean_submission_lag_days": round(float(lag.mean()), 2), "pct_within_sla_pct": round(100 * on_time, 3)}


def full_validation_report(df: pd.DataFrame) -> dict:
    return {"completeness": completeness(df), "accuracy": accuracy(df), "timeliness": timeliness(df)}


if __name__ == "__main__":
    from .simulate_cms_claims import simulate_all_batches
    from .aggregation import aggregate_batches

    aggregated = aggregate_batches(simulate_all_batches())
    import json
    print(json.dumps(full_validation_report(aggregated), indent=2))
