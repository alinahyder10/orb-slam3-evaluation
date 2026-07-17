import os
import json
import re
import subprocess
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

def scale_timestamps(input_file, output_file):
    if not os.path.exists(input_file): return False
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            parts = line.split()
            if parts:
                try:
                    parts[0] = f"{float(parts[0]) / 1e9:.9f}"
                    f_out.write(" ".join(parts) + "\n")
                except ValueError:
                    continue
    return True

def run_evo_evaluation(est_file, gt_file):
    try:
        cmd = [
            os.path.expanduser("~/.local/bin/evo_ape"), "tum", gt_file, est_file,
            "-a", "-s", "--no_warnings"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        rmse_match = re.search(r"rmse\s+([\d.]+)", result.stdout)
        return float(rmse_match.group(1)) if rmse_match else 0.0
    except Exception:
        return 0.0

def parse_slam_logs(log_paths, trajectory_paths, ground_truth_path):
    report = {
        "pipeline_id": "multi_mono_orb_slam3_vs_lidar",
        "timestamp": datetime.now(ZoneInfo("Africa/Johannesburg")).strftime("%Y-%m-%dT%H:%M:%S%z"),
        "cameras": {}
    }

    # Loop through each camera's log and trajectory
    for idx, (log_path, trajectory_path) in enumerate(zip(log_paths, trajectory_paths), start=1):
        cam_key = f"camera_{idx}"
        cam_metrics = {
            "trajectory_accuracy": {"ate_rmse_meters": 0.0},
            "performance": {"mean_frame_processing_time_ms": 0.0, "max_frame_processing_time_ms": 0.0},
            "reliability": {"track_loss_events": 0}
        }

        # 1. Parse Performance from logs
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                log_content = f.read()
            cam_metrics["reliability"]["track_loss_events"] = len(re.findall(r"(Tracking Lost|Track Lost|Reset)", log_content, re.IGNORECASE))
            
            frame_times = [float(t) for t in re.findall(r"process frame:\s*([\d.]+)", log_content)]
            if frame_times:
                cam_metrics["performance"]["mean_frame_processing_time_ms"] = round(sum(frame_times) / len(frame_times), 2)
                cam_metrics["performance"]["max_frame_processing_time_ms"] = max(frame_times)

        # 2. Compute Real Trajectory Accuracy
        scaled_traj = f"CameraTrajectory_scaled_cam{idx}.txt"
        if scale_timestamps(trajectory_path, scaled_traj):
            cam_metrics["trajectory_accuracy"]["ate_rmse_meters"] = run_evo_evaluation(scaled_traj, ground_truth_path)
            
            # Clean up the temporary scaled file
            if os.path.exists(scaled_traj):
                os.remove(scaled_traj)

        report["cameras"][cam_key] = cam_metrics

    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Multi-Camera SLAM Pipeline Results")
    # nargs="+" allows you to pass a space-separated list of files
    parser.add_argument("--logs", nargs="+", required=True, help="List of SLAM terminal logs (e.g., log1.txt log2.txt)")
    parser.add_argument("--ests", nargs="+", required=True, help="List of estimated trajectories (e.g., traj1.txt traj2.txt)")
    parser.add_argument("--gt", required=True, help="Path to the LiDAR ground truth .tum file")
    parser.add_argument("--out", default="report.json", help="Where to save the JSON report")
    
    args = parser.parse_args()

    # Ensure the user provided a trajectory for every log
    if len(args.logs) != len(args.ests):
        print("[ERROR] The number of logs must match the number of estimated trajectories.")
        exit(1)

    metrics_report = parse_slam_logs(args.logs, args.ests, args.gt)

    with open(args.out, "w") as jf:
        json.dump(metrics_report, jf, indent=2)
    print(f"Metrics report successfully generated: {args.out}")