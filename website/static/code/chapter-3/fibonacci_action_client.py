#!/usr/bin/env python3
"""
File: fibonacci_action_client.py
Purpose: Demonstrates a minimal ROS 2 action client
Chapter: 3 - ROS 2 Architecture & Core Concepts
Dependencies: rclpy, action_msgs, example_interfaces
Hardware: None (simulation)
"""

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciActionClient(Node):

    def __init__(self):
        super().__init__('fibonacci_action_client')
        self._action_client = ActionClient(
            self,
            Fibonacci,
            'fibonacci')

    def send_goal(self, order):
        # Wait for the action server to be available
        self.get_logger().info('Waiting for action server...')
        self._action_client.wait_for_server()

        # Create a goal
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        # Send the goal
        self.get_logger().info(f'Sending goal with order: {order}')
        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)

        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')

        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: {result.sequence}')
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Received feedback: {feedback.sequence}')


def main(args=None):
    rclpy.init(args=args)

    action_client = FibonacciActionClient()

    # Send a goal to calculate Fibonacci sequence of order 10
    action_client.send_goal(10)

    rclpy.spin(action_client)


if __name__ == '__main__':
    main()