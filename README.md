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

I tested the code in Gazebo using the TurtleBot3 Burger robot. I started the robot close to (0, 0) and let it move until the IMU-estimated distance reached 10 m.

These are the readings I got:

Starting odometry position: (0.000062, -0.00000456)

Final odometry position: (4.603687, -0.00009509)

IMU estimate when it stopped: 10.03 m

Actual displacement based on odometry: 4.6036 m

Difference between IMU estimate and odometry: 5.4264 m

Difference between the 10 m target and actual displacement: 5.3964 m

Error relative to the target: 53.96%

What happened

The robot stopped when the estimated distance reached 10.03 m, so the stopping condition worked as expected.

But when I checked the odometry, the robot had actually travelled only around 4.6 m. The difference was much larger than I initially expected.

I think the main issue is the double integration of acceleration. Small errors in the IMU readings keep accumulating, and that affects the final position estimate quite a lot.

For now, the basic stopping logic works, but the distance estimation needs improvement. I would probably try accelerometer bias correction or some filtering method if I were to work on this further.

## What I would improve
<img width="1600" height="832" alt="image_1" src="https://github.com/user-attachments/assets/3426b179-6937-4045-9a17-c91914e842d4" />


The code uses basic numerical integration and doesn't estimate or remove accelerometer bias. Small errors build up after integrating twice. It also only uses yaw for the acceleration rotation, which is a simplification suitable for a flat-ground experiment, not a full 3D solution. Better calibration and orientation handling would be worth trying next.

This is a basic experiment, not an accurate localization system.
