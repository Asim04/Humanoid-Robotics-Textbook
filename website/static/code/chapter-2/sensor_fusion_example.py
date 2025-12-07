#!/usr/bin/env python3
"""
File: sensor_fusion_example.py
Purpose: Demonstrates sensor fusion concepts with multiple sensor types
Chapter: 2 - Sensor Systems & Perception
Dependencies: numpy
Hardware: None (simulation)
"""

import numpy as np
import time
from dataclasses import dataclass
from typing import Tuple, Optional
import math


@dataclass
class SensorData:
    """
    Container for sensor data from different modalities
    """
    timestamp: float
    lidar_distances: Optional[np.ndarray] = None  # LIDAR distance measurements
    camera_rgb: Optional[np.ndarray] = None       # RGB image data (simulated)
    camera_depth: Optional[np.ndarray] = None     # Depth image data (simulated)
    imu_orientation: Optional[np.ndarray] = None  # Orientation (roll, pitch, yaw)
    imu_angular_velocity: Optional[np.ndarray] = None  # Angular velocity
    imu_linear_acceleration: Optional[np.ndarray] = None  # Linear acceleration
    force_torque: Optional[np.ndarray] = None     # Force/torque measurements (x, y, z, rx, ry, rz)


class SensorFusionSystem:
    """
    A system that demonstrates sensor fusion concepts for Physical AI.
    Integrates data from multiple sensor modalities to create a comprehensive
    understanding of the environment and robot state.
    """

    def __init__(self):
        self.sensor_data_history = []
        self.environment_map = {}  # Simulated environment map

    def simulate_lidar_data(self) -> np.ndarray:
        """
        Simulate LIDAR distance measurements
        Returns array of distances in meters for different angles
        """
        angles = np.linspace(0, 2*np.pi, 360)  # 1-degree resolution
        # Simulate environment with some obstacles
        distances = np.full_like(angles, 10.0)  # Default max range

        # Add some obstacles at specific angles
        for angle_idx in [45, 90, 180, 270]:
            if angle_idx < len(distances):
                distances[angle_idx] = 2.5  # Obstacle at 2.5m
                if angle_idx > 0:
                    distances[angle_idx-1] = 2.6
                    distances[angle_idx+1] = 2.6

        return distances

    def simulate_camera_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate RGB and depth camera data
        Returns RGB image and depth map
        """
        # Simulate a 640x480 RGB image (simplified as a single value per channel)
        rgb_image = np.random.randint(0, 255, size=(480, 640, 3), dtype=np.uint8)

        # Add a "object" in the center
        center_y, center_x = 240, 320
        rgb_image[center_y-50:center_y+50, center_x-50:center_x+50] = [255, 0, 0]  # Red object

        # Simulate depth map (in meters)
        depth_map = np.full((480, 640), 5.0, dtype=np.float32)  # Default distance 5m
        depth_map[center_y-50:center_y+50, center_x-50:center_x+50] = 2.0  # Object at 2m

        return rgb_image, depth_map

    def simulate_imu_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Simulate IMU data: orientation, angular velocity, linear acceleration
        """
        # Simulate small random movements
        orientation = np.array([
            np.random.normal(0, 0.1),      # Roll (radians)
            np.random.normal(0, 0.1),      # Pitch (radians)
            np.random.normal(0, 0.2)       # Yaw (radians)
        ])

        angular_velocity = np.array([
            np.random.normal(0, 0.05),     # Angular velocity around x
            np.random.normal(0, 0.05),     # Angular velocity around y
            np.random.normal(0, 0.05)      # Angular velocity around z
        ])

        linear_acceleration = np.array([
            np.random.normal(0, 0.1),      # Linear acceleration x
            np.random.normal(0, 0.1),      # Linear acceleration y
            9.81 + np.random.normal(0, 0.1)  # Linear acceleration z (gravity + noise)
        ])

        return orientation, angular_velocity, linear_acceleration

    def simulate_force_torque_data(self) -> np.ndarray:
        """
        Simulate force/torque sensor data (6 DOF: Fx, Fy, Fz, Tx, Ty, Tz)
        """
        # Simulate small forces and torques
        force_torque = np.array([
            np.random.normal(0, 0.5),    # Fx
            np.random.normal(0, 0.5),    # Fy
            np.random.normal(0, 1.0),    # Fz (higher variation due to gravity)
            np.random.normal(0, 0.1),    # Tx
            np.random.normal(0, 0.1),    # Ty
            np.random.normal(0, 0.1)     # Tz
        ])

        return force_torque

    def acquire_sensor_data(self) -> SensorData:
        """
        Acquire data from all sensors at the current time step
        """
        timestamp = time.time()

        lidar_data = self.simulate_lidar_data()
        rgb_data, depth_data = self.simulate_camera_data()
        orientation, ang_vel, lin_acc = self.simulate_imu_data()
        force_torque_data = self.simulate_force_torque_data()

        sensor_data = SensorData(
            timestamp=timestamp,
            lidar_distances=lidar_data,
            camera_rgb=rgb_data,
            camera_depth=depth_data,
            imu_orientation=orientation,
            imu_angular_velocity=ang_vel,
            imu_linear_acceleration=lin_acc,
            force_torque=force_torque_data
        )

        self.sensor_data_history.append(sensor_data)
        return sensor_data

    def process_sensor_data(self, sensor_data: SensorData) -> dict:
        """
        Process sensor data to extract meaningful information
        This demonstrates sensor fusion concepts
        """
        processed_data = {}

        # Process LIDAR data - find nearest obstacle
        if sensor_data.lidar_distances is not None:
            min_distance_idx = np.argmin(sensor_data.lidar_distances)
            processed_data['nearest_obstacle_distance'] = sensor_data.lidar_distances[min_distance_idx]
            processed_data['nearest_obstacle_angle'] = np.degrees(min_distance_idx)  # Approximate

        # Process camera data - detect objects
        if sensor_data.camera_rgb is not None:
            # Simple red object detection (in our simulated image)
            red_pixels = np.sum((sensor_data.camera_rgb[:, :, 0] > 200) &
                               (sensor_data.camera_rgb[:, :, 1] < 100) &
                               (sensor_data.camera_rgb[:, :, 2] < 100))
            processed_data['red_objects_detected'] = red_pixels > 1000  # Threshold

        # Process IMU data - calculate tilt
        if sensor_data.imu_orientation is not None:
            roll_deg = math.degrees(sensor_data.imu_orientation[0])
            pitch_deg = math.degrees(sensor_data.imu_orientation[1])
            processed_data['tilt'] = {'roll': roll_deg, 'pitch': pitch_deg}

        # Process force/torque data - check for contact
        if sensor_data.force_torque is not None:
            # Check if significant force is detected (indicating contact)
            force_magnitude = np.linalg.norm(sensor_data.force_torque[:3])
            processed_data['contact_detected'] = force_magnitude > 2.0  # Threshold

        return processed_data

    def run_sensor_fusion_demo(self, steps: int = 10):
        """
        Run a demonstration of sensor fusion for a specified number of steps
        """
        print("Starting Sensor Fusion Demonstration")
        print("="*50)

        for step in range(steps):
            print(f"\nStep {step + 1}:")

            # Acquire sensor data
            sensor_data = self.acquire_sensor_data()
            print(f"  Acquired sensor data at timestamp: {sensor_data.timestamp:.2f}")

            # Process the sensor data
            processed_data = self.process_sensor_data(sensor_data)

            # Display processed information
            if 'nearest_obstacle_distance' in processed_data:
                print(f"  Nearest obstacle: {processed_data['nearest_obstacle_distance']:.2f}m at angle {processed_data['nearest_obstacle_angle']:.1f}°")

            if 'red_objects_detected' in processed_data:
                status = "DETECTED" if processed_data['red_objects_detected'] else "NOT DETECTED"
                print(f"  Red object: {status}")

            if 'tilt' in processed_data:
                tilt = processed_data['tilt']
                print(f"  Tilt - Roll: {tilt['roll']:.2f}°, Pitch: {tilt['pitch']:.2f}°")

            if 'contact_detected' in processed_data:
                contact_status = "CONTACT" if processed_data['contact_detected'] else "NO CONTACT"
                print(f"  End-effector status: {contact_status}")

            time.sleep(0.1)  # Simulate real-time acquisition interval

        print("\n" + "="*50)
        print("Sensor Fusion Demonstration Complete")

        # Summary statistics
        if self.sensor_data_history:
            avg_tilt_roll = np.mean([data.imu_orientation[0] if data.imu_orientation is not None else 0
                                    for data in self.sensor_data_history])
            avg_tilt_pitch = np.mean([data.imu_orientation[1] if data.imu_orientation is not None else 0
                                     for data in self.sensor_data_history])

            print(f"Average tilt - Roll: {math.degrees(avg_tilt_roll):.2f}°, Pitch: {math.degrees(avg_tilt_pitch):.2f}°")


def main():
    """
    Main function demonstrating sensor fusion concepts from Chapter 2.
    Shows integration of multiple sensor modalities for environmental understanding.
    """
    print("Sensor Fusion Example - Chapter 2: Sensor Systems & Perception")
    print("Demonstrating multi-modal sensing and sensor fusion concepts\n")

    # Create and run the sensor fusion system
    fusion_system = SensorFusionSystem()
    fusion_system.run_sensor_fusion_demo(steps=5)

    print("\nKey concepts demonstrated:")
    print("1. Multi-modal sensing (LIDAR, camera, IMU, force/torque)")
    print("2. Sensor data integration for comprehensive understanding")
    print("3. Real-time processing of sensor streams")
    print("4. State estimation from multiple sensor inputs")
    print("5. Environmental perception through sensor fusion")


if __name__ == '__main__':
    main()