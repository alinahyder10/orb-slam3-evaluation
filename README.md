# ORB-SLAM3 Optimization & Evaluation Project

This repository contains the setup, execution, and accuracy evaluation of the ORB-SLAM3 pipeline running on the TUM RGB-D dataset sequence (`rgbd_dataset_freiburg1_desk2`).

## Benchmark Results (Week 2)

We optimized the system performance by tuning the feature extraction count in `TUM1.yaml`.

| Configuration | Median Tracking Time | Absolute Trajectory Error (RMSE) | Scale Factor |
| :--- | :--- | :--- | :--- |
| **Default (1000 Features)** | 0.0158 sec | 0.1885 meters | 0.58x |
| **Optimized (500 Features)** | 0.0148 sec | 0.0367 meters | 1.11x |

### Key Takeaway
Reducing the target features to 500 decreased processing time per frame and drastically improved tracking accuracy (from ~18.8 cm down to **3.67 cm**). Tracking fewer, higher-quality features helped the engine avoid noisy background points.

## Project Structure
* `plot_path.py`: Python script utilizing the Umeyama algorithm for 3D alignment and plotting.
* `evaluate_ate.py`: Evaluation script computing the Absolute Trajectory Error (RMSE).
* `trajectory_comparison.png`: 3D visual plot overlaying SLAM tracking against real ground truth.
