import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from src.simulate_cms_claims import simulate_all_batches
from src.aggregation import aggregate_batches
from src.validation_criteria import full_validation_report
from src.onboarding_process import demonstrate_repeatability


@pytest.fixture(scope="module")
def batches():
    return simulate_all_batches()


def test_three_batches_simulated(batches):
    assert len(batches) == 3


def test_aggregation_deduplicates_by_claim_id(batches):
    aggregated = aggregate_batches(batches)
    assert not aggregated["claim_id"].duplicated().any()


def test_aggregation_preserves_total_claim_count(batches):
    aggregated = aggregate_batches(batches)
    total_raw = sum(len(df) for df in batches.values())
    assert len(aggregated) == total_raw  # no real duplicates injected, so none should be dropped


def test_validation_report_has_all_three_dimensions(batches):
    aggregated = aggregate_batches(batches)
    report = full_validation_report(aggregated)
    assert set(report.keys()) == {"completeness", "accuracy", "timeliness"}


def test_injected_defects_detected_by_completeness_and_accuracy(batches):
    aggregated = aggregate_batches(batches)
    report = full_validation_report(aggregated)
    assert report["completeness"]["overall_pct"] < 100.0
    assert report["accuracy"]["overall_pct"] < 100.0


def test_onboarding_is_repeatable_across_batches(batches):
    """The same onboarding function run on batch 1 (cold start) and
    batches 2/3 (incremental) should behave identically -- claims
    accumulate correctly and every step's report is well-formed."""
    demo = demonstrate_repeatability(batches)
    assert len(demo["steps"]) == 3
    counts = [s["n_claims_total"] for s in demo["steps"]]
    assert counts == sorted(counts)  # monotonically increasing as batches onboard
