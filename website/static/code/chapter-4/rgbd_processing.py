#!/usr/bin/env python3
"""
File: rgbd_processing.py
Purpose: Demonstrates processing of RGB-D camera data for 3D perception
Chapter: 4 - Sensors and Perception
Dependencies: rclpy, sensor_msgs, cv_bridge, numpy
Hardware: RGB-D Camera (simulation)
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2
import numpy as np
from geometry_msgs.msg import PointStamped
from sensor_msgs.msg import PointCloud2, PointField
import struct


class RGBDProcessor(Node):
    """
    A node that processes RGB-D camera data to extract depth information,
    create point clouds, and perform basic 3D perception tasks.
    """

    def __init__(self):
        super().__init__('rgbd_processor')

        # Initialize OpenCV bridge
        self.bridge = CvBridge()

        # Camera parameters (will be updated from camera info)
        self.camera_matrix = None
        self.distortion_coeffs = None

        # Create subscribers for RGB and depth images
        self.rgb_sub = self.create_subscription(
            Image,
            '/camera/rgb/image_raw',
            self.rgb_callback,
            10
        )

        self.depth_sub = self.create_subscription(
            Image,
            '/camera/depth/image_raw',
            self.depth_callback,
            10
        )

        self.camera_info_sub = self.create_subscription(
            CameraInfo,
            '/camera/rgb/camera_info',
            self.camera_info_callback,
            10
        )

        # Create publisher for processed point cloud
        self.point_cloud_pub = self.create_publisher(
            PointCloud2,
            '/camera/point_cloud',
            10
        )

        # Create publisher for depth image
        self.depth_processed_pub = self.create_publisher(
            Image,
            '/camera/depth/processed',
            10
        )

        self.get_logger().info('RGB-D processor initialized')

    def camera_info_callback(self, msg):
        """Update camera parameters from camera info message."""
        self.camera_matrix = np.array(msg.k).reshape(3, 3)
        self.distortion_coeffs = np.array(msg.d)
        self.get_logger().info('Camera parameters updated')

    def rgb_callback(self, msg):
        """Process RGB image data."""
        try:
            # Convert ROS Image message to OpenCV image
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Process the RGB image (example: edge detection)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)

            # Display processed image (for debugging)
            cv2.imshow('RGB Image', cv_image)
            cv2.imshow('Edges', edges)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f'Error processing RGB image: {e}')

    def depth_callback(self, msg):
        """Process depth image data."""
        try:
            # Convert ROS Image message to OpenCV image
            cv_depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')

            # Normalize depth for visualization (0-255 range)
            depth_normalized = cv2.normalize(cv_depth, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)

            # Convert back to ROS Image message for publishing
            depth_processed_msg = self.bridge.cv2_to_imgmsg(depth_normalized, encoding='mono8')
            depth_processed_msg.header = msg.header
            self.depth_processed_pub.publish(depth_processed_msg)

            # Process depth data for point cloud generation
            if self.camera_matrix is not None:
                point_cloud = self.generate_point_cloud(cv_depth, msg.header)
                if point_cloud is not None:
                    self.point_cloud_pub.publish(point_cloud)

            # Display depth image (for debugging)
            cv2.imshow('Depth Image', depth_normalized)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f'Error processing depth image: {e}')

    def generate_point_cloud(self, depth_image, header):
        """Generate a point cloud from depth image and camera parameters."""
        if self.camera_matrix is None:
            return None

        height, width = depth_image.shape
        points = []

        # Invert camera matrix to get pixel coordinates to 3D coordinates
        inv_camera_matrix = np.linalg.inv(self.camera_matrix)

        for v in range(0, height, 5):  # Sample every 5th pixel for efficiency
            for u in range(0, width, 5):
                z = depth_image[v, u] / 1000.0  # Convert mm to meters

                # Skip invalid depth values
                if z <= 0 or z > 10.0:  # Skip if too far or invalid
                    continue

                # Convert pixel coordinates to 3D coordinates
                pixel_coords = np.array([u, v, 1])
                cam_coords = inv_camera_matrix @ pixel_coords
                world_coords = cam_coords * z

                # Add point to list
                points.append([world_coords[0], world_coords[1], world_coords[2]])

        if not points:
            return None

        # Create PointCloud2 message
        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1)
        ]

        # Pack points into binary data
        data = []
        for point in points:
            data.append(struct.pack('fff', point[0], point[1], point[2]))

        # Create PointCloud2 message
        point_cloud_msg = PointCloud2()
        point_cloud_msg.header = header
        point_cloud_msg.height = 1
        point_cloud_msg.width = len(points)
        point_cloud_msg.fields = fields
        point_cloud_msg.is_bigendian = False
        point_cloud_msg.point_step = 12  # 3 floats * 4 bytes each
        point_cloud_msg.row_step = point_cloud_msg.point_step * point_cloud_msg.width
        point_cloud_msg.is_dense = True
        point_cloud_msg.data = b''.join(data)

        return point_cloud_msg


def main(args=None):
    rclpy.init(args=args)

    rgbd_processor = RGBDProcessor()

    try:
        rclpy.spin(rgbd_processor)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        rgbd_processor.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()