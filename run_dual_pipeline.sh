#!/bin/bash

# Define paths (Update these when deploying to the Orin)
ORB_VOCAB="Vocabulary/ORBvoc.txt"
STEREO_EXEC="./Examples/Stereo/stereo_euroc"# Swap to stereo_inertial if using IMU

CONFIG_LEFT="config_pair_left.yaml"
CONFIG_RIGHT="config_pair_right.yaml"

# Placeholders for input streams/datasets
# (For live deployment, these will be your camera device paths or ROS topics)
DATASET_LEFT_PATH="/path/to/left_pair_data"
DATASET_RIGHT_PATH="/path/to/right_pair_data"

echo "=== Launching Dual Stereo Pipelines ==="

# 1. Launch Left+Center Camera Pipeline (Camera 1 & 2)
echo "Starting Left Pair Pipeline (Camera 1 + 2)..."
$STEREO_EXEC $ORB_VOCAB $CONFIG_LEFT $DATASET_LEFT_PATH > log_pipeline_left.txt 2>&1 &
PID_LEFT=$!

# 2. Launch Center+Right Camera Pipeline (Camera 2 & 3)
echo "Starting Right Pair Pipeline (Camera 2 + 3)..."
$STEREO_EXEC $ORB_VOCAB $CONFIG_RIGHT $DATASET_RIGHT_PATH > log_pipeline_right.txt 2>&1 &
PID_RIGHT=$!

echo "---------------------------------------"
echo "Both pipelines are running in the background!"
echo "Left Pair PID:  $PID_LEFT  (Logging to log_pipeline_left.txt)"
echo "Right Pair PID: $PID_RIGHT (Logging to log_pipeline_right.txt)"
echo "---------------------------------------"
echo "Press Ctrl+C to stop both pipelines."

# Trap Ctrl+C to clean up and kill both background processes safely
trap "echo -e '\nStopping pipelines...'; kill $PID_LEFT $PID_RIGHT 2>/dev/null; exit" INT

# Keep script alive while pipelines run
wait
