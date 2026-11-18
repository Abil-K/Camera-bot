# Validation record

Date: 18 November 2026.

## Completed checks

- Guest OS inspected in the terminal: Ubuntu 24.04.4 LTS.
- Host: Oracle VirtualBox 7.2.6, virtual machine `dimka`.
- Camera attached through VirtualBox: USB2.0 HD UVC WebCam.
- `v4l2-ctl --list-formats-ext` returned Motion-JPEG capture modes.
- `v4l2-ctl --stream-mmap --stream-count=10` returned ten frame markers and exited to the shell without an error. This verifies Linux capture, not ROS image publication or gesture recognition.
- Eight command-gating unit tests passed with Python 3.10.14 on Windows.
- All eight original Python source files parsed successfully.
- The technical report opened successfully in Microsoft Word, with five pages.
- ROS 2 Jazzy, Gazebo and TurtleBot3 system packages installed successfully in Ubuntu (`SYSTEM_PACKAGES_READY`).
- All three simulation packages built successfully with colcon.
- MediaPipe 0.10.21 and its gesture model installed; ROS and vision imports passed.
- The same eight command-gating tests passed in the Ubuntu project environment (8 tests in 0.002 seconds).
- The demo displayed live camera frames with hand landmarks and a TurtleBot3 Burger model in Gazebo.
- Live forward test: `Pointing_Up`, confidence 0.86, linear command +0.10 m/s, angular command 0.00 rad/s; forward movement was observed in Gazebo.
- Hand-removal test while enabled: the preview changed to `NO HAND` and both velocity components became zero; the model stopped.
- Live backward test: `Victory`, confidence 0.88, linear command -0.10 m/s and angular command 0.00 rad/s; reverse movement was observed in Gazebo.
- Live left-turn command: `Thumb_Up`, confidence 0.72, linear command 0.00 m/s and angular command +0.45 rad/s.
- Live right-turn test: `Thumb_Down`, confidence 0.84, linear command 0.00 m/s and angular command -0.45 rad/s; rotation of the model was observed in Gazebo.
- Manual STOP: clicking STOP/DISABLE changed the preview from ENABLED to STOPPED. `/gesture/status` reported `enabled: false`; an independent `ros2 topic echo /cmd_vel --once` returned zero for all linear and angular components.
- `ros2 node list` showed `/camera_publisher`, `/gesture_robot_controller`, `/robot_state_publisher` and `/ros_gz_bridge`.
- `ros2 topic list -t` confirmed `/camera/image_raw` as `sensor_msgs/msg/Image`, `/cmd_vel` as `geometry_msgs/msg/TwistStamped` and `/gesture/status` as `std_msgs/msg/String`.
- `timeout 8 ros2 topic hz /camera/image_raw` reported averages of 9.972, 9.981 and 10.001 Hz. The last displayed window was 32, with minimum interval 0.089 s, maximum 0.111 s and standard deviation 0.00569 s. This was a short observation, not a long-duration benchmark.
- Gazebo showed real-time factors around 0.31-0.41 during observed intervals; the simulation ran slower than wall time.

## Limits of this validation

- Webcam unplug/reconnect and precise end-to-end stop latency were not measured live. Stale-data handling was tested in the command-gating unit tests.
- The left-turn command was read from the live interface; left rotation was not separately measured. Right rotation, forward and backward motion were visually observed.
- Confidence values are individual model outputs. Recognition accuracy across repeated trials, lighting conditions or people was not measured.
- No physical robot was connected. These observations apply to the simulated TurtleBot3 only.

This file records direct observations and manual transcriptions from the running guest. It is not an exported raw test log. Runtime logs remain in `/home/dimka/ros_camera_robot/logs` inside Ubuntu.
