# IMU Distance Stopper

This is a small ROS 2 Python project. The idea is to move a robot forward in Gazebo and stop it once the distance **estimated from the IMU** reaches 10 metres.

The important word here is *estimated*. An IMU doesn't tell us the robot's position directly. I calculate it from acceleration, so the result can drift quite a lot.

## What the node does

The node listens to `/imu` and sends commands on `/cmd_vel`. It reads the IMU timestamp to work out the time between samples, uses the orientation to rotate horizontal acceleration into the world frame, and integrates that acceleration to estimate velocity and position.

The distance from the starting point is calculated as:

`distance = sqrt(x*x + y*y)`

The robot is commanded to move forward at `0.2 m/s` while that estimate is below `10 m`. Once it reaches the limit, the node keeps publishing a zero-velocity command. The printed distance also stops updating at that point.

## Requirements

- Ubuntu with ROS 2 Humble
- Gazebo Classic and the ROS-Gazebo integration
- TurtleBot3 Burger model available locally
- Python 3

## Build

Copy the `imu_distance_stop_basic` folder into `~/ros2_ws/src/`, then run:

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
colcon build --packages-select imu_distance_stop_basic
source install/setup.bash
```

## Run

Start Gazebo in a terminal:

```bash
source /opt/ros/humble/setup.bash
gzserver --verbose -s libgazebo_ros_init.so -s libgazebo_ros_factory.so
```

In another terminal, spawn the robot:

```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 run gazebo_ros spawn_entity.py -entity burger -file /opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_burger/model.sdf -x 0 -y 0 -z 0.01
```

Then run the node:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run imu_distance_stop_basic stop_node
```

To inspect the simulated odometry separately:

```bash
ros2 topic echo /odom --once
```

**Note:** `/odom` is only for checking the result. The stop decision in `stop_node.py` uses IMU data, not odometry.

## Test notes

I still need to run and record a clean test of this version. The things to record are:

- Starting odometry position: ______
- Final odometry position: ______
- IMU estimate when it stopped: ______
- Actual displacement based on odometry: ______
- Difference between the target (10 m) and actual displacement: ______

## What I would improve

The code uses basic numerical integration and doesn't estimate or remove accelerometer bias. Small errors build up after integrating twice. It also only uses yaw for the acceleration rotation, which is a simplification suitable for a flat-ground experiment, not a full 3D solution. Better calibration and orientation handling would be worth trying next.

This is a basic experiment, not an accurate localization system.
