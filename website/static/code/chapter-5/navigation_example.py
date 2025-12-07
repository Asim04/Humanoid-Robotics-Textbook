#!/usr/bin/env python3
"""
File: navigation_example.py
Purpose: Demonstrates ROS 2 navigation stack concepts including path planning and execution
Chapter: 5 - Navigation and Path Planning
Dependencies: rclpy, geometry_msgs, nav_msgs, tf2_ros
Hardware: Mobile robot base (simulation)
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Point, Quaternion
from nav_msgs.msg import Path, OccupancyGrid
from geometry_msgs.msg import Twist
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
import numpy as np
from math import sqrt, atan2, pi


class NavigationNode(Node):
    """
    A node that demonstrates navigation concepts including path planning,
    obstacle avoidance, and path following.
    """

    def __init__(self):
        super().__init__('navigation_node')

        # Initialize path planning variables
        self.current_pose = None
        self.goal_pose = None
        self.path = []
        self.obstacles = []
        self.path_index = 0

        # TF2 buffer and listener for transforms
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Create subscribers
        self.goal_sub = self.create_subscription(
            PoseStamped,
            '/move_base_simple/goal',
            self.goal_callback,
            10
        )

        self.map_sub = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_callback,
            10
        )

        # Create publishers
        self.path_pub = self.create_publisher(
            Path,
            '/plan',
            10
        )

        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.local_plan_pub = self.create_publisher(
            Path,
            '/local_plan',
            10
        )

        # Timer for navigation control
        self.nav_timer = self.create_timer(0.1, self.navigation_control)  # 10 Hz

        # Timer for getting current pose
        self.pose_timer = self.create_timer(0.05, self.get_current_pose)  # 20 Hz

        self.get_logger().info('Navigation node initialized')

    def goal_callback(self, msg):
        """Handle new goal pose."""
        self.goal_pose = msg.pose
        self.get_logger().info(f'New goal received: ({msg.pose.position.x:.2f}, {msg.pose.position.y:.2f})')

        # Plan path to goal
        if self.current_pose is not None:
            self.plan_path(self.current_pose, self.goal_pose)
        else:
            self.get_logger().warning('Current pose not available for path planning')

    def map_callback(self, msg):
        """Process map data for obstacle information."""
        self.get_logger().info(f'Map received: {msg.info.width}x{msg.info.height} resolution: {msg.info.resolution}')

        # Store map information for path planning
        self.map_info = msg.info
        self.map_data = msg.data

    def get_current_pose(self):
        """Get current robot pose from TF."""
        try:
            # Get transform from map to base_link
            t = self.tf_buffer.lookup_transform(
                'map',
                'base_link',
                rclpy.time.Time()
            )

            # Create pose from transform
            self.current_pose = PoseStamped()
            self.current_pose.pose.position.x = t.transform.translation.x
            self.current_pose.pose.position.y = t.transform.translation.y
            self.current_pose.pose.position.z = t.transform.translation.z
            self.current_pose.pose.orientation = t.transform.rotation

        except TransformException as ex:
            self.get_logger().warning(f'Could not transform map to base_link: {ex}')

    def plan_path(self, start_pose, goal_pose):
        """Simple path planning (in a real implementation, this would use A*, Dijkstra, etc.)."""
        # Clear previous path
        self.path = []

        # Create a simple straight-line path (for demonstration)
        steps = 20  # Number of steps in the path
        start = np.array([start_pose.position.x, start_pose.position.y])
        goal = np.array([goal_pose.position.x, goal_pose.position.y])

        for i in range(steps + 1):
            t = i / steps
            point = start + t * (goal - start)

            pose_stamped = PoseStamped()
            pose_stamped.pose.position.x = float(point[0])
            pose_stamped.pose.position.y = float(point[1])
            pose_stamped.pose.position.z = 0.0
            # Simple orientation towards goal
            angle = atan2(goal[1] - start[1], goal[0] - start[0])
            pose_stamped.pose.orientation.z = np.sin(angle / 2)
            pose_stamped.pose.orientation.w = np.cos(angle / 2)

            self.path.append(pose_stamped)

        # Publish the path
        path_msg = Path()
        path_msg.header.frame_id = 'map'
        path_msg.header.stamp = self.get_clock().now().to_msg()
        path_msg.poses = self.path

        self.path_pub.publish(path_msg)
        self.path_index = 0  # Reset path index

        self.get_logger().info(f'Path planned with {len(self.path)} waypoints')

    def navigation_control(self):
        """Main navigation control loop."""
        if self.current_pose is None or self.goal_pose is None or len(self.path) == 0:
            return

        # Check if we've reached the goal
        current_pos = np.array([self.current_pose.position.x, self.current_pose.position.y])
        goal_pos = np.array([self.goal_pose.position.x, self.goal_pose.position.y])

        distance_to_goal = np.linalg.norm(current_pos - goal_pos)

        if distance_to_goal < 0.5:  # Within 0.5m of goal
            self.get_logger().info('Goal reached!')
            # Stop the robot
            cmd_vel = Twist()
            cmd_vel.linear.x = 0.0
            cmd_vel.angular.z = 0.0
            self.cmd_vel_pub.publish(cmd_vel)
            return

        # Follow the path
        if self.path_index < len(self.path):
            target_pose = self.path[self.path_index].pose
            self.follow_path_to_waypoint(target_pose)

            # Check if we've reached this waypoint
            target_pos = np.array([target_pose.position.x, target_pose.position.y])
            distance_to_waypoint = np.linalg.norm(current_pos - target_pos)

            if distance_to_waypoint < 0.3:  # Within 0.3m of waypoint
                self.path_index += 1

    def follow_path_to_waypoint(self, target_pose):
        """Simple proportional controller to follow path to a waypoint."""
        # Get current position
        current_x = self.current_pose.position.x
        current_y = self.current_pose.position.y

        # Calculate desired heading
        target_x = target_pose.position.x
        target_y = target_pose.position.y
        desired_angle = atan2(target_y - current_y, target_x - current_x)

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

        # Simple proportional controller
        angular_velocity = max(min(angle_error * 1.0, 1.0), -1.0)  # Limit angular velocity
        linear_velocity = max(min(0.5 * (1.0 - abs(angle_error) / pi), 0.5), 0.0)  # Slower when turning

        # Create and publish velocity command
        cmd_vel = Twist()
        cmd_vel.linear.x = linear_velocity
        cmd_vel.angular.z = angular_velocity

        self.cmd_vel_pub.publish(cmd_vel)

        self.get_logger().debug(f'Following path - Linear: {linear_velocity:.3f}, Angular: {angular_velocity:.3f}')


def main(args=None):
    rclpy.init(args=args)

    navigation_node = NavigationNode()

    try:
        rclpy.spin(navigation_node)
    except KeyboardInterrupt:
        pass
    finally:
        navigation_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()