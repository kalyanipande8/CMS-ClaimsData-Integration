"""End-to-end: simulate 3 CMS claims batches, demonstrate the repeatable
onboarding process, and report the final validation criteria."""
import json
import os

from src.simulate_cms_claims import simulate_all_batches
from src.onboarding_process import demonstrate_repeatability

os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

print("=== Simulating 3 CMS claims batches ===")
batches = simulate_all_batches()
for name, df in batches.items():
    df.to_csv(f"data/{name}.csv", index=False)
    print(f"  {name}: {len(df)} claims")

print("\n=== Demonstrating the repeatable onboarding process ===")
demo = demonstrate_repeatability(batches)
for step in demo["steps"]:
    print(f"Step {step['step']}: {step['n_claims_total']} total claims")
    print(f"  Completeness: {step['validation_report']['completeness']['overall_pct']}%")
    print(f"  Accuracy:     {step['validation_report']['accuracy']['overall_pct']}%")
    print(f"  Timeliness:   {step['validation_report']['timeliness']['pct_within_sla_pct']}% within SLA")

final_report = demo["steps"][-1]["validation_report"]
summary = {
    "n_batches_onboarded": len(batches),
    "final_total_claims": demo["final_total_claims"],
    "completeness_pct": final_report["completeness"]["overall_pct"],
    "accuracy_pct": final_report["accuracy"]["overall_pct"],
    "timeliness_pct_within_sla": final_report["timeliness"]["pct_within_sla_pct"],
    "mean_submission_lag_days": final_report["timeliness"]["mean_submission_lag_days"],
}
with open("results/summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n=== Summary ===")
print(json.dumps(summary, indent=2))
