import numpy as np

# Load trajectory and ground truth
traj = np.loadtxt('KeyFrameTrajectory.txt')
gt = np.loadtxt('groundtruth.txt')

errors = []
for t_row in traj:
    t_time = t_row[0]
    # Find the row in ground truth with the closest timestamp
    closest_gt_idx = np.argmin(np.abs(gt[:, 0] - t_time))
    
    # Calculate Euclidean distance between estimated (x,y,z) and ground truth (x,y,z)
    pred_pos = t_row[1:4]
    true_pos = gt[closest_gt_idx, 1:4]
    
    dist = np.linalg.norm(pred_pos - true_pos)
    errors.append(dist)

rmse = np.sqrt(np.mean(np.square(errors)))
print(f"\n=== SLAM Accuracy Results ===")
print(f"Absolute Trajectory Error (RMSE): {rmse:.4f} meters")
print(f"Max Error: {max(errors):.4f} meters")
