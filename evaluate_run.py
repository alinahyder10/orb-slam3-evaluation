import os
import json
import re
import math
import subprocess
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

# Locate and load the schema file dynamically
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(SCRIPT_DIR, "schema.json")

try:
    with open(SCHEMA_PATH, "r") as f:
        REPORT_SCHEMA = json.load(f)
except FileNotFoundError:
    REPORT_SCHEMA = None

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

def run_evo_ape(est_file, gt_file):
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

def run_evo_rpe(est_file, gt_file):
    try:
        # Use native consecutive frames (-u f is default) and align scale for monocular SLAM
        cmd = [
            os.path.expanduser("~/.local/bin/evo_rpe"), "tum", gt_file, est_file,
            "-r", "trans_part", "--correct_scale", "--no_warnings"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        rmse_match = re.search(r"rmse\s+([\d.]+)", result.stdout)
        return float(rmse_match.group(1)) if rmse_match else 0.0
    except Exception:
        return 0.0

def calculate_trajectory_metrics(file_path):
    """Calculates total duration and 3D path length of a TUM trajectory."""
    if not os.path.exists(file_path):
        return 0.0, 0.0
    
    timestamps = []
    path_length = 0.0
    prev_point = None
    
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 4:
                try:
                    t = float(parts[0])
                    # If timestamps are in nanoseconds, scale to seconds for calculation
                    if t > 1e12:
                        t = t / 1e9
                    timestamps.append(t)
                    
                    curr_point = (float(parts[1]), float(parts[2]), float(parts[3]))
                    if prev_point is not None:
                        dist = math.sqrt(
                            (curr_point[0] - prev_point[0])**2 +
                            (curr_point[1] - prev_point[1])**2 +
                            (curr_point[2] - prev_point[2])**2
                        )
                        path_length += dist
                    prev_point = curr_point
                except ValueError:
                    continue
                    
    if len(timestamps) < 2:
        return 0.0, 0.0
        
    duration = max(timestamps) - min(timestamps)
    return duration, path_length

def validate_generated_report(report_data):
    if REPORT_SCHEMA is None:
        return
    try:
        import jsonschema
        jsonschema.validate(instance=report_data, schema=REPORT_SCHEMA)
        print("✅ Report successfully validated against JSON Schema.")
    except ImportError:
        print("⚠️ 'jsonschema' library not installed. Skipping schema validation step.")
    except Exception as err:
        print(f"❌ Schema Validation Error: {err}")

def parse_slam_logs(log_paths, trajectory_paths, ground_truth_path, dataset_name):
    report = {
        "pipeline_id": "multi_mono_orb_slam3_vs_lidar",
        "dataset": dataset_name,
        "timestamp": datetime.now(ZoneInfo("Africa/Johannesburg")).strftime("%Y-%m-%dT%H:%M:%S%z"),
        "cameras": {}
    }

    # Pre-calculate Ground Truth duration
    gt_duration, _ = calculate_trajectory_metrics(ground_truth_path)

    for idx, (log_path, trajectory_path) in enumerate(zip(log_paths, trajectory_paths), start=1):
        cam_key = f"camera_{idx}"
        
        cam_metrics = {
            "trajectory_accuracy": {
                "ate_rmse_meters": 0.0,
                "rpe_rmse_meters_per_sec": 0.0,
                "drift_per_meter_percentage": 0.0
            },
            "performance": {
                "mean_frame_processing_time_ms": 0.0,
                "max_frame_processing_time_ms": 0.0,
                "total_execution_time_sec": 0.0
            },
            "reliability": {
                "track_loss_events": 0,
                "frames_tracked_percentage": 100.0
            }
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

        # 2. Process Trajectory Dynamics
        if os.path.exists(trajectory_path):
            scaled_traj = f"CameraTrajectory_scaled_cam{idx}.txt"
            if scale_timestamps(trajectory_path, scaled_traj):
                # Count total tracking poses in the file
                with open(scaled_traj, 'r') as f:
                    num_poses = sum(1 for line in f if line.strip())
                
                # Calculate absolute (ATE) error using evo
                ate_rmse = run_evo_ape(scaled_traj, ground_truth_path)
                
                # Calculate raw frame-to-frame RPE (in meters)
                raw_rpe_meters = run_evo_rpe(scaled_traj, ground_truth_path)
                
                # Extract temporal duration and 3D path length
                duration, path_length = calculate_trajectory_metrics(scaled_traj)
                
                # Convert RPE from meters-per-frame to meters-per-second
                if num_poses > 1 and duration > 0:
                    avg_time_step = duration / (num_poses - 1)
                    rpe_rmse_per_sec = raw_rpe_meters / avg_time_step if avg_time_step > 0 else 0.0
                else:
                    rpe_rmse_per_sec = 0.0
                
                # Math calculations for drift and track percentages
                drift_percentage = (ate_rmse / path_length * 100.0) if path_length > 0 else 0.0
                track_percentage = (duration / gt_duration * 100.0) if gt_duration > 0 else 100.0

                # Populate metrics dict with clean rounding
                cam_metrics["trajectory_accuracy"]["ate_rmse_meters"] = round(ate_rmse, 6)
                cam_metrics["trajectory_accuracy"]["rpe_rmse_meters_per_sec"] = round(rpe_rmse_per_sec, 6)
                cam_metrics["trajectory_accuracy"]["drift_per_meter_percentage"] = round(drift_percentage, 4)
                
                cam_metrics["performance"]["total_execution_time_sec"] = round(duration, 2)
                cam_metrics["reliability"]["frames_tracked_percentage"] = round(min(100.0, max(0.0, track_percentage)), 2)
                
                # Clean up temporary scaled file
                if os.path.exists(scaled_traj):
                    os.remove(scaled_traj)

        report["cameras"][cam_key] = cam_metrics

    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Multi-Camera SLAM Pipeline Results")
    parser.add_argument("--logs", nargs="+", required=True, help="List of SLAM terminal logs")
    parser.add_argument("--ests", nargs="+", required=True, help="List of estimated trajectories")
    parser.add_argument("--gt", required=True, help="Path to the LiDAR ground truth .tum file")
    parser.add_argument("--dataset", default="live_scan", help="Name of the evaluated dataset")
    parser.add_argument("--out", default="final_report.json", help="Where to save the JSON report")
    
    args = parser.parse_args()

    if len(args.logs) != len(args.ests):
        print("[ERROR] The number of logs must match the number of estimated trajectories.")
        exit(1)

    metrics_report = parse_slam_logs(args.logs, args.ests, args.gt, args.dataset)
    validate_generated_report(metrics_report)

    with open(args.out, "w") as jf:
        json.dump(metrics_report, jf, indent=2)
    print(f"Metrics report successfully generated: {args.out}")