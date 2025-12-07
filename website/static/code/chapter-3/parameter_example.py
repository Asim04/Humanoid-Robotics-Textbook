#!/usr/bin/env python3
"""
File: parameter_example.py
Purpose: Demonstrates ROS 2 parameter usage
Chapter: 3 - ROS 2 Architecture & Core Concepts
Dependencies: rclpy
Hardware: None (simulation)
"""

import rclpy
from rclpy.node import Node


class ParameterExample(Node):

    def __init__(self):
        super().__init__('parameter_example')

        # Declare parameters with default values
        self.declare_parameter('robot_name', 'turtlebot')
        self.declare_parameter('max_velocity', 1.0)
        self.declare_parameter('sensors_enabled', True)

        # Get parameter values
        robot_name = self.get_parameter('robot_name').value
        max_velocity = self.get_parameter('max_velocity').value
        sensors_enabled = self.get_parameter('sensors_enabled').value

        self.get_logger().info(f'Robot name: {robot_name}')
        self.get_logger().info(f'Max velocity: {max_velocity}')
        self.get_logger().info(f'Sensors enabled: {sensors_enabled}')

        # Set a parameter callback to handle parameter changes
        self.add_on_set_parameters_callback(self.parameter_callback)

    def parameter_callback(self, params):
        for param in params:
            self.get_logger().info(f'Parameter {param.name} changed to {param.value}')
        return rclpy.node.SetParametersResult(successful=True)


def main(args=None):
    rclpy.init(args=args)

    parameter_example = ParameterExample()

    # Print current parameters
    print("\nCurrent parameters:")
    for param_name in ['robot_name', 'max_velocity', 'sensors_enabled']:
        param_value = parameter_example.get_parameter(param_name).value
        print(f"  {param_name}: {param_value}")

    rclpy.spin(parameter_example)

    # Destroy the node explicitly
    parameter_example.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()