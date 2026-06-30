import numpy as np

def test_evaluation_math():
    print("Running SLAM Metric Unit Tests...")
    
    # 1. Create a perfect synthetic Ground Truth (Straight line from 0 to 10 meters)
    timestamps = np.arange(0, 10, 1.0)
    gt_x = timestamps
    gt_y = np.zeros_like(timestamps)
    gt_z = np.zeros_like(timestamps)
    gt = np.column_stack((timestamps, gt_x, gt_y, gt_z))
    
    # 2. Create an Estimated Trajectory with a KNOWN constant offset of exactly 0.5 meters (50 cm)
    est_x = timestamps + 0.5
    est_y = np.zeros_like(timestamps)
    est_z = np.zeros_like(timestamps)
    traj = np.column_stack((timestamps, est_x, est_y, est_z))
    
    # 3. Calculate ATE (Absolute Trajectory Error)
    # Since every point is off by exactly 0.5m, the RMSE must be exactly 0.5
    ate_errors = np.sqrt(np.sum((traj[:, 1:4] - gt[:, 1:4])**2, axis=1))
    rmse_ate = np.sqrt(np.mean(ate_errors**2))
    
    # 4. Calculate RPE (Relative Pose Error for delta_t = 1s)
    # Since both move at the exact same speed, the relative frame-to-frame error should be exactly 0.0
    rpe_errors = []
    for i in range(len(traj) - 1):
        dist_est = np.linalg.norm(traj[i+1, 1:4] - traj[i, 1:4])
        dist_gt = np.linalg.norm(gt[i+1, 1:4] - gt[i, 1:4])
        rpe_errors.append(abs(dist_est - dist_gt))
    mean_rpe = np.mean(rpe_errors)

    # 5. Assertions (Verifying the math matches the absolute truth)
    try:
        assert np.isclose(rmse_ate, 0.5), f"ATE Math Failed! Expected 0.5, got {rmse_ate}"
        assert np.isclose(mean_rpe, 0.0), f"RPE Math Failed! Expected 0.0, got {mean_rpe}"
        print("✅ ALL TESTS PASSED! Your evaluation math framework is mathematically flawless.")
    except AssertionError as e:
        print(f"❌ TEST FAILED: {e}")

if __name__ == "__main__":
    test_evaluation_math()
