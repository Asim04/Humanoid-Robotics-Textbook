#!/usr/bin/env python3
"""
File: sensor_fusion_example.py
Purpose: Demonstrates sensor fusion techniques using multiple sensor inputs
Chapter: 4 - Sensors and Perception
Dependencies: rclpy, sensor_msgs, geometry_msgs
Hardware: IMU, Camera, LiDAR (simulation)
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, PointCloud2, Image
from geometry_msgs.msg import Vector3
from std_msgs.msg import Float64
import numpy as np
from scipy.spatial.transform import Rotation as R


class SensorFusionNode(Node):
    """
    A node that demonstrates sensor fusion by combining data from multiple sensors
    to estimate robot state more accurately than any single sensor could provide.
    """

    def __init__(self):
        super().__init__('sensor_fusion_node')

        # Initialize state variables
        self.orientation = np.array([0.0, 0.0, 0.0, 1.0])  # Quaternion [x, y, z, w]
        self.angular_velocity = np.array([0.0, 0.0, 0.0])  # [x, y, z] in rad/s
        self.linear_acceleration = np.array([0.0, 0.0, 0.0])  # [x, y, z] in m/s^2
        self.position = np.array([0.0, 0.0, 0.0])  # [x, y, z] in meters
        self.velocity = np.array([0.0, 0.0, 0.0])  # [x, y, z] in m/s

        # Initialize sensor data timestamps
        self.imu_timestamp = self.get_clock().now()
        self.lidar_timestamp = self.get_clock().now()
        self.camera_timestamp = self.get_clock().now()

        # Create subscribers for different sensor types
        self.imu_sub = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )

        self.lidar_sub = self.create_subscription(
            PointCloud2,
            '/lidar/points',
            self.lidar_callback,
            10
        )

        self.camera_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.camera_callback,
            10
        )

        # Create publishers for fused data
        self.fused_orientation_pub = self.create_publisher(
            Vector3,
            '/fused/orientation_euler',
            10
        )

        self.fused_position_pub = self.create_publisher(
            Vector3,
            '/fused/position',
            10
        )

        # Timer for publishing fused data
        self.timer = self.create_timer(0.1, self.publish_fused_data)  # 10 Hz

        self.get_logger().info('Sensor fusion node initialized')

    def imu_callback(self, msg):
        """Process IMU data and update orientation estimate."""
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

        self.imu_timestamp = msg.header.stamp
        self.get_logger().debug('IMU data received and processed')

    def lidar_callback(self, msg):
        """Process LiDAR data and update position estimate."""
        # In a real implementation, this would process point cloud data
        # For this example, we'll simulate position updates from LiDAR
        # based on the number of points and some simple heuristics

        # Update timestamp
        self.lidar_timestamp = msg.header.stamp
        self.get_logger().debug('LiDAR data received')

        # In a real implementation, this would use point cloud processing
        # to estimate position relative to environment features

    def camera_callback(self, msg):
        """Process camera data and update position/pose estimate."""
        # In a real implementation, this would process image data
        # for visual odometry, feature tracking, etc.

        # Update timestamp
        self.camera_timestamp = msg.header.stamp
        self.get_logger().debug('Camera data received')

        # In a real implementation, this would use computer vision
        # techniques to estimate motion/position

    def publish_fused_data(self):
        """Publish the fused sensor data."""
        # Create and publish fused orientation (converted to Euler angles)
        orientation_msg = Vector3()
        r = R.from_quat(self.orientation)
        euler = r.as_euler('xyz')
        orientation_msg.x = euler[0]  # Roll
        orientation_msg.y = euler[1]  # Pitch
        orientation_msg.z = euler[2]  # Yaw
        self.fused_orientation_pub.publish(orientation_msg)

        # Create and publish fused position
        position_msg = Vector3()
        position_msg.x = self.position[0]
        position_msg.y = self.position[1]
        position_msg.z = self.position[2]
        self.fused_position_pub.publish(position_msg)

        self.get_logger().info(
            f'Fused data - Orientation (RPY): [{orientation_msg.x:.3f}, {orientation_msg.y:.3f}, {orientation_msg.z:.3f}], '
            f'Position: [{position_msg.x:.3f}, {position_msg.y:.3f}, {position_msg.z:.3f}]'
        )


def main(args=None):
    rclpy.init(args=args)

    sensor_fusion_node = SensorFusionNode()

    try:
        rclpy.spin(sensor_fusion_node)
    except KeyboardInterrupt:
        pass
    finally:
        sensor_fusion_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()