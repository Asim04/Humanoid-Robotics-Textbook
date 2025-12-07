#!/usr/bin/env python3
"""
File: imu_proprioception.py
Purpose: Demonstrates IMU data processing and proprioceptive sensing
Chapter: 4 - Sensors and Perception
Dependencies: rclpy, sensor_msgs, geometry_msgs
Hardware: IMU, Joint Position Sensors (simulation)
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, JointState
from geometry_msgs.msg import Vector3, Quaternion
from std_msgs.msg import Float64MultiArray
import numpy as np
from scipy.spatial.transform import Rotation as R
import math


class IMUProprioceptionNode(Node):
    """
    A node that processes IMU data and joint state information to provide
    proprioceptive awareness of the robot's state in space.
    """

    def __init__(self):
        super().__init__('imu_proprioception_node')

        # Initialize robot state
        self.orientation = np.array([0.0, 0.0, 0.0, 1.0])  # Quaternion [x, y, z, w]
        self.angular_velocity = np.array([0.0, 0.0, 0.0])  # [x, y, z] in rad/s
        self.linear_acceleration = np.array([0.0, 0.0, 0.0])  # [x, y, z] in m/s^2
        self.joint_positions = {}
        self.joint_velocities = {}
        self.joint_efforts = {}

        # Initialize orientation filter (simple complementary filter)
        self.filtered_orientation = np.array([0.0, 0.0, 0.0, 1.0])
        self.gravity_vector = np.array([0.0, 0.0, -9.81])  # Gravity in world frame

        # Create subscribers for IMU and joint state
        self.imu_sub = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )

        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )

        # Create publishers for processed data
        self.attitude_pub = self.create_publisher(
            Vector3,
            '/robot/attitude',
            10
        )

        self.balance_pub = self.create_publisher(
            Float64MultiArray,
            '/robot/balance_metrics',
            10
        )

        self.center_of_mass_pub = self.create_publisher(
            Vector3,
            '/robot/center_of_mass',
            10
        )

        # Timer for processing and publishing data
        self.timer = self.create_timer(0.05, self.process_and_publish)  # 20 Hz

        self.get_logger().info('IMU and proprioception node initialized')

    def imu_callback(self, msg):
        """Process IMU data."""
        # Update orientation from quaternion
        self.orientation = np.array([
            msg.orientation.x,
            msg.orientation.y,
            msg.orientation.z,
            msg.orientation.w
        ])

        # Update angular velocity and linear acceleration
        self.angular_velocity = np.array([
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z
        ])

        self.linear_acceleration = np.array([
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z
        ])

        # Apply simple complementary filter to combine gyroscope and accelerometer data
        self.update_orientation_filter(msg)

        self.get_logger().debug('IMU data processed')

    def joint_state_callback(self, msg):
        """Process joint state data."""
        for i, name in enumerate(msg.name):
            if i < len(msg.position):
                self.joint_positions[name] = msg.position[i]
            if i < len(msg.velocity):
                self.joint_velocities[name] = msg.velocity[i]
            if i < len(msg.effort):
                self.joint_efforts[name] = msg.effort[i]

        self.get_logger().debug(f'Joint states updated: {len(msg.name)} joints')

    def update_orientation_filter(self, imu_msg):
        """Update orientation using a simple complementary filter."""
        dt = 0.05  # Time step (from timer)

        # Convert quaternion to rotation matrix to work with accelerometer data
        quat = np.array([
            imu_msg.orientation.x,
            imu_msg.orientation.y,
            imu_msg.orientation.z,
            imu_msg.orientation.w
        ])

        # Get rotation matrix from quaternion
        r = R.from_quat(quat)

        # Get gravity vector in sensor frame (from accelerometer)
        acc_sensor = np.array([
            imu_msg.linear_acceleration.x,
            imu_msg.linear_acceleration.y,
            imu_msg.linear_acceleration.z
        ])

        # Normalize to get direction
        if np.linalg.norm(acc_sensor) > 0.1:  # Only if significant acceleration
            acc_normalized = acc_sensor / np.linalg.norm(acc_sensor)

            # Transform to world frame to get gravity direction
            gravity_world = r.apply(acc_normalized)

            # Simple complementary filter
            alpha = 0.9  # Weight for gyroscope integration
            # This is a simplified version - in practice, you'd integrate gyroscope data
            # and combine with accelerometer data

            # For this example, we'll just blend the orientations
            self.filtered_orientation = quat  # Placeholder for actual filter

    def calculate_balance_metrics(self):
        """Calculate balance-related metrics."""
        balance_metrics = Float64MultiArray()

        # Calculate center of mass based on joint positions
        # This is a simplified calculation - real implementation would use link masses
        com_x = 0.0
        com_y = 0.0
        com_z = 0.0
        total_mass = 1.0  # Simplified - assume unit mass

        # Example: calculate based on some key joints
        if 'left_foot_joint' in self.joint_positions:
            com_x += self.joint_positions['left_foot_joint'] * 0.2
        if 'right_foot_joint' in self.joint_positions:
            com_x += self.joint_positions['right_foot_joint'] * 0.2

        # Calculate stability metrics
        pitch = math.atan2(self.linear_acceleration[0],
                          math.sqrt(self.linear_acceleration[1]**2 + self.linear_acceleration[2]**2))
        roll = math.atan2(-self.linear_acceleration[1], self.linear_acceleration[2])

        balance_metrics.data = [
            pitch,      # Pitch angle
            roll,       # Roll angle
            self.linear_acceleration[0],  # X acceleration
            self.linear_acceleration[1],  # Y acceleration
            self.linear_acceleration[2],  # Z acceleration
            com_x,      # Center of mass X
            com_y,      # Center of mass Y
            com_z       # Center of mass Z
        ]

        return balance_metrics

    def process_and_publish(self):
        """Process all sensor data and publish results."""
        # Publish attitude (roll, pitch, yaw)
        attitude_msg = Vector3()
        r = R.from_quat(self.orientation)
        euler = r.as_euler('xyz')
        attitude_msg.x = euler[0]  # Roll
        attitude_msg.y = euler[1]  # Pitch
        attitude_msg.z = euler[2]  # Yaw
        self.attitude_pub.publish(attitude_msg)

        # Publish balance metrics
        balance_metrics = self.calculate_balance_metrics()
        self.balance_pub.publish(balance_metrics)

        # Publish center of mass estimate
        com_msg = Vector3()
        # Simplified center of mass calculation
        com_msg.x = balance_metrics.data[5] if len(balance_metrics.data) > 5 else 0.0
        com_msg.y = balance_metrics.data[6] if len(balance_metrics.data) > 6 else 0.0
        com_msg.z = balance_metrics.data[7] if len(balance_metrics.data) > 7 else 0.0
        self.center_of_mass_pub.publish(com_msg)

        self.get_logger().info(
            f'Attitude (RPY): [{attitude_msg.x:.3f}, {attitude_msg.y:.3f}, {attitude_msg.z:.3f}], '
            f'COM: [{com_msg.x:.3f}, {com_msg.y:.3f}, {com_msg.z:.3f}]'
        )


def main(args=None):
    rclpy.init(args=args)

    imu_proprioception_node = IMUProprioceptionNode()

    try:
        rclpy.spin(imu_proprioception_node)
    except KeyboardInterrupt:
        pass
    finally:
        imu_proprioception_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()