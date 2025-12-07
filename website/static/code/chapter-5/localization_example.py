#!/usr/bin/env python3
"""
File: localization_example.py
Purpose: Demonstrates robot localization techniques (Monte Carlo Localization/PF)
Chapter: 5 - Navigation and Path Planning
Dependencies: rclpy, geometry_msgs, sensor_msgs, tf2_ros
Hardware: Mobile robot with sensors (simulation)
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseStamped, Point, PoseArray, Pose
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Point, Quaternion
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
import numpy as np
from math import cos, sin, sqrt, atan2, pi
import random


class Particle:
    """Particle for Monte Carlo Localization."""

    def __init__(self, x=0.0, y=0.0, theta=0.0, weight=1.0):
        self.x = x
        self.y = y
        self.theta = theta  # orientation
        self.weight = weight


class LocalizationNode(Node):
    """
    A node that demonstrates Monte Carlo Localization (Particle Filter)
    for estimating robot pose in a known map.
    """

    def __init__(self):
        super().__init__('localization_node')

        # Initialize localization variables
        self.particles = []
        self.num_particles = 100
        self.map = None
        self.laser_data = None
        self.odom_pose = None
        self.estimated_pose = Pose()

        # Initialize particles in a random distribution (in a real system,
        # this might be based on initial pose estimate)
        self.initialize_particles()

        # TF2 buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Create subscribers
        self.initial_pose_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/initialpose',
            self.initial_pose_callback,
            10
        )

        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.map_sub = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_callback,
            10
        )

        # Create publishers
        self.amcl_pose_pub = self.create_publisher(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            10
        )

        self.particle_cloud_pub = self.create_publisher(
            PoseArray,
            '/particlecloud',
            10
        )

        # Timer for localization update
        self.localization_timer = self.create_timer(0.1, self.localization_update)  # 10 Hz

        self.get_logger().info('Localization node initialized')

    def initialize_particles(self):
        """Initialize particles with random distribution."""
        self.particles = []
        for _ in range(self.num_particles):
            # In a real system, this might be based on initial pose estimate with covariance
            particle = Particle(
                x=random.uniform(-5.0, 5.0),
                y=random.uniform(-5.0, 5.0),
                theta=random.uniform(-pi, pi),
                weight=1.0 / self.num_particles
            )
            self.particles.append(particle)

    def initial_pose_callback(self, msg):
        """Handle initial pose estimate."""
        self.estimated_pose = msg.pose.pose

        # Initialize particles around the provided pose
        self.particles = []
        for _ in range(self.num_particles):
            # Add some noise around the initial estimate
            noise_x = random.gauss(0, 0.5)  # 0.5m std dev
            noise_y = random.gauss(0, 0.5)
            noise_theta = random.gauss(0, 0.1)  # 0.1 rad std dev

            particle = Particle(
                x=msg.pose.pose.position.x + noise_x,
                y=msg.pose.pose.position.y + noise_y,
                theta=2 * atan2(msg.pose.pose.orientation.z, msg.pose.pose.orientation.w) + noise_theta,
                weight=1.0 / self.num_particles
            )
            self.particles.append(particle)

        self.get_logger().info(f'Particles initialized around: ({msg.pose.pose.position.x:.2f}, {msg.pose.pose.position.y:.2f})')

    def map_callback(self, msg):
        """Process map data."""
        self.map = msg
        self.get_logger().info(f'Map received: {msg.info.width}x{msg.info.height}')

    def scan_callback(self, msg):
        """Process laser scan data."""
        self.laser_data = msg

    def localization_update(self):
        """Main localization update loop."""
        if self.laser_data is None or self.map is None:
            return

        # Get odometry data for motion model
        self.get_odometry()

        # Predict step: move particles based on odometry
        self.predict()

        # Update step: weight particles based on sensor data
        self.update()

        # Resample step: resample particles based on weights
        self.resample()

        # Estimate pose from particles
        self.estimate_pose()

    def get_odometry(self):
        """Get odometry data for motion model."""
        try:
            # Get transform from odom to base_link
            t = self.tf_buffer.lookup_transform(
                'odom',
                'base_link',
                rclpy.time.Time()
            )

            # Store current odometry pose
            self.odom_pose = Pose()
            self.odom_pose.position.x = t.transform.translation.x
            self.odom_pose.position.y = t.transform.translation.y
            self.odom_pose.orientation = t.transform.rotation

        except TransformException as ex:
            self.get_logger().warning(f'Could not transform odom to base_link: {ex}')

    def predict(self):
        """Predict particle poses based on odometry."""
        if self.odom_pose is None:
            return

        # This is a simplified motion model - in reality, you'd track pose changes
        # between time steps and apply them to each particle with some noise
        for particle in self.particles:
            # Add some process noise to each particle
            particle.x += random.gauss(0, 0.05)  # 5cm process noise
            particle.y += random.gauss(0, 0.05)
            particle.theta += random.gauss(0, 0.01)  # 0.01 rad process noise

    def update(self):
        """Update particle weights based on sensor likelihood."""
        if self.laser_data is None or self.map is None:
            return

        # Calculate weights for each particle based on how well
        # the expected laser scan matches the actual scan
        total_weight = 0.0

        for particle in self.particles:
            weight = self.calculate_likelihood(particle)
            particle.weight = weight
            total_weight += weight

        # Normalize weights
        if total_weight > 0:
            for particle in self.particles:
                particle.weight /= total_weight
        else:
            # If all weights are zero, reset to uniform distribution
            for particle in self.particles:
                particle.weight = 1.0 / len(self.particles)

    def calculate_likelihood(self, particle):
        """Calculate likelihood of a particle given sensor data."""
        # This is a simplified likelihood calculation
        # In a real implementation, this would involve ray tracing
        # through the map to predict expected laser readings

        if self.laser_data is None or self.map is None:
            return 1.0 / self.num_particles

        # For each laser beam, check if the expected range matches the actual range
        likelihood = 1.0
        num_beams = min(len(self.laser_data.ranges), 20)  # Use fewer beams for efficiency

        for i in range(0, len(self.laser_data.ranges), len(self.laser_data.ranges) // num_beams):
            if i >= len(self.laser_data.ranges):
                continue

            measured_range = self.laser_data.ranges[i]
            if not (self.laser_data.range_min < measured_range < self.laser_data.range_max):
                continue  # Skip invalid ranges

            # Calculate expected range from particle's pose
            beam_angle = self.laser_data.angle_min + i * self.laser_data.angle_increment
            expected_angle = particle.theta + beam_angle

            # Simple ray tracing to find expected range in map
            expected_range = self.ray_trace(particle.x, particle.y, expected_angle)

            # Calculate likelihood based on difference between expected and measured
            range_diff = abs(expected_range - measured_range)
            beam_likelihood = np.exp(-0.5 * (range_diff / 0.5) ** 2)  # Gaussian with std dev 0.5m

            likelihood *= beam_likelihood

        return max(likelihood, 1e-10)  # Avoid zero weights

    def ray_trace(self, x, y, angle):
        """Simple ray tracing to find distance to obstacle."""
        # This is a simplified ray tracer
        # In a real implementation, you'd use a more efficient algorithm like DDA

        step_size = 0.1  # 10cm steps
        max_range = 10.0  # Maximum sensor range

        for dist in np.arange(0, max_range, step_size):
            check_x = x + dist * cos(angle)
            check_y = y + dist * sin(angle)

            # Convert to map coordinates
            map_x = int((check_x - self.map.info.origin.position.x) / self.map.info.resolution)
            map_y = int((check_y - self.map.info.origin.position.y) / self.map.info.resolution)

            # Check bounds
            if (map_x < 0 or map_x >= self.map.info.width or
                map_y < 0 or map_y >= self.map.info.height):
                continue

            # Check if this cell is occupied
            map_index = map_y * self.map.info.width + map_x
            if map_index < len(self.map.data) and self.map.data[map_index] > 50:  # Occupied threshold
                return dist

        return max_range  # No obstacle found within range

    def resample(self):
        """Resample particles based on their weights."""
        # Create new particles based on current weights
        new_particles = []

        # Calculate cumulative weights
        cumulative_weights = []
        cumsum = 0
        for particle in self.particles:
            cumsum += particle.weight
            cumulative_weights.append(cumsum)

        # Resample using low-variance sampling
        start = random.uniform(0, 1.0 / self.num_particles)
        for i in range(self.num_particles):
            threshold = start + i * (1.0 / self.num_particles)

            # Find particle corresponding to threshold
            for j, cum_weight in enumerate(cumulative_weights):
                if threshold <= cum_weight:
                    # Add this particle to new set with uniform weight
                    source_particle = self.particles[j]
                    new_particle = Particle(
                        x=source_particle.x + random.gauss(0, 0.05),  # Add some noise
                        y=source_particle.y + random.gauss(0, 0.05),
                        theta=source_particle.theta + random.gauss(0, 0.01),
                        weight=1.0 / self.num_particles
                    )
                    new_particles.append(new_particle)
                    break

        self.particles = new_particles

    def estimate_pose(self):
        """Estimate robot pose from particles."""
        # Calculate weighted average of particles
        avg_x = sum(p.x * p.weight for p in self.particles)
        avg_y = sum(p.y * p.weight for p in self.particles)
        avg_theta = sum(p.theta * p.weight for p in self.particles)

        # Create pose message
        pose_msg = PoseWithCovarianceStamped()
        pose_msg.header.frame_id = 'map'
        pose_msg.header.stamp = self.get_clock().now().to_msg()

        pose_msg.pose.pose.position.x = avg_x
        pose_msg.pose.pose.position.y = avg_y
        pose_msg.pose.pose.position.z = 0.0

        # Convert angle to quaternion
        from math import sin, cos
        quat_z = sin(avg_theta / 2.0)
        quat_w = cos(avg_theta / 2.0)
        pose_msg.pose.pose.orientation.z = quat_z
        pose_msg.pose.pose.orientation.w = quat_w

        # Calculate covariance (simplified)
        # In a real implementation, you'd calculate the full covariance matrix
        pose_msg.pose.covariance[0] = 0.1  # X variance
        pose_msg.pose.covariance[7] = 0.1  # Y variance
        pose_msg.pose.covariance[35] = 0.1  # Theta variance

        # Publish estimated pose
        self.amcl_pose_pub.publish(pose_msg)

        # Store for internal use
        self.estimated_pose = pose_msg.pose.pose

        self.get_logger().info(f'Estimated pose: ({avg_x:.3f}, {avg_y:.3f}, {avg_theta:.3f})')

    def publish_particle_cloud(self):
        """Publish particle cloud for visualization."""
        from geometry_msgs.msg import PoseArray

        particle_cloud = PoseArray()
        particle_cloud.header.frame_id = 'map'
        particle_cloud.header.stamp = self.get_clock().now().to_msg()

        for particle in self.particles:
            pose = Pose()
            pose.position.x = particle.x
            pose.position.y = particle.y
            pose.position.z = 0.0

            # Convert angle to quaternion
            from math import sin, cos
            quat_z = sin(particle.theta / 2.0)
            quat_w = cos(particle.theta / 2.0)
            pose.orientation.z = quat_z
            pose.orientation.w = quat_w

            particle_cloud.poses.append(pose)

        self.particle_cloud_pub.publish(particle_cloud)


def main(args=None):
    rclpy.init(args=args)

    localization_node = LocalizationNode()

    try:
        rclpy.spin(localization_node)
    except KeyboardInterrupt:
        pass
    finally:
        localization_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()