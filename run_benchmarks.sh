#!/bin/bash

# Check if the user actually provided a ground truth file
if [ -z "$1" ]; then
    echo "[ERROR] You must provide the LiDAR ground truth file."
    echo "Usage: ./run_benchmarks.sh /path/to/ground_truth.tum"
    exit 1
fi

echo "=== Launching 3-Camera Monocular SLAM Evaluation ==="
echo "----------------------------------------------------"

# Configuration Paths
GT_FILE=$1  # <--- This grabs the file path you type in the terminal
ORB_VOCAB="/home/alina/ros2_ws/src/orbslam3_ros2/config/ORBvoc.txt"
CONFIG_CAM1="config_cam1.yaml"
CONFIG_CAM2="config_cam2.yaml"
CONFIG_CAM3="config_cam3.yaml"

# 1. Create temporary subdirectories to prevent file overwrites
mkdir -p out_cam1 out_cam2 out_cam3

# 2. Launch Camera 1
echo "Starting Camera 1 pipeline..."
cd out_cam1
ros2 run orbslam3_ros2 mono --ros-args -p vocab_path:=../$ORB_VOCAB -p config_path:=../$CONFIG_CAM1 --remap /camera/image_raw:=/zed2i/zed_node/left/image_rect_color > ../log_cam1.txt 2>&1 &
PID1=$!
cd ..

# 3. Launch Camera 2
echo "Starting Camera 2 pipeline..."
cd out_cam2
ros2 run orbslam3_ros2 mono --ros-args -p vocab_path:=../$ORB_VOCAB -p config_path:=../$CONFIG_CAM2 --remap /camera/image_raw:=/zed2i/zed_node/right/image_rect_color > ../log_cam2.txt 2>&1 &
PID2=$!
cd ..

# 4. Launch Camera 3 (Adjust the remap topic to your 3rd camera/lens)
echo "Starting Camera 3 pipeline..."
cd out_cam3
ros2 run orbslam3_ros2 mono --ros-args -p vocab_path:=../$ORB_VOCAB -p config_path:=../$CONFIG_CAM3 --remap /camera/image_raw:=/zed2i/zed_node/center/image_rect_color > ../log_cam3.txt 2>&1 &
PID3=$!
cd ..

echo "----------------------------------------------------"
echo "Pipelines are running!"
echo "If running a bag file, let it finish playing."
echo "Press [ENTER] when you are ready to stop tracking and evaluate..."
read -r

# 5. Gracefully kill nodes to trigger trajectory saves
echo "Sending shutdown signals to save trajectories..."
kill -SIGINT $PID1 $PID2 $PID3

echo "Waiting for trajectories to be written to disk..."
while true; do
    # Check that all 3 logs confirm the trajectory was saved
    if grep -q "Saving camera trajectory" log_cam1.txt && \
       grep -q "Saving camera trajectory" log_cam2.txt && \
       grep -q "Saving camera trajectory" log_cam3.txt; then
        echo "✅ All trajectory data successfully captured."
        break
    fi
    sleep 1
done

# 6. Extract and rename the trajectories
mv out_cam1/CameraTrajectory.txt ./Trajectory_cam1.txt
mv out_cam2/CameraTrajectory.txt ./Trajectory_cam2.txt
mv out_cam3/CameraTrajectory.txt ./Trajectory_cam3.txt

# Clean up the temporary empty folders
rm -rf out_cam1 out_cam2 out_cam3

echo "----------------------------------------------------"
echo "Running automated metrics evaluation..."

# 7. Pass everything into the new Python script
python3 evaluate_run.py \
    --logs log_cam1.txt log_cam2.txt log_cam3.txt \
    --ests Trajectory_cam1.txt Trajectory_cam2.txt Trajectory_cam3.txt \
    --gt $GT_FILE \
    --out final_report.json

echo "Done! Check final_report.json for your baseline metrics."
