#!/bin/bash

ORB_VOCAB="Vocabulary/ORBvoc.txt"
STEREO_EXEC="./Examples/Stereo/stereo_euroc"
CONFIG_LEFT="config_pair_left.yaml"
CONFIG_RIGHT="config_pair_right.yaml"
DATASET_LEFT_PATH="Datasets/MH01"
DATASET_RIGHT_PATH="Datasets/MH01"

echo "=== Launching Dual Stereo Pipelines (EuRoC Test) ==="

$STEREO_EXEC $ORB_VOCAB $CONFIG_LEFT $DATASET_LEFT_PATH ./Examples/Stereo/EuRoC_TimeStamps/MH01.txt > log_pipeline_left.txt 2>&1 &
PID_LEFT=$!

$STEREO_EXEC $ORB_VOCAB $CONFIG_RIGHT $DATASET_RIGHT_PATH ./Examples/Stereo/EuRoC_TimeStamps/MH01.txt > log_pipeline_right.txt 2>&1 &
PID_RIGHT=$!

echo "---------------------------------------"
echo "Both pipelines are running in the background!"
echo "Left Pair PID:  $PID_LEFT"
echo "Right Pair PID: $PID_RIGHT"
echo "---------------------------------------"
echo "Press Ctrl+C to stop both processes."

trap "kill $PID_LEFT $PID_RIGHT 2>/dev/null; exit" INT

wait
