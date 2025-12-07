#!/usr/bin/env python3
"""
File: rgbd_processing.py
Purpose: Demonstrates RGB-D camera processing and 3D reconstruction concepts
Chapter: 2 - Sensor Systems & Perception
Dependencies: numpy, math
Hardware: None (simulation)
"""

import numpy as np
import math
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class RGBDFrame:
    """
    Represents an RGB-D frame with color and depth information
    """
    rgb_image: np.ndarray  # Shape: (height, width, 3) - RGB values 0-255
    depth_map: np.ndarray  # Shape: (height, width) - Depth values in meters
    timestamp: float
    camera_intrinsics: Tuple[float, float, float, float]  # (fx, fy, cx, cy)


class RGBDProcessor:
    """
    Processes RGB-D camera data to extract 3D information
    Demonstrates concepts from RGB-D cameras (RealSense) section
    """

    def __init__(self, width: int = 640, height: int = 480):
        # Camera intrinsics (typical values for RGB-D cameras like RealSense)
        self.fx = 320.0  # Focal length x
        self.fy = 320.0  # Focal length y
        self.cx = width / 2   # Principal point x
        self.cy = height / 2  # Principal point y

        self.intrinsics = (self.fx, self.fy, self.cx, self.cy)
        self.width = width
        self.height = height

    def simulate_rgbd_frame(self) -> RGBDFrame:
        """
        Simulate an RGB-D frame with a simple scene
        """
        # Create a simulated RGB image
        rgb_image = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Add a colored object in the center (e.g., a cube)
        center_y, center_x = self.height // 2, self.width // 2
        size = 50

        # Add a blue object
        rgb_image[center_y-size:center_y+size, center_x-size:center_x+size] = [0, 0, 255]

        # Add some random background
        rgb_image += np.random.randint(0, 30, size=(self.height, self.width, 3), dtype=np.uint8)

        # Clamp values to valid range
        rgb_image = np.clip(rgb_image, 0, 255)

        # Create a depth map with different distances
        depth_map = np.full((self.height, self.width), 5.0, dtype=np.float32)  # Default 5m

        # Object in the center is closer (2m)
        depth_map[center_y-size:center_y+size, center_x-size:center_x+size] = 2.0

        # Add some noise to make it more realistic
        depth_map += np.random.normal(0, 0.01, size=depth_map.shape)

        return RGBDFrame(
            rgb_image=rgb_image,
            depth_map=depth_map,
            timestamp=0.0,  # Placeholder
            camera_intrinsics=self.intrinsics
        )

    def depth_to_point_cloud(self, rgbd_frame: RGBDFrame) -> np.ndarray:
        """
        Convert depth map to 3D point cloud
        Returns array of 3D points (x, y, z) in camera coordinate system
        """
        height, width = rgbd_frame.depth_map.shape
        fx, fy, cx, cy = rgbd_frame.camera_intrinsics

        # Create coordinate grids
        y_coords, x_coords = np.mgrid[0:height, 0:width]

        # Flatten for processing
        x_flat = x_coords.flatten()
        y_flat = y_coords.flatten()
        depth_flat = rgbd_frame.depth_map.flatten()

        # Convert pixel coordinates to 3D camera coordinates
        z = depth_flat
        x = (x_flat - cx) * z / fx
        y = (y_flat - cy) * z / fy

        # Combine into point cloud (Nx3 array)
        point_cloud = np.stack([x, y, z], axis=1)

        # Filter out invalid points (zero depth or too far)
        valid_points = point_cloud[z > 0.1]  # Remove points with depth <= 0.1m

        return valid_points

    def extract_object_points(self, rgbd_frame: RGBDFrame, distance_threshold: float = 3.0) -> np.ndarray:
        """
        Extract points belonging to objects closer than the threshold
        This simulates object segmentation using depth information
        """
        # Get the full point cloud
        all_points = self.depth_to_point_cloud(rgbd_frame)

        # Filter points that are closer than the threshold (potential objects of interest)
        object_points = all_points[all_points[:, 2] < distance_threshold]

        return object_points

    def calculate_object_centroid(self, rgbd_frame: RGBDFrame, distance_threshold: float = 3.0) -> Optional[np.ndarray]:
        """
        Calculate the 3D centroid of objects in the scene
        """
        object_points = self.extract_object_points(rgbd_frame, distance_threshold)

        if len(object_points) == 0:
            return None

        # Calculate centroid
        centroid = np.mean(object_points, axis=0)
        return centroid

    def detect_planes(self, rgbd_frame: RGBDFrame, distance_threshold: float = 3.0,
                     inlier_threshold: float = 0.05) -> list:
        """
        Simple plane detection using depth information
        Returns list of plane equations [a, b, c, d] where ax + by + cz + d = 0
        """
        object_points = self.extract_object_points(rgbd_frame, distance_threshold)

        if len(object_points) < 10:  # Need minimum points for plane detection
            return []

        # For this simulation, we'll detect the ground plane
        # In a real implementation, this would use RANSAC or similar algorithm
        z_values = object_points[:, 2]  # z is depth in camera coordinates

        # Find the most common z-value (ground level)
        if len(z_values) > 0:
            ground_z = np.mean(z_values)
            # Ground plane equation: z = ground_z => 0*x + 0*y + 1*z - ground_z = 0
            return [[0.0, 0.0, 1.0, -ground_z]]

        return []

    def process_rgbd_demo(self):
        """
        Run a demonstration of RGB-D processing techniques
        """
        print("RGB-D Camera Processing Demo")
        print("="*40)

        # Simulate an RGB-D frame
        frame = self.simulate_rgbd_frame()
        print(f"Simulated RGB-D frame: {self.width}x{self.height}")

        # Convert to point cloud
        point_cloud = self.depth_to_point_cloud(frame)
        print(f"Generated point cloud with {len(point_cloud)} points")

        # Extract object points
        object_points = self.extract_object_points(frame)
        print(f"Detected {len(object_points)} object points")

        # Calculate object centroid
        centroid = self.calculate_object_centroid(frame)
        if centroid is not None:
            print(f"Object centroid in camera coordinates: ({centroid[0]:.3f}, {centroid[1]:.3f}, {centroid[2]:.3f})")

        # Detect planes
        planes = self.detect_planes(frame)
        print(f"Detected {len(planes)} planes")

        print("\nProcessing steps:")
        print("1. RGB-D frame acquisition (color + depth)")
        print("2. Depth to 3D point cloud conversion")
        print("3. Object segmentation using depth threshold")
        print("4. 3D centroid calculation")
        print("5. Plane detection for environment understanding")

        return frame, point_cloud, object_points


def simulate_lidar_point_cloud(num_points: int = 1000) -> np.ndarray:
    """
    Simulate LIDAR point cloud data for comparison with RGB-D
    """
    # Generate random points in a 2D plane (typical for 2D LIDAR)
    angles = np.random.uniform(0, 2*np.pi, num_points)
    distances = np.random.uniform(0.5, 10.0, num_points)  # 0.5m to 10m range

    x = distances * np.cos(angles)
    y = distances * np.sin(angles)
    z = np.random.uniform(-0.1, 0.1, num_points)  # Small z variation for ground level

    return np.column_stack([x, y, z])


def compare_sensor_modalities():
    """
    Compare RGB-D and LIDAR sensing modalities
    """
    print("\nSensor Modality Comparison")
    print("="*30)

    # RGB-D advantages: color information, dense 3D data, texture
    print("RGB-D Camera Advantages:")
    print("- Color information for object recognition")
    print("- Dense 3D point clouds")
    print("- Texture and appearance data")
    print("- Good for close-range detailed mapping")

    # LIDAR advantages: accuracy, range, reliability
    print("\nLIDAR Advantages:")
    print("- High accuracy distance measurements")
    print("- Works in various lighting conditions")
    print("- Long range capability")
    print("- Reliable geometric data")

    # Simulate point clouds from both
    rgbd_processor = RGBDProcessor()
    _, _, rgbd_points = rgbd_processor.process_rgbd_demo()

    lidar_points = simulate_lidar_point_cloud()
    print(f"\nSimulated LIDAR point cloud with {len(lidar_points)} points")

    print("\nFusion benefits:")
    print("- RGB-D for detailed close objects with color")
    print("- LIDAR for accurate long-range geometry")
    print("- Combined for comprehensive environmental understanding")


def main():
    """
    Main function demonstrating RGB-D camera processing concepts from Chapter 2.
    Shows how RGB-D cameras like RealSense provide rich sensory information.
    """
    print("RGB-D Camera Processing - Chapter 2: Sensor Systems & Perception")
    print("Demonstrating RGB-D camera concepts (e.g., RealSense cameras)\n")

    # Create and run RGB-D processor
    processor = RGBDProcessor()
    processor.process_rgbd_demo()

    # Compare with other sensor modalities
    compare_sensor_modalities()

    print("\n" + "="*60)
    print("Key concepts demonstrated:")
    print("1. RGB-D data acquisition (color + depth)")
    print("2. Depth to 3D point cloud conversion")
    print("3. Object segmentation using depth")
    print("4. 3D centroid calculation for object localization")
    print("5. Plane detection for environment understanding")
    print("6. Comparison with other sensing modalities")


if __name__ == '__main__':
    main()