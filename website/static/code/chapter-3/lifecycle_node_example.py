#!/usr/bin/env python3
"""
File: lifecycle_node_example.py
Purpose: Demonstrates a ROS 2 lifecycle node
Chapter: 3 - ROS 2 Architecture & Core Concepts
Dependencies: rclpy, lifecycle_msgs
Hardware: None (simulation)
"""

import rclpy
from rclpy.lifecycle import LifecycleNode, TransitionCallbackReturn
from rclpy.lifecycle import State
from std_msgs.msg import String


class LifecycleNodeExample(LifecycleNode):

    def __init__(self):
        super().__init__('lifecycle_node_example')
        self.get_logger().info('Lifecycle node created, current state: unconfigured')

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        """Callback for configuring the node."""
        self.get_logger().info(f'Configuring node, previous state: {state.label}')
        self.pub = self.create_publisher(String, 'lifecycle_chatter', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.counter = 0
        self.timer.cancel()  # Don't start timer until activated
        return TransitionCallbackReturn.SUCCESS

    def on_cleanup(self, state: State) -> TransitionCallbackReturn:
        """Callback for cleaning up the node."""
        self.get_logger().info(f'Cleaning up node, previous state: {state.label}')
        self.destroy_publisher(self.pub)
        self.destroy_timer(self.timer)
        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        """Callback for activating the node."""
        self.get_logger().info(f'Activating node, previous state: {state.label}')
        self.timer.reset()  # Start the timer
        return super().on_activate(state)

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        """Callback for deactivating the node."""
        self.get_logger().info(f'Deactivating node, previous state: {state.label}')
        self.timer.cancel()  # Stop the timer
        return super().on_deactivate(state)

    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        """Callback for shutting down the node."""
        self.get_logger().info(f'Shutting down node, previous state: {state.label}')
        return TransitionCallbackReturn.SUCCESS

    def timer_callback(self):
        """Timer callback to publish messages."""
        msg = String()
        msg.data = f'Lifecycle node message #{self.counter}'
        self.pub.publish(msg)
        self.get_logger().info(f'Published: {msg.data}')
        self.counter += 1


def main(args=None):
    rclpy.init(args=args)

    lifecycle_node = LifecycleNodeExample()

    # In a real application, the lifecycle node would be controlled by a lifecycle manager
    # For this example, we'll just spin and let external tools control the lifecycle
    rclpy.spin(lifecycle_node)

    lifecycle_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()