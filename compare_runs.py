import json
import sys
import os

def load_report(path):
    with open(path, 'r') as f:
        return json.load(f)

def compare(baseline_path, current_path):
    if not os.path.exists(baseline_path) or not os.path.exists(current_path):
        print(f"Error: One of the report files is missing.")
        sys.exit(1)

    b = load_report(baseline_path)
    c = load_report(current_path)

    b_metrics = b["metrics"]
    c_metrics = c["metrics"]

    print(f"\n=== Performance Comparison ===")
    print(f"Baseline: {baseline_path} | Current: {current_path}\n")
    print(f"{'Metric':<35} | {'Baseline':<10} | {'Current':<10} | {'Status':<10}")
    print("-" * 75)

    regressions = 0

    # 1. Check ATE Accuracy (Threshold: 0.05 meters degradation)
    ate_b = b_metrics["trajectory_accuracy"]["ate_rmse_meters"]
    ate_c = c_metrics["trajectory_accuracy"]["ate_rmse_meters"]
    ate_status = "PASS"
    if ate_c > ate_b + 0.05:
        ate_status = "REGRESSION"
        regressions += 1
    print(f"{'ATE RMSE (meters)':<35} | {ate_b:<10.4f} | {ate_c:<10.4f} | {ate_status:<10}")

    # 2. Check Frame Processing Speed (Threshold: 10ms degradation)
    time_b = b_metrics["performance"]["mean_frame_processing_time_ms"]
    time_c = c_metrics["performance"]["mean_frame_processing_time_ms"]
    time_status = "PASS"
    if time_c > time_b + 10.0:
        time_status = "REGRESSION"
        regressions += 1
    print(f"{'Mean Frame Processing (ms)':<35} | {time_b:<10.1f} | {time_c:<10.1f} | {time_status:<10}")

    # 3. Check Track Loss Events
    loss_b = b_metrics["reliability"]["track_loss_events"]
    loss_c = c_metrics["reliability"]["track_loss_events"]
    loss_status = "PASS"
    if loss_c > loss_b:
        loss_status = "REGRESSION"
        regressions += 1
    print(f"{'Track Loss Events':<35} | {loss_b:<10} | {loss_c:<10} | {loss_status:<10}")
    print("-" * 75)

    if regressions > 0:
        print(f"❌ ALERT: {regressions} regression(s) detected!")
        sys.exit(1)
    else:
        print("✅ SUCCESS: All metrics are stable.")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 compare_runs.py <baseline.json> <current.json>")
        sys.exit(1)
    compare(sys.argv[1], sys.argv[2])
