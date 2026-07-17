#!/bin/bash

# Configuration Paths

# Locate ORBvoc.txt dynamically
if [ -f "./Vocabulary/ORBvoc.txt" ]; then
    ORB_VOCAB="./Vocabulary/ORBvoc.txt"
elif [ -f "../Vocabulary/ORBvoc.txt" ]; then
    ORB_VOCAB="../Vocabulary/ORBvoc.txt"
elif ros2 pkg prefix orbslam3_ros2 &>/dev/null; then
    ORB_VOCAB="$(ros2 pkg prefix orbslam3_ros2)/share/orbslam3_ros2/config/ORBvoc.txt"
else
    # Your local fallback path
    ORB_VOCAB="/home/alina/ros2_ws/src/orbslam3_ros2/config/ORBvoc.txt"
fi

# Let the user know where we found it
echo "Using Vocabulary: $ORB_VOCAB"

CONFIG_CAM1="config_cam1.yaml"
CONFIG_CAM2="config_cam2.yaml"
CONFIG_CAM3="config_cam3.yaml"

# 1. Determine Mode (Live vs Offline)
if [ -z "$1" ]; then
    echo "🎥 No ground truth file provided. Entering LIVE SCAN mode..."
    echo "Starting KISS-ICP LiDAR tracking for live ground truth..."
    
    # Launch KISS-ICP in the background to generate live GT
    ros2 run kiss_icp kiss_icp_node --ros-args -r /pointcloud:=/ouster/points > log_lidar_gt.txt 2>&1 &
    LIDAR_PID=$!
    
    # Default output path for live KISS-ICP trajectory
    GT_FILE="kiss_icp_trajectory.tum"
    MODE="live"
else
    echo "📁 Ground truth file provided. Entering OFFLINE EVALUATION mode..."
    GT_FILE=$1
    MODE="offline"
fi

echo "=== Launching 3-Camera Monocular SLAM Evaluation ==="
echo "Mode: ${MODE^^}"
echo "----------------------------------------------------"

# 2. Create temporary subdirectories to prevent file overwrites
mkdir -p out_cam1 out_cam2 out_cam3

# 3. Launch Camera 1
echo "Starting Camera 1 pipeline..."
cd out_cam1
ros2 run orbslam3_ros2 mono --ros-args -p vocab_path:=../$ORB_VOCAB -p config_path:=../$CONFIG_CAM1 --remap /camera/image_raw:=/zed2i/zed_node/left/image_rect_color > ../log_cam1.txt 2>&1 &
PID1=$!
cd ..

# 4. Launch Camera 2
echo "Starting Camera 2 pipeline..."
cd out_cam2
ros2 run orbslam3_ros2 mono --ros-args -p vocab_path:=../$ORB_VOCAB -p config_path:=../$CONFIG_CAM2 --remap /camera/image_raw:=/zed2i/zed_node/right/image_rect_color > ../log_cam2.txt 2>&1 &
PID2=$!
cd ..

# 5. Launch Camera 3
echo "Starting Camera 3 pipeline..."
cd out_cam3
ros2 run orbslam3_ros2 mono --ros-args -p vocab_path:=../$ORB_VOCAB -p config_path:=../$CONFIG_CAM3 --remap /camera/image_raw:=/zed2i/zed_node/center/image_rect_color > ../log_cam3.txt 2>&1 &
PID3=$!
cd ..

echo "----------------------------------------------------"
echo "Pipelines are running!"
if [ "$MODE" = "live" ]; then
    echo "Walk around with your scanner now."
else
    echo "If running a bag file, let it finish playing."
fi
echo "Press [ENTER] when you are ready to stop tracking and evaluate..."
read -r

# 6. Gracefully kill nodes to trigger trajectory saves
echo "Sending shutdown signals to save trajectories..."
kill -SIGINT $PID1 $PID2 $PID3

if [ "$MODE" = "live" ]; then
    kill -SIGINT $LIDAR_PID
fi

echo "Waiting for trajectories to be written to disk..."
while true; do
    # Check that all 3 camera logs confirm the trajectory was saved
    if grep -q "Saving camera trajectory" log_cam1.txt && \
       grep -q "Saving camera trajectory" log_cam2.txt && \
       grep -q "Saving camera trajectory" log_cam3.txt; then
        
        # If in live mode, also wait for the LiDAR trajectory file to appear on disk
        if [ "$MODE" = "live" ]; then
            if [ -f "$GT_FILE" ]; then
                echo "✅ All trajectory data and live LiDAR GT captured."
                break
            fi
        else
            echo "✅ All camera trajectory data successfully captured."
            break
        fi
    fi
    sleep 1
done

# 7. Extract and rename the trajectories
mv out_cam1/CameraTrajectory.txt ./Trajectory_cam1.txt
mv out_cam2/CameraTrajectory.txt ./Trajectory_cam2.txt
mv out_cam3/CameraTrajectory.txt ./Trajectory_cam3.txt

# Clean up the temporary empty folders
rm -rf out_cam1 out_cam2 out_cam3

echo "----------------------------------------------------"
echo "Running automated metrics evaluation..."

# 8. Pass everything into the Python script
python3 evaluate_run.py \
    --logs log_cam1.txt log_cam2.txt log_cam3.txt \
    --ests Trajectory_cam1.txt Trajectory_cam2.txt Trajectory_cam3.txt \
    --gt $GT_FILE \
    --out final_report.json

echo "Done! Check final_report.json for your baseline metrics."