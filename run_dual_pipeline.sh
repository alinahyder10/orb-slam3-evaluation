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
echo "Monitoring logs for trajectory disk writes..."
echo "---------------------------------------"

# Process watcher loop
while true; do
    # Break early if BOTH logs confirm the trajectory file was written to disk
    if grep -q "Saving trajectory to" log_pipeline_left.txt && grep -q "Saving trajectory to" log_pipeline_right.txt; then
        echo "✅ Trajectory data successfully captured from both pipelines."
        break
    fi
    
    # Fallback safety break if both processes completely crash early
    if ! kill -0 $LEFT_PID 2>/dev/null && ! kill -0 $RIGHT_PID 2>/dev/null; then
        echo "Pipelines stopped unexpectedly."
        break
    fi
    sleep 1
done

# Force kill the remaining spinning viewer/zombie threads safely
kill -9 $LEFT_PID $RIGHT_PID 2>/dev/null

echo "Running automated metrics evaluation..."
python3 evaluate_run.py

echo "Done! Check report.json for your baseline metrics."
