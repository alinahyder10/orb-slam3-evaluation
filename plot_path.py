import numpy as np
import matplotlib.pyplot as plt

traj = np.loadtxt('KeyFrameTrajectory.txt')
gt = np.loadtxt('groundtruth.txt')

matched_traj, matched_gt = [], []
for t_row in traj:
    idx = np.argmin(np.abs(gt[:, 0] - t_row[0]))
    matched_traj.append(t_row[1:4])
    matched_gt.append(gt[idx, 1:4])

X = np.array(matched_traj).T
Y = np.array(matched_gt).T

# Umeyama 3D Alignment
mu_X, mu_Y = X.mean(axis=1, keepdims=True), Y.mean(axis=1, keepdims=True)
X_c, Y_c = X - mu_X, Y - mu_Y
sigma_X = np.mean(np.sum(X_c**2, axis=0))
H = (Y_c @ X_c.T) / X.shape[1]
U, D, Vt = np.linalg.svd(H)
R = U @ Vt
if np.linalg.det(R) < 0: R[:, -1] *= -1
c = np.trace(np.diag(D) @ np.eye(3)) / sigma_X
t = mu_Y - c * R @ mu_X

# Transpose matrices back to (N, 3) for correct plotting
X_aligned = (c * R @ X + t).T
Y_aligned = Y.T

# Plotting
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(projection='3d')
ax.plot(X_aligned[:, 0], X_aligned[:, 1], X_aligned[:, 2], label='ORB-SLAM3 (500 features)', color='blue', linewidth=2)
ax.plot(Y_aligned[:, 0], Y_aligned[:, 1], Y_aligned[:, 2], label='Ground Truth', color='red', linestyle='--', linewidth=1.5)

ax.set_xlabel('X (meters)')
ax.set_ylabel('Y (meters)')
ax.set_zlabel('Z (meters)')
plt.title('SLAM Estimated Path vs. Real Ground Truth')
plt.legend()
plt.savefig('trajectory_comparison.png', dpi=300)
print("Success! Fixed comparison plot saved as 'trajectory_comparison.png'")
