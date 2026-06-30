import numpy as np

# 1. Load Trajectories
traj = np.loadtxt('KeyFrameTrajectory.txt')
gt = np.loadtxt('groundtruth.txt')

# 2. Time-Synchronize Data
matched_traj, matched_gt = [], []
for t_row in traj:
    idx = np.argmin(np.abs(gt[:, 0] - t_row[0]))
    matched_traj.append(t_row[0:4]) # [time, x, y, z]
    matched_gt.append(gt[idx, 0:4])

E = np.array(matched_traj)
G = np.array(matched_gt)
num_frames = len(E)

# 3. Calculate Total Distance Traveled
distances = np.sqrt(np.diff(G[:, 1], axis=0)**2 + np.diff(G[:, 2], axis=0)**2 + np.diff(G[:, 3], axis=0)**2)
total_distance = np.sum(distances)

# 4. Calculate RPE (Fixed Time Interval Delta t = 1.0 second)
delta_t = 1.0
rpe_errors = []

for i in range(num_frames):
    for j in range(i + 1, num_frames):
        # Find pairs separated by approximately 1 second
        if abs((E[j, 0] - E[i, 0]) - delta_t) < 0.1:
            # Local translation segments
            dist_est = np.linalg.norm(E[j, 1:4] - E[i, 1:4])
            dist_gt = np.linalg.norm(G[j, 1:4] - G[i, 1:4])
            
            rpe_errors.append(abs(dist_est - dist_gt))
            break

mean_rpe = np.mean(rpe_errors) if rpe_errors else 0.0

# 5. Calculate Drift Per Meter Traveled
# (Final absolute tracking discrepancy divided by total path distance)
final_drift = np.linalg.norm(E[-1, 1:4] - G[-1, 1:4])
drift_per_meter = final_drift / total_distance

# Print Results
print("=== Additional SLAM Metrics ===")
print(f"Total Path Distance:   {total_distance:.2f} meters")
print(f"Relative Pose Error:   {mean_rpe * 100:.2f} cm per second (delta_t = 1s)")
print(f"Drift Per Meter:       {drift_per_meter * 100:.2f} cm/m")
