#!/usr/bin/env python3
"""
File: gazebo_ros_controller.py
Purpose: Example ROS 2 controller for Gazebo simulation
Chapter: 6 - Gazebo Classic & Fortress
Dependencies: rclpy, geometry_msgs, gazebo_msgs
Hardware: Simulated robot in Gazebo
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from gazebo_msgs.srv import SetEntityState
from gazebo_msgs.msg import ModelStates
from std_msgs.msg import String
import math


class GazeboController(Node):
    """
    A controller that interfaces with Gazebo through ROS 2 services and topics.
    """

    def __init__(self):
        super().__init__('gazebo_controller')

        # Create publisher for velocity commands
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Create subscriber for Gazebo model states
        self.model_states_sub = self.create_subscription(
            ModelStates,
            '/gazebo/model_states',
            self.model_states_callback,
            10
        )

        # Create client for Gazebo services
        self.set_state_client = self.create_client(
            SetEntityState,
            '/gazebo/set_entity_state'
        )

        # Wait for service to be available
        while not self.set_state_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Gazebo service not available, waiting again...')

        # Timer for control loop
        self.timer = self.create_timer(0.1, self.control_loop)

        # Robot state
        self.robot_position = [0.0, 0.0, 0.0]
        self.robot_orientation = [0.0, 0.0, 0.0, 1.0]  # quaternion
        self.robot_linear_vel = [0.0, 0.0, 0.0]
        self.robot_angular_vel = [0.0, 0.0, 0.0]

        # Control parameters
        self.linear_speed = 0.5  # m/s
        self.angular_speed = 0.3  # rad/s

        self.get_logger().info('Gazebo controller initialized')

    def model_states_callback(self, msg):
        """Process Gazebo model states."""
        # Find our robot in the model states
        robot_name = 'my_robot'  # Adjust this to your robot's name
        try:
            robot_index = msg.name.index(robot_name)

            # Update robot position
            self.robot_position[0] = msg.pose[robot_index].position.x
            self.robot_position[1] = msg.pose[robot_index].position.y
            self.robot_position[2] = msg.pose[robot_index].position.z

            # Update robot orientation (quaternion)
            self.robot_orientation[0] = msg.pose[robot_index].orientation.x
            self.robot_orientation[1] = msg.pose[robot_index].orientation.y
            self.robot_orientation[2] = msg.pose[robot_index].orientation.z
            self.robot_orientation[3] = msg.pose[robot_index].orientation.w

            # Update linear velocity
            self.robot_linear_vel[0] = msg.twist[robot_index].linear.x
            self.robot_linear_vel[1] = msg.twist[robot_index].linear.y
            self.robot_linear_vel[2] = msg.twist[robot_index].linear.z

            # Update angular velocity
            self.robot_angular_vel[0] = msg.twist[robot_index].angular.x
            self.robot_angular_vel[1] = msg.twist[robot_index].angular.y
            self.robot_angular_vel[2] = msg.twist[robot_index].angular.z

        except ValueError:
            # Robot not found in model states
            pass

    def control_loop(self):
        """Main control loop."""
        # Simple control: move in a square pattern
        current_time = self.get_clock().now().nanoseconds / 1e9

        # Calculate movement pattern (square trajectory)
        phase = (current_time * 0.1) % 4  # Cycle every 40 seconds

        cmd_vel = Twist()

        if phase < 1:  # Moving in +X direction
            cmd_vel.linear.x = self.linear_speed
            cmd_vel.angular.z = 0.0
            self.get_logger().info('Moving in +X direction')
        elif phase < 2:  # Turning
            cmd_vel.linear.x = 0.0
            cmd_vel.angular.z = self.angular_speed
            self.get_logger().info('Turning')
        elif phase < 3:  # Moving in -X direction
            cmd_vel.linear.x = -self.linear_speed
            cmd_vel.angular.z = 0.0
            self.get_logger().info('Moving in -X direction')
        else:  # Turning back
            cmd_vel.linear.x = 0.0
            cmd_vel.angular.z = -self.angular_speed
            self.get_logger().info('Turning back')

        # Publish the command
        self.cmd_vel_pub.publish(cmd_vel)

        # Log robot state
        self.get_logger().info(
            f'Robot position: ({self.robot_position[0]:.2f}, {self.robot_position[1]:.2f}, {self.robot_position[2]:.2f})'
        )

    def move_to_position(self, target_x, target_y):
        """Move robot to a specific position."""
        cmd_vel = Twist()

        # Calculate distance to target
        dx = target_x - self.robot_position[0]
        dy = target_y - self.robot_position[1]
        distance = math.sqrt(dx*dx + dy*dy)

        if distance > 0.1:  # If not close enough to target
            # Calculate desired angle
            desired_angle = math.atan2(dy, dx)

            # Get current orientation (simplified - assuming z-axis rotation)
            current_angle = math.atan2(
                2.0 * (self.robot_orientation[3] * self.robot_orientation[2]),
                1.0 - 2.0 * (self.robot_orientation[2] * self.robot_orientation[2])
            )

            # Calculate angle error
            angle_error = desired_angle - current_angle
            # Normalize angle error to [-pi, pi]
            while angle_error > math.pi:
                angle_error -= 2 * math.pi
            while angle_error < -math.pi:
                angle_error += 2 * math.pi

            # Set velocities based on errors
            cmd_vel.linear.x = min(self.linear_speed, distance) if abs(angle_error) < 0.2 else 0.0
            cmd_vel.angular.z = max(-self.angular_speed, min(self.angular_speed, angle_error * 1.0))

        self.cmd_vel_pub.publish(cmd_vel)

    def set_robot_state(self, x, y, z, roll, pitch, yaw):
        """Set robot state directly in Gazebo."""
        from gazebo_msgs.srv import SetEntityState
        from geometry_msgs.msg import Pose, Point, Quaternion, Twist, Vector3

        # Convert RPY to quaternion
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        qw = cr * cp * cy + sr * sp * sy
        qx = sr * cp * cy - cr * sp * sy
        qy = cr * sp * cy + sr * cp * sy
        qz = cr * cp * sy - sr * sp * cy

        req = SetEntityState.Request()
        req.state.name = 'my_robot'  # Adjust to your robot's name
        req.state.pose = Pose(
            position=Point(x=x, y=y, z=z),
            orientation=Quaternion(x=qx, y=qy, z=qz, w=qw)
        )
        req.state.twist = Twist(
            linear=Vector3(x=0.0, y=0.0, z=0.0),
            angular=Vector3(x=0.0, y=0.0, z=0.0)
        )
        req.state.reference_frame = 'world'

        future = self.set_state_client.call_async(req)
        return future


def main(args=None):
    rclpy.init(args=args)

    controller = GazeboController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()