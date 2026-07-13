#!/bin/bash

# Configuration Paths
STEREO_EXEC="./Examples/Stereo/stereo_euroc"
ORB_VOCAB="./Vocabulary/ORBvoc.txt"
CONFIG_LEFT="config_pair_left.yaml"
CONFIG_RIGHT="config_pair_right.yaml"
DATASET_LEFT_PATH="Datasets/MH01"
DATASET_RIGHT_PATH="Datasets/MH01"

echo "=== Launching Dual Stereo Pipelines (EuRoC Test) ==="
echo "---------------------------------------"

# Launch Left Pipeline in background
$STEREO_EXEC $ORB_VOCAB $CONFIG_LEFT $DATASET_LEFT_PATH ./Examples/Stereo/EuRoC_TimeStamps/MH01.txt > log_pipeline_left.txt 2>&1 &
LEFT_PID=$!
echo "Left Pair PID:  $LEFT_PID"

# Launch Right Pipeline in background
$STEREO_EXEC $ORB_VOCAB $CONFIG_RIGHT $DATASET_RIGHT_PATH ./Examples/Stereo/EuRoC_TimeStamps/MH01.txt > log_pipeline_right.txt 2>&1 &
RIGHT_PID=$!
echo "Right Pair PID: $RIGHT_PID"
echo "---------------------------------------"

echo "Waiting for both SLAM pipelines to complete..."
# Wait for both background processes to finish safely
wait $LEFT_PID
wait $RIGHT_PID

echo "Pipelines finished. Running automated metrics evaluation..."
# Run the evaluation script automatically
python3 evaluate_run.py

echo "Evaluation complete! Check report.json for metrics."
