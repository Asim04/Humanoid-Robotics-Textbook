#!/usr/bin/env python3
"""
File: controller_example.py
Purpose: Demonstrates various robot controllers (PID, MPC, etc.)
Chapter: 5 - Navigation and Path Planning
Dependencies: rclpy, geometry_msgs, nav_msgs
Hardware: Mobile robot base (simulation)
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped, Point
from nav_msgs.msg import Path, Odometry
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
import numpy as np
from math import sin, cos, atan2, sqrt, pi


class PIDController:
    """Simple PID controller for robot motion control."""

    def __init__(self, kp=1.0, ki=0.0, kd=0.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0.0
        self.integral = 0.0

    def update(self, error, dt):
        """Update PID controller."""
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0

        output = self.kp * error + self.ki * self.integral + self.kd * derivative

        self.prev_error = error
        return output


class ControllerNode(Node):
    """
    A node that demonstrates different control strategies for robot navigation.
    """

    def __init__(self):
        super().__init__('controller_node')

        # Initialize control variables
        self.current_pose = None
        self.target_pose = None
        self.path = []
        self.path_index = 0
        self.linear_vel = 0.0
        self.angular_vel = 0.0

        # Initialize PID controllers
        self.linear_pid = PIDController(kp=1.0, ki=0.1, kd=0.05)
        self.angular_pid = PIDController(kp=2.0, ki=0.1, kd=0.1)

        # TF2 buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Create subscribers
        self.path_sub = self.create_subscription(
            Path,
            '/plan',
            self.path_callback,
            10
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # Create publishers
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Timer for control loop
        self.control_timer = self.create_timer(0.05, self.control_loop)  # 20 Hz

        self.get_logger().info('Controller node initialized')

    def path_callback(self, msg):
        """Handle new path."""
        self.path = msg.poses
        self.path_index = 0
        self.get_logger().info(f'New path received with {len(self.path)} waypoints')

    def odom_callback(self, msg):
        """Handle odometry data."""
        self.current_pose = msg.pose.pose

    def control_loop(self):
        """Main control loop."""
        if self.current_pose is None or len(self.path) == 0:
            return

        # Get current position
        current_x = self.current_pose.position.x
        current_y = self.current_pose.position.y

        # Get target position from path
        if self.path_index < len(self.path):
            target_pose = self.path[self.path_index].pose
            target_x = target_pose.position.x
            target_y = target_pose.position.y

            # Calculate distance to target
            dx = target_x - current_x
            dy = target_y - current_y
            distance = sqrt(dx**2 + dy**2)

            # Check if we've reached the current waypoint
            if distance < 0.3:  # Within 0.3m of waypoint
                self.path_index += 1
                if self.path_index >= len(self.path):
                    # Path completed
                    self.linear_vel = 0.0
                    self.angular_vel = 0.0
                    self.publish_cmd_vel()
                    return

                # Get next target
                if self.path_index < len(self.path):
                    target_pose = self.path[self.path_index].pose
                    target_x = target_pose.position.x
                    target_y = target_pose.position.y
                    dx = target_x - current_x
                    dy = target_y - current_y
                    distance = sqrt(dx**2 + dy**2)

            # Calculate desired heading
            desired_angle = atan2(dy, dx)

            # Get current orientation
            q = self.current_pose.orientation
            current_angle = atan2(2.0 * (q.w * q.z + q.x * q.y),
                                 1.0 - 2.0 * (q.y * q.y + q.z * q.z))

            # Calculate angle error
            angle_error = desired_angle - current_angle
            # Normalize angle error to [-pi, pi]
            while angle_error > pi:
                angle_error -= 2 * pi
            while angle_error < -pi:
                angle_error += 2 * pi

            # Use PID controllers to calculate velocities
            dt = 0.05  # Time step from timer

            # Linear velocity based on distance to target
            linear_error = distance
            self.linear_vel = max(min(self.linear_pid.update(linear_error, dt), 0.5), 0.0)  # Max 0.5 m/s

            # Angular velocity based on angle error
            angular_error = angle_error
            self.angular_vel = max(min(self.angular_pid.update(angular_error, dt), 1.0), -1.0)  # Max 1.0 rad/s

            # Publish command velocity
            self.publish_cmd_vel()

            self.get_logger().debug(
                f'Control - Distance: {distance:.3f}, Angle error: {angle_error:.3f}, '
                f'Linear: {self.linear_vel:.3f}, Angular: {self.angular_vel:.3f}'
            )

    def publish_cmd_vel(self):
        """Publish velocity commands."""
        cmd_vel = Twist()
        cmd_vel.linear.x = self.linear_vel
        cmd_vel.angular.z = self.angular_vel
        self.cmd_vel_pub.publish(cmd_vel)

    def follow_trajectory(self, trajectory_points):
        """Follow a predefined trajectory."""
        # This would implement trajectory following using feedforward + feedback control
        pass

    def obstacle_avoidance(self):
        """Implement simple obstacle avoidance."""
        # This would use sensor data to avoid obstacles while following path
        pass


def main(args=None):
    rclpy.init(args=args)

    controller_node = ControllerNode()

    try:
        rclpy.spin(controller_node)
    except KeyboardInterrupt:
        pass
    finally:
        controller_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()