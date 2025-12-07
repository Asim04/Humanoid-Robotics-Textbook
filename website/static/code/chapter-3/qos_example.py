#!/usr/bin/env python3
"""
File: qos_example.py
Purpose: Demonstrates ROS 2 Quality of Service policies
Chapter: 3 - ROS 2 Architecture & Core Concepts
Dependencies: rclpy, std_msgs
Hardware: None (simulation)
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSHistoryPolicy, QoSReliabilityPolicy
from std_msgs.msg import String


class QoSExamplePublisher(Node):

    def __init__(self):
        super().__init__('qos_example_publisher')

        # Create different QoS profiles to demonstrate various policies
        # 1. Default QoS profile (Reliable, Keep Last 10, Volatile)
        default_qos = rclpy.qos.qos_profile_default
        self.default_publisher = self.create_publisher(String, 'default_topic', default_qos)

        # 2. Reliable communication with Keep All history
        reliable_qos = QoSProfile(
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_ALL,
            durability=QoSDurabilityPolicy.VOLATILE
        )
        self.reliable_publisher = self.create_publisher(String, 'reliable_topic', reliable_qos)

        # 3. Best effort communication with Keep Last history
        best_effort_qos = QoSProfile(
            depth=5,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            durability=QoSDurabilityPolicy.VOLATILE
        )
        self.best_effort_publisher = self.create_publisher(String, 'best_effort_topic', best_effort_qos)

        # 4. Transient local durability (for latching)
        latching_qos = QoSProfile(
            depth=1,
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL
        )
        self.latching_publisher = self.create_publisher(String, 'latching_topic', latching_qos)

        timer_period = 1.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'QoS Example Message: {self.i}'

        # Publish to all topics with different QoS profiles
        self.default_publisher.publish(msg)
        self.reliable_publisher.publish(msg)
        self.best_effort_publisher.publish(msg)
        self.latching_publisher.publish(msg)

        self.get_logger().info(f'Published to all topics: "{msg.data}"')
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    qos_example_publisher = QoSExamplePublisher()

    rclpy.spin(qos_example_publisher)

    # Destroy the node explicitly
    qos_example_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()