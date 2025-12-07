#!/usr/bin/env python3
"""
File: lidar_processing.py
Purpose: Demonstrates LiDAR point cloud processing and obstacle detection
Chapter: 4 - Sensors and Perception
Dependencies: rclpy, sensor_msgs, numpy
Hardware: LiDAR (simulation)
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, PointCloud2
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import PointStamped, Vector3
import numpy as np
import sensor_msgs.point_cloud2 as pc2
from collections import deque


class LiDARProcessor(Node):
    """
    A node that processes LiDAR data to detect obstacles, create occupancy maps,
    and perform basic navigation-related tasks.
    """

    def __init__(self):
        super().__init__('lidar_processor')

        # Initialize LiDAR processing parameters
        self.min_distance = 0.3  # Minimum detection distance (m)
        self.max_distance = 10.0  # Maximum detection distance (m)
        self.obstacle_threshold = 0.5  # Distance threshold for obstacles (m)
        self.scan_history = deque(maxlen=5)  # Keep last 5 scans for filtering

        # Create subscribers for different LiDAR data types
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.pointcloud_sub = self.create_subscription(
            PointCloud2,
            '/lidar/points',
            self.pointcloud_callback,
            10
        )

        # Create publishers for processed data
        self.obstacle_pub = self.create_publisher(
            Float32MultiArray,
            '/lidar/obstacles',
            10
        )

        self.closest_object_pub = self.create_publisher(
            Vector3,
            '/lidar/closest_object',
            10
        )

        self.free_space_pub = self.create_publisher(
            Float32MultiArray,
            '/lidar/free_space',
            10
        )

        self.get_logger().info('LiDAR processor initialized')

    def scan_callback(self, msg):
        """Process LaserScan message."""
        # Store scan in history for filtering
        self.scan_history.append(msg)

        # Process the scan to detect obstacles
        obstacles = self.process_scan(msg)
        free_space = self.detect_free_space(msg)

        # Publish obstacle information
        obstacle_msg = Float32MultiArray()
        obstacle_msg.data = obstacles
        self.obstacle_pub.publish(obstacle_msg)

        # Publish free space information
        free_space_msg = Float32MultiArray()
        free_space_msg.data = free_space
        self.free_space_pub.publish(free_space_msg)

        # Find and publish closest object
        closest_obj = self.find_closest_object(msg)
        if closest_obj is not None:
            closest_msg = Vector3()
            closest_msg.x = closest_obj[0]  # X coordinate
            closest_msg.y = closest_obj[1]  # Y coordinate
            closest_msg.z = closest_obj[2]  # Distance
            self.closest_object_pub.publish(closest_msg)

        self.get_logger().info(
            f'Laser scan processed: {len(obstacles)} obstacles detected, '
            f'closest object at distance: {closest_obj[2] if closest_obj else "N/A"}m'
        )

    def pointcloud_callback(self, msg):
        """Process PointCloud2 message."""
        try:
            # Convert PointCloud2 to list of points
            points = list(pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True))

            if len(points) > 0:
                # Convert to numpy array for processing
                points_array = np.array(points)

                # Filter points based on distance
                distances = np.linalg.norm(points_array, axis=1)
                valid_indices = (distances >= self.min_distance) & (distances <= self.max_distance)
                filtered_points = points_array[valid_indices]

                if len(filtered_points) > 0:
                    # Perform basic clustering to identify objects
                    clusters = self.cluster_points(filtered_points)

                    self.get_logger().info(f'Point cloud processed: {len(clusters)} clusters detected')

        except Exception as e:
            self.get_logger().error(f'Error processing point cloud: {e}')

    def process_scan(self, scan_msg):
        """Process LaserScan to detect obstacles."""
        obstacles = []

        # Process each range reading
        for i, range_val in enumerate(scan_msg.ranges):
            if np.isfinite(range_val) and self.min_distance <= range_val <= self.max_distance:
                # Calculate angle for this reading
                angle = scan_msg.angle_min + i * scan_msg.angle_increment

                # Check if this range indicates an obstacle
                if range_val <= self.obstacle_threshold:
                    # Convert polar to Cartesian coordinates
                    x = range_val * np.cos(angle)
                    y = range_val * np.sin(angle)

                    obstacles.append([x, y, range_val, angle])

        return [item for sublist in obstacles for item in sublist]  # Flatten list

    def detect_free_space(self, scan_msg):
        """Detect free space in the scan."""
        free_space = []

        # Look for consecutive readings indicating free space
        consecutive_free = 0
        max_free_directions = []

        for i, range_val in enumerate(scan_msg.ranges):
            angle = scan_msg.angle_min + i * scan_msg.angle_increment

            if np.isfinite(range_val) and range_val > self.obstacle_threshold:
                consecutive_free += 1
            else:
                if consecutive_free > 10:  # At least 10 consecutive free readings
                    # Calculate the angle of this free space
                    free_space.append(angle)
                consecutive_free = 0

        # Also add the longest free space direction
        if consecutive_free > 10:
            free_space.append(scan_msg.angle_min + (len(scan_msg.ranges) - 1) * scan_msg.angle_increment)

        return free_space

    def find_closest_object(self, scan_msg):
        """Find the closest object in the scan."""
        min_distance = float('inf')
        closest_angle = 0.0

        for i, range_val in enumerate(scan_msg.ranges):
            if np.isfinite(range_val) and self.min_distance <= range_val <= self.max_distance:
                if range_val < min_distance:
                    min_distance = range_val
                    closest_angle = scan_msg.angle_min + i * scan_msg.angle_increment

        if min_distance != float('inf'):
            # Convert to Cartesian coordinates
            x = min_distance * np.cos(closest_angle)
            y = min_distance * np.sin(closest_angle)
            return [x, y, min_distance]

        return None

    def cluster_points(self, points):
        """Simple clustering of 3D points to identify objects."""
        if len(points) == 0:
            return []

        clusters = []
        visited = [False] * len(points)

        for i, point in enumerate(points):
            if not visited[i]:
                cluster = [i]
                visited[i] = True

                # Find all points within clustering distance
                for j, other_point in enumerate(points):
                    if i != j and not visited[j]:
                        distance = np.linalg.norm(point - other_point)
                        if distance < 0.5:  # 0.5m clustering distance
                            cluster.append(j)
                            visited[j] = True

                if len(cluster) > 5:  # Only consider clusters with more than 5 points
                    cluster_points = points[cluster]
                    centroid = np.mean(cluster_points, axis=0)
                    clusters.append(centroid)

        return clusters


def main(args=None):
    rclpy.init(args=args)

    lidar_processor = LiDARProcessor()

    try:
        rclpy.spin(lidar_processor)
    except KeyboardInterrupt:
        pass
    finally:
        lidar_processor.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()