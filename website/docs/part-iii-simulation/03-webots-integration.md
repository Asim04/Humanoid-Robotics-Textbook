---
sidebar_position: 3
---

# Webots Integration

## Introduction

Webots is an open-source robot simulation software that provides a complete development environment for fast robot prototyping, simulation, and programming. It offers realistic physics simulation, 3D visualization, and native ROS 2 support, making it an excellent choice for robotics education and development.

## Webots ROS 2 Interface

Webots provides the `webots_ros2` package that enables seamless integration with ROS 2. This package includes:

- **webots_ros2_core**: Core ROS 2 interface
- **webots_ros2_driver**: Robot driver framework
- **webots_ros2_control**: ros_control integration
- **webots_ros2_tutorials**: Example implementations

## Setting Up Webots with ROS 2

### 1. Robot Description in Webots

Webots uses its own robot description format, but it can work with URDF models. Here's a basic controller template:

```python
#!/usr/bin/env python3
"""
Webots ROS 2 Controller for My Robot
"""

import rclpy
from webots_ros2_core.webots_node import WebotsNode
from sensor_msgs.msg import LaserScan, Imu, JointState
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import numpy as np


class MyRobotController(WebotsNode):
    def __init__(self):
        super().__init__('my_robot_controller')

        # Create subscribers
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            'cmd_vel',
            self.cmd_vel_callback,
            10
        )

        # Create publishers
        self.laser_pub = self.create_publisher(LaserScan, 'scan', 10)
        self.imu_pub = self.create_publisher(Imu, 'imu', 10)
        self.joint_state_pub = self.create_publisher(JointState, 'joint_states', 10)

        # Get devices
        self.left_motor = self.robot.getDevice('left_wheel_motor')
        self.right_motor = self.robot.getDevice('right_wheel_motor')
        self.lidar = self.robot.getDevice('lidar')
        self.imu = self.robot.getDevice('imu')

        # Enable devices
        self.lidar.enable(self.timestep)
        self.imu.enable(self.timestep)

        # Set motor parameters
        self.left_motor.setPosition(float('inf'))
        self.right_motor.setPosition(float('inf'))
        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)

        # Timer for publishing sensor data
        self.timer = self.create_timer(0.1, self.publish_sensor_data)

    def cmd_vel_callback(self, msg):
        """Handle velocity commands."""
        linear_vel = msg.linear.x
        angular_vel = msg.angular.z

        # Convert differential drive kinematics
        wheel_radius = 0.05  # meters
        wheel_separation = 0.3  # meters

        left_wheel_vel = (linear_vel - angular_vel * wheel_separation / 2) / wheel_radius
        right_wheel_vel = (linear_vel + angular_vel * wheel_separation / 2) / wheel_radius

        self.left_motor.setVelocity(left_wheel_vel)
        self.right_motor.setVelocity(right_wheel_vel)

    def publish_sensor_data(self):
        """Publish sensor data from Webots."""
        # Publish laser scan
        if self.lidar is not None:
            ranges = self.lidar.getRangeImage()
            scan_msg = LaserScan()
            scan_msg.header.stamp = self.get_clock().now().to_msg()
            scan_msg.header.frame_id = 'lidar_link'
            scan_msg.angle_min = -np.pi / 2
            scan_msg.angle_max = np.pi / 2
            scan_msg.angle_increment = np.pi / len(ranges)
            scan_msg.range_min = 0.01
            scan_msg.range_max = 10.0
            scan_msg.ranges = [float(r) for r in ranges]
            self.laser_pub.publish(scan_msg)

        # Publish IMU data
        if self.imu is not None:
            imu_data = self.imu.getRollPitchYaw()
            imu_msg = Imu()
            imu_msg.header.stamp = self.get_clock().now().to_msg()
            imu_msg.header.frame_id = 'imu_link'
            # Convert RPY to quaternion
            from math import sin, cos
            roll, pitch, yaw = imu_data
            cy = cos(yaw * 0.5)
            sy = sin(yaw * 0.5)
            cp = cos(pitch * 0.5)
            sp = sin(pitch * 0.5)
            cr = cos(roll * 0.5)
            sr = sin(roll * 0.5)

            imu_msg.orientation.w = cr * cp * cy + sr * sp * sy
            imu_msg.orientation.x = sr * cp * cy - cr * sp * sy
            imu_msg.orientation.y = cr * sp * cy + sr * cp * sy
            imu_msg.orientation.z = cr * cp * sy - sr * sp * cy
            self.imu_pub.publish(imu_msg)


def main(args=None):
    rclpy.init(args=args)
    controller = MyRobotController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()