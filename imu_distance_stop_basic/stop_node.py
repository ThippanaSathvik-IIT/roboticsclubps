import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Imu


class DistanceStopNode(Node):
    def __init__(self):
        super().__init__('distance_stop_node')

        self.target_distance = 10.0
        self.speed = 0.2
        self.position = [0.0, 0.0]
        self.velocity = [0.0, 0.0]
        self.previous_stamp = None
        self.finished = False

        self.create_subscription(Imu, '/imu', self.read_imu, qos_profile_sensor_data)
        self.velocity_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_timer(0.1, self.send_command)

    def read_imu(self, msg):
        if self.finished:
            return

        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        if self.previous_stamp is None:
            self.previous_stamp = stamp
            return

        dt = stamp - self.previous_stamp
        self.previous_stamp = stamp
        if dt <= 0:
            return

        q = msg.orientation
        yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z),
        )

        ax = msg.linear_acceleration.x
        ay = msg.linear_acceleration.y
        world_ax = ax * math.cos(yaw) - ay * math.sin(yaw)
        world_ay = ax * math.sin(yaw) + ay * math.cos(yaw)

        self.velocity[0] += world_ax * dt
        self.velocity[1] += world_ay * dt
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt

    def send_command(self):
        distance = math.hypot(*self.position)
        if distance >= self.target_distance:
            self.finished = True

        command = Twist()
        command.linear.x = 0.0 if self.finished else self.speed
        self.velocity_pub.publish(command)
        self.get_logger().info(f'IMU distance: {distance:.2f} m')


def main(args=None):
    rclpy.init(args=args)
    node = DistanceStopNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.velocity_pub.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
