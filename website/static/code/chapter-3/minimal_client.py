#!/usr/bin/env python3
"""
File: minimal_client.py
Purpose: Demonstrates a minimal ROS 2 service client
Chapter: 3 - ROS 2 Architecture & Core Concepts
Dependencies: rclpy, example_interfaces
Hardware: None (simulation)
"""

import sys
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class MinimalClient(Node):

    def __init__(self):
        super().__init__('minimal_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')
        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a = a
        self.req.b = b
        future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()


def main(args=None):
    rclpy.init(args=args)

    minimal_client = MinimalClient()
    response = minimal_client.send_request(int(sys.argv[1]), int(sys.argv[2]))

    if response is not None:
        print(f'Result of add_two_ints: {response.sum}')
    else:
        print('Service call failed')

    minimal_client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()