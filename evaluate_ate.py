import numpy as np

traj = np.loadtxt('KeyFrameTrajectory.txt')
gt = np.loadtxt('groundtruth.txt')

matched_traj, matched_gt = [], []
for t_row in traj:
    idx = np.argmin(np.abs(gt[:, 0] - t_row[0]))
    matched_traj.append(t_row[1:4])
    matched_gt.append(gt[idx, 1:4])

X = np.array(matched_traj).T  # 3 x N
Y = np.array(matched_gt).T   # 3 x N

# Umeyama Alignment (Find best Scale, Rotation, and Translation)
mu_X, mu_Y = X.mean(axis=1, keepdims=True), Y.mean(axis=1, keepdims=True)
X_c, Y_c = X - mu_X, Y - mu_Y
sigma_X = np.mean(np.sum(X_c**2, axis=0))
H = (Y_c @ X_c.T) / X.shape[1]
U, D, Vt = np.linalg.svd(H)
R = U @ Vt
if np.linalg.det(R) < 0: R[:, -1] *= -1
c = np.trace(np.diag(D) @ np.eye(3)) / sigma_X
t = mu_Y - c * R @ mu_X

# Transform estimated path
X_aligned = (c * R @ X + t).T
Y = Y.T

errors = np.linalg.norm(X_aligned - Y, axis=1)
print(f"\n=== Fully Aligned SLAM Accuracy ===")
print(f"Absolute Trajectory Error (RMSE): {np.sqrt(np.mean(errors**2)):.4f} meters")
print(f"Scale Factor: {c:.2f}x")
