#!/usr/bin/env python3
"""
File: composition_example.py
Purpose: Demonstrates ROS 2 composition (components)
Chapter: 3 - ROS 2 Architecture & Core Concepts
Dependencies: rclpy, std_msgs
Hardware: None (simulation)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimpleComponent(Node):
    """
    A simple component that can be composed into a single process.
    This demonstrates the composition pattern in ROS 2 where multiple
    nodes can run in the same process for better performance.
    """

    def __init__(self, name='simple_component'):
        super().__init__(name)

        # Create publisher and subscriber
        self.publisher = self.create_publisher(String, 'composed_topic', 10)
        self.subscription = self.create_subscription(
            String,
            'composed_input',
            self.listener_callback,
            10
        )

        # Create timer for periodic publishing
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.counter = 0

        self.get_logger().info(f'{name} initialized')

    def listener_callback(self, msg):
        """Callback for handling incoming messages."""
        self.get_logger().info(f'Component received: {msg.data}')

        # Echo the message back with a prefix
        response_msg = String()
        response_msg.data = f'Echo: {msg.data}'
        self.publisher.publish(response_msg)

    def timer_callback(self):
        """Timer callback for periodic publishing."""
        msg = String()
        msg.data = f'Component message #{self.counter}'
        self.publisher.publish(msg)
        self.get_logger().info(f'Component published: {msg.data}')
        self.counter += 1


def main(args=None):
    """
    Main function demonstrating composition by creating multiple components
    in a single process.
    """
    rclpy.init(args=args)

    # Create a single executor to manage multiple nodes/components
    executor = rclpy.executors.MultiThreadedExecutor()

    # Create multiple component instances
    component1 = SimpleComponent('component_1')
    component2 = SimpleComponent('component_2')

    # Add nodes to executor
    executor.add_node(component1)
    executor.add_node(component2)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup
        component1.destroy_node()
        component2.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()