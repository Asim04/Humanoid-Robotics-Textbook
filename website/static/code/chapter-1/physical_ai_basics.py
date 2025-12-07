#!/usr/bin/env python3
"""
File: physical_ai_basics.py
Purpose: Demonstrates basic Physical AI concepts with a simple ROS 2 node
Chapter: 1 - Introduction to Physical AI
Dependencies: rclpy, std_msgs
Hardware: None (simulation)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time


class PhysicalAINode(Node):
    """
    A basic ROS 2 node that demonstrates Physical AI concepts:
    - Real-time processing (publishing at fixed intervals)
    - Multi-modal sensing (would integrate with sensors in real implementation)
    - Embodied cognition (reacting to environment - simulated here)
    """

    def __init__(self):
        super().__init__('physical_ai_node')

        # Publisher for system status
        self.status_publisher = self.create_publisher(String, 'physical_ai/status', 10)

        # Publisher for sensor data (simulated)
        self.sensor_publisher = self.create_publisher(String, 'physical_ai/sensors', 10)

        # Timer for periodic publishing (real-time processing)
        self.timer = self.create_timer(1.0, self.timer_callback)

        # Simulated sensor data
        self.sensor_data = {
            'timestamp': time.time(),
            'environment_state': 'normal',
            'safety_status': 'safe'
        }

        self.get_logger().info('Physical AI node initialized')
        self.get_logger().info('Demonstrating: Real-time constraints, Multi-modal sensing, Safety considerations')

    def timer_callback(self):
        """
        Callback that runs at fixed intervals to simulate real-time processing
        """
        # Update simulated sensor data
        self.sensor_data['timestamp'] = time.time()

        # Publish status message
        status_msg = String()
        status_msg.data = f"Physical AI System Status: {self.sensor_data['environment_state']}, Safety: {self.sensor_data['safety_status']}"
        self.status_publisher.publish(status_msg)

        # Publish sensor data
        sensor_msg = String()
        sensor_msg.data = f"Simulated Sensor Data: {self.sensor_data}"
        self.sensor_publisher.publish(sensor_msg)

        self.get_logger().info(f'Status published: {status_msg.data}')


def main(args=None):
    """
    Main entry point for the Physical AI node.
    Demonstrates the core components of Physical AI systems:
    - Perception System: Simulated sensor data
    - Cognition System: Decision making based on environment state
    - Action System: Publishing status updates
    """
    rclpy.init(args=args)
    node = PhysicalAINode()

    try:
        print("Physical AI node running...")
        print("Demonstrating core Physical AI concepts:")
        print("- Real-time constraints (publishing every 1 second)")
        print("- Uncertainty and noise (simulated in sensor data)")
        print("- Embodiment (simulated interaction with environment)")
        print("- Safety considerations (safety status monitoring)")
        print("\nPress Ctrl+C to stop...")

        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\nShutting down Physical AI node...")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()