#!/bin/bash

# Configuration Paths
STEREO_EXEC="./Examples/Stereo/stereo_euroc"
ORB_VOCAB="./Vocabulary/ORBvoc.txt"
CONFIG_LEFT="config_pair_left.yaml"
CONFIG_RIGHT="config_pair_right.yaml"
DATASET_LEFT_PATH="Datasets/MH01"
DATASET_RIGHT_PATH="Datasets/MH01"

echo "=== Launching Dual Headless Stereo Pipelines ==="
echo "---------------------------------------"

# Launch Left Pipeline
xvfb-run -a $STEREO_EXEC $ORB_VOCAB $CONFIG_LEFT $DATASET_LEFT_PATH ./Examples/Stereo/EuRoC_TimeStamps/MH01.txt > log_pipeline_left.txt 2>&1 &
LEFT_PID=$!

# Launch Right Pipeline
xvfb-run -a $STEREO_EXEC $ORB_VOCAB $CONFIG_RIGHT $DATASET_RIGHT_PATH ./Examples/Stereo/EuRoC_TimeStamps/MH01.txt > log_pipeline_right.txt 2>&1 &
RIGHT_PID=$!

echo "Pipelines processing in background..."
echo "Monitoring process lifecycles..."
echo "---------------------------------------"

# Process watcher loop
while true; do
    # Check if both background processes have exited/died
    if ! kill -0 $LEFT_PID 2>/dev/null && ! kill -0 $RIGHT_PID 2>/dev/null; then
        echo "Pipelines have completed execution."
        break
    fi
    sleep 1
done

echo "Running automated metrics evaluation..."
python3 evaluate_run.py

echo "Done! Check report.json for your baseline metrics."
