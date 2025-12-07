#!/usr/bin/env python3
"""
File: advanced_physics_controller.py
Purpose: Advanced physics simulation controller with contact forces and friction
Chapter: 7 - Advanced Simulation Techniques
Dependencies: rclpy, geometry_msgs, std_msgs, gazebo_msgs
Hardware: Simulated robot in Gazebo
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Wrench, Vector3
from std_msgs.msg import Float32, Bool
from gazebo_msgs.msg import ContactsState
from gazebo_msgs.srv import ApplyBodyWrench, GetPhysicsProperties
from sensor_msgs.msg import Imu, JointState
from nav_msgs.msg import Odometry
import numpy as np
import math


class AdvancedPhysicsController(Node):
    """
    Advanced physics controller that handles complex contact forces,
    friction modeling, and environmental disturbances.
    """

    def __init__(self):
        super().__init__('advanced_physics_controller')

        # Physics parameters
        self.gravity = 9.81  # m/s^2
        self.contact_stiffness = 1000000.0  # N/m
        self.contact_damping = 100.0  # Ns/m
        self.friction_coefficient = 0.8  # Unitless

        # Environmental parameters
        self.wind_force = np.array([0.0, 0.0, 0.0])  # N
        self.wind_gust_probability = 0.01  # 1% chance per update
        self.turbulence = 0.1  # Variance in wind

        # Robot state
        self.robot_mass = 10.0  # kg
        self.robot_inertia = np.array([0.5, 0.5, 0.5])  # kg*m^2
        self.robot_position = np.array([0.0, 0.0, 0.0])
        self.robot_velocity = np.array([0.0, 0.0, 0.0])
        self.robot_orientation = np.array([0.0, 0.0, 0.0, 1.0])  # quaternion
        self.robot_angular_velocity = np.array([0.0, 0.0, 0.0])

        # Contact information
        self.contacts = []
        self.in_contact = False
        self.contact_force = np.array([0.0, 0.0, 0.0])
        self.contact_normal = np.array([0.0, 0.0, 1.0])  # Up by default

        # Publishers and subscribers
        self.contact_sub = self.create_subscription(
            ContactsState,
            '/gazebo/contact_states',
            self.contact_callback,
            10
        )

        self.imu_sub = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.joint_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_callback,
            10
        )

        self.physics_pub = self.create_publisher(
            Float32,
            '/physics_simulation/energy',
            10
        )

        self.contact_pub = self.create_publisher(
            Bool,
            '/physics_simulation/in_contact',
            10
        )

        # Timer for physics updates
        self.physics_timer = self.create_timer(0.01, self.physics_update)  # 100 Hz

        # Service clients
        self.apply_wrench_cli = self.create_client(
            ApplyBodyWrench,
            '/gazebo/apply_body_wrench'
        )

        self.get_physics_cli = self.create_client(
            GetPhysicsProperties,
            '/gazebo/get_physics_properties'
        )

        # Wait for services
        while not self.apply_wrench_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Apply wrench service not available, waiting...')

        self.get_logger().info('Advanced physics controller initialized')

    def contact_callback(self, msg):
        """Process contact sensor data."""
        self.contacts = []
        self.in_contact = False
        total_force = np.array([0.0, 0.0, 0.0])
        total_normal = np.array([0.0, 0.0, 0.0])

        for contact in msg.states:
            if len(contact.contact_positions) > 0:
                self.in_contact = True
                # Get the contact force (average of all contact points)
                for wrench in contact.wrenches:
                    force = np.array([
                        wrench.force.x,
                        wrench.force.y,
                        wrench.force.z
                    ])
                    total_force += force

                    # Get contact normal
                    normal = np.array([
                        wrench.surface_normal.x,
                        wrench.surface_normal.y,
                        wrench.surface_normal.z
                    ])
                    total_normal += normal

        if self.in_contact and len(msg.states) > 0:
            self.contact_force = total_force / len(msg.states)
            self.contact_normal = total_normal / len(msg.states)
            self.contact_normal = self.contact_normal / np.linalg.norm(self.contact_normal)

        # Publish contact state
        contact_msg = Bool()
        contact_msg.data = self.in_contact
        self.contact_pub.publish(contact_msg)

    def imu_callback(self, msg):
        """Process IMU data."""
        self.robot_orientation = np.array([
            msg.orientation.x,
            msg.orientation.y,
            msg.orientation.z,
            msg.orientation.w
        ])

        self.robot_angular_velocity = np.array([
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z
        ])

        # Get linear acceleration (remove gravity)
        accel = np.array([
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z
        ])
        # Remove gravity component (simplified)
        gravity_vector = self.rotate_vector_from_body_to_world(
            np.array([0, 0, -self.gravity])
        )
        linear_acceleration = accel - gravity_vector
        self.robot_velocity += linear_acceleration * 0.01  # dt = 0.01s

    def odom_callback(self, msg):
        """Process odometry data."""
        self.robot_position = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z
        ])

        # Update velocity from odometry (if available)
        self.robot_velocity = np.array([
            msg.twist.twist.linear.x,
            msg.twist.twist.linear.y,
            msg.twist.twist.linear.z
        ])

    def joint_callback(self, msg):
        """Process joint state data."""
        # This could be used to get more detailed robot state
        pass

    def rotate_vector_from_body_to_world(self, vector_body):
        """Rotate a vector from body frame to world frame using quaternion."""
        q = self.robot_orientation
        # Convert quaternion to rotation matrix
        R = np.array([
            [1 - 2*(q[1]**2 + q[2]**2), 2*(q[0]*q[1] - q[3]*q[2]), 2*(q[0]*q[2] + q[3]*q[1])],
            [2*(q[0]*q[1] + q[3]*q[2]), 1 - 2*(q[0]**2 + q[2]**2), 2*(q[1]*q[2] - q[3]*q[0])],
            [2*(q[0]*q[2] - q[3]*q[1]), 2*(q[1]*q[2] + q[3]*q[0]), 1 - 2*(q[0]**2 + q[1]**2)]
        ])
        return R @ vector_body

    def physics_update(self):
        """Main physics update loop."""
        dt = 0.01  # 100 Hz update rate

        # Update environmental conditions
        self.update_environmental_forces()

        # Calculate total forces acting on robot
        total_force = self.calculate_total_forces()

        # Apply forces using Newton's second law: F = ma
        acceleration = total_force / self.robot_mass
        self.robot_velocity += acceleration * dt

        # Update position
        self.robot_position += self.robot_velocity * dt

        # Calculate and publish energy
        kinetic_energy = 0.5 * self.robot_mass * np.dot(self.robot_velocity, self.robot_velocity)
        energy_msg = Float32()
        energy_msg.data = kinetic_energy
        self.physics_pub.publish(energy_msg)

        # Apply external wrench to Gazebo if needed
        if np.linalg.norm(total_force) > 0.01:  # Only apply significant forces
            self.apply_external_force(total_force)

    def update_environmental_forces(self):
        """Update environmental forces like wind."""
        # Update wind force with some randomness
        random_force = np.random.normal(0, self.turbulence, 3)

        # Occasionally add a wind gust
        if np.random.random() < self.wind_gust_probability:
            gust_force = np.random.normal(0, 2.0, 3)  # Stronger gust
            self.wind_force = gust_force
        else:
            # Apply turbulence to base wind
            self.wind_force += random_force * dt  # dt is time step
            # Dampen the wind to prevent accumulation
            self.wind_force *= 0.99

    def calculate_total_forces(self):
        """Calculate all forces acting on the robot."""
        total_force = np.array([0.0, 0.0, 0.0])

        # Gravity
        gravity_force = np.array([0.0, 0.0, -self.robot_mass * self.gravity])
        total_force += gravity_force

        # Wind force
        total_force += self.wind_force

        # Contact forces (simplified spring-damper model)
        if self.in_contact:
            # Calculate penetration depth (simplified)
            penetration_depth = max(0, -self.robot_position[2])  # Assuming robot should stay above z=0
            if penetration_depth > 0:
                # Spring force (proportional to penetration)
                spring_force = self.contact_stiffness * penetration_depth * self.contact_normal
                # Damping force (proportional to velocity in contact normal direction)
                vel_in_normal_dir = np.dot(self.robot_velocity, self.contact_normal)
                damping_force = -self.contact_damping * vel_in_normal_dir * self.contact_normal

                total_force += spring_force + damping_force

                # Friction force (opposes motion parallel to contact surface)
                normal_force_magnitude = abs(np.dot(total_force, self.contact_normal))
                tangential_velocity = self.robot_velocity - np.dot(self.robot_velocity, self.contact_normal) * self.contact_normal
                tangential_speed = np.linalg.norm(tangential_velocity)

                if tangential_speed > 0.001:  # Avoid division by zero
                    tangential_direction = tangential_velocity / tangential_speed
                    friction_magnitude = min(
                        self.friction_coefficient * normal_force_magnitude,
                        self.robot_mass * tangential_speed / dt  # Don't overcorrect
                    )
                    friction_force = -friction_magnitude * tangential_direction
                    total_force += friction_force

        return total_force

    def apply_external_force(self, force):
        """Apply an external force to the robot in Gazebo."""
        req = ApplyBodyWrench.Request()
        req.body_name = 'my_robot::base_link'  # Adjust to your robot's link name
        req.reference_frame = 'world'
        req.wrench.force = Vector3(x=float(force[0]), y=float(force[1]), z=float(force[2]))
        req.start_time = self.get_clock().now().to_msg()
        req.duration.sec = 0
        req.duration.nanosec = 10000000  # 10 ms

        future = self.apply_wrench_cli.call_async(req)
        # Note: In a real implementation, you'd want to handle the future response

    def get_physics_properties(self):
        """Get current physics properties from Gazebo."""
        req = GetPhysicsProperties.Request()
        future = self.get_physics_cli.call_async(req)
        # Note: In a real implementation, you'd want to handle the future response


class DomainRandomizationNode(Node):
    """
    Node that implements domain randomization for robust simulation.
    """

    def __init__(self):
        super().__init__('domain_randomization_node')

        # Physics parameters to randomize
        self.param_ranges = {
            'friction': (0.4, 1.0),
            'mass_variance': (0.8, 1.2),
            'gravity_variance': (0.9, 1.1),
            'sensor_noise': (0.001, 0.01),
            'wind_base': (0.0, 1.0)
        }

        # Timer for randomization updates
        self.randomization_timer = self.create_timer(5.0, self.randomize_parameters)

        # Publisher for randomized parameters
        self.param_pub = self.create_publisher(Float32, '/domain_randomization/parameters', 10)

        self.get_logger().info('Domain randomization node initialized')

    def randomize_parameters(self):
        """Randomize physics parameters."""
        randomized_params = {}

        for param, (min_val, max_val) in self.param_ranges.items():
            randomized_params[param] = np.random.uniform(min_val, max_val)

        self.get_logger().info(f'Randomized parameters: {randomized_params}')

        # Publish one of the parameters for monitoring
        param_msg = Float32()
        param_msg.data = randomized_params['friction']
        self.param_pub.publish(param_msg)

        # Here you would apply the parameters to your simulation
        # For example, by calling services to update Gazebo physics properties
        self.apply_randomized_parameters(randomized_params)

    def apply_randomized_parameters(self, params):
        """Apply randomized parameters to simulation."""
        # In a real implementation, this would update Gazebo physics properties
        # through services or parameters
        pass


def main(args=None):
    rclpy.init(args=args)

    # Create both nodes
    physics_controller = AdvancedPhysicsController()
    domain_randomization = DomainRandomizationNode()

    # Create executor and add nodes
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(physics_controller)
    executor.add_node(domain_randomization)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        physics_controller.destroy_node()
        domain_randomization.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()