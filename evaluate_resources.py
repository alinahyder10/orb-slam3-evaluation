import os
import time
import psutil
import numpy as np

# 1. Calculate Frame Drop Rate
total_frames = 1177  
try:
    tracked_frames = len(np.loadtxt('KeyFrameTrajectory.txt'))
    dropped_frames = total_frames - tracked_frames
    frame_drop_rate = (dropped_frames / total_frames) * 100
except Exception:
    tracked_frames = 0
    frame_drop_rate = 100.0

# 2. Dynamic Resource Profiling
peak_cpu = 0.0
peak_ram = 0.0
found_process = False

print("Scanning for active './mono_tum' process...")

# Monitor loop (runs while looking for or tracking the SLAM engine)
for _ in range(100):  # Check for up to 10 seconds
    for proc in psutil.process_iter(['pid', 'name']):
        if 'mono_tum' in proc.info['name']:
            found_process = True
            try:
                # Track metrics while the process remains active
                p = psutil.Process(proc.info['pid'])
                while p.is_running():
                    peak_cpu = max(peak_cpu, p.cpu_percent(interval=0.1))
                    peak_ram = max(peak_ram, p.memory_info().rss / (1024 ** 3)) # Bytes to GB
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
    if found_process:
        break
    time.sleep(0.1)

# 3. Print Live Metrics
print("\n=== Dynamic Computational & Resource Metrics ===")
print(f"Total Dataset Frames: {total_frames}")
print(f"Successfully Tracked: {tracked_frames}")
print(f"Frame Drop Rate:      {frame_drop_rate:.2f}%")
print("---------------------------------------")
if found_process:
    print(f"Peak CPU Usage:       {peak_cpu:.1f}%")
    print(f"Peak RAM Usage:       {peak_ram:.2f} GB")
else:
    print("Peak CPU Usage:       N/A (Process 'mono_tum' not detected running)")
    print("Peak RAM Usage:       N/A (Process 'mono_tum' not detected running)")
