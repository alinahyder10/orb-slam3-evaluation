# Multi-Camera SLAM Benchmarking Pipeline

This repository contains an automated benchmarking framework for evaluating visual SLAM performance on physical hardware. Originally designed to tune ORB-SLAM3 on offline TUM RGB-D datasets, the project has evolved into a "Benchmarking Machine" capable of running three parallel monocular camera feeds (live or via ROS2 bags) and automatically scoring them against LiDAR or high-accuracy hardware ground truth.

## The Benchmarking Pipeline

The system handles the entire evaluation workflow seamlessly:
1. **Data Ingestion:** Takes in live ROS2 topics (e.g., `/zed2i/zed_node/.../image_rect_color`) or pre-recorded ROS2 bags from the physical scanner.
2. **Parallel SLAM Execution:** Runs three isolated instances of ORB-SLAM3 simultaneously in subdirectories to prevent file overwrites, tracking left, right, and center camera feeds.
3. **Automated Formatting:** Gracefully catches shutdown signals, extracts trajectories, and automatically scales ORB-SLAM3's nanosecond timestamps to standard Unix seconds.
4. **evo Integration:** Bypasses manual alignment scripts by natively calling `evo` (`evo_ape`) via subprocesses to calculate the Absolute Trajectory Error (RMSE) against the ground truth.
5. **Consolidated Reporting:** Generates a comprehensive `final_report.json` containing positional accuracy, track loss events, and processing times for all three cameras simultaneously.

## Project Structure

* **`run_benchmarks.sh`**: The master execution script. Launches the 3-camera nodes, handles graceful `SIGINT` shutdowns for live feeds to ensure data is written to disk, renames output files, and triggers the Python evaluator.
* **`evaluate_run.py`**: A dynamic Python evaluation script utilizing `argparse`. It ingests multiple camera logs and trajectories, aligns them with the single ground truth, fixes timestamp scales, and compiles the metrics JSON.
* **Legacy Scripts**: `plot_path.py` and `evaluate_ate.py` (custom Umeyama/RMSE scripts) have been deprecated and replaced by the robust `evo` package.

## Usage

Run the master benchmarking script by passing your LiDAR or hardware ground truth (`.tum`) file as the single argument:

```bash
./run_benchmarks.sh /path/to/latest_scan_lidar_gt.tum
