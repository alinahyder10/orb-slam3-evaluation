import numpy as np

traj = np.loadtxt('KeyFrameTrajectory.txt')
gt = np.loadtxt('groundtruth.txt')

# Match timestamps
matched_traj = []
matched_gt = []
for t_row in traj:
    closest_gt_idx = np.argmin(np.abs(gt[:, 0] - t_row[0]))
    matched_traj.append(t_row[1:4])
    matched_gt.append(gt[closest_gt_idx, 1:4])

P = np.array(matched_traj)
Q = np.array(matched_gt)

# Simple scale alignment factor
scale = np.mean(np.linalg.norm(Q, axis=1)) / np.mean(np.linalg.norm(P, axis=1))
P_scaled = P * scale

# Calculate true tracking error
errors = np.linalg.norm(P_scaled - Q, axis=1)
rmse = np.sqrt(np.mean(np.square(errors)))

print(f"\n=== Scale-Aligned SLAM Accuracy ===")
print(f"Absolute Trajectory Error (RMSE): {rmse:.4f} meters")
print(f"Scale Factor applied: {scale:.2f}x")
