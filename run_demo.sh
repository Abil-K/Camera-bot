#!/usr/bin/env bash
set -eo pipefail
cd "$(dirname "$0")"
export ROS_GESTURE_ROOT="$PWD"
export ROS_DOMAIN_ID=37
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export TURTLEBOT3_MODEL=burger
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
source /opt/ros/jazzy/setup.bash
source simulation_ws/install/setup.bash
exec .venv/bin/python run_demo.py "$@"
