#!/usr/bin/env python3
"""
File: sensor_fusion_example.py
Purpose: Example of sensor fusion in Isaac Sim using camera and LiDAR
Chapter: 9 - NVIDIA Isaac Sim
Dependencies: omni.isaac.core, omni.isaac.range_sensor, omni.isaac.sensor
Hardware: Isaac Sim simulation environment
"""

import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.robots import Robot
from omni.isaac.core.objects import DynamicCuboid
from omni.isaac.sensor import Camera
from omni.isaac.range_sensor import LidarRtx
from omni.isaac.core.utils.prims import set_targets
import numpy as np
import cv2  # For image processing (install with: pip install opencv-python)
import carb


class IsaacSimSensorFusion:
    """
    Example of sensor fusion in Isaac Sim combining camera and LiDAR data.
    """
    def __init__(self):
        # Initialize Isaac Sim world
        self.world = World(stage_units_in_meters=1.0)
        self.robot = None
        self.camera = None
        self.lidar = None

        # Sensor fusion properties
        self.camera_data = None
        self.lidar_data = None
        self.fusion_data = {}

        print("Initialized IsaacSimSensorFusion")

    def setup_environment(self):
        """Set up the simulation environment with multiple objects."""
        # Add default ground plane
        self.world.scene.add_default_ground_plane()

        # Add various objects with different properties
        objects_config = [
            {"name": "red_box", "pos": [1.5, 1.0, 0.25], "size": 0.4, "color": [0.8, 0.1, 0.1]},
            {"name": "green_cylinder", "pos": [-1.5, -1.0, 0.3], "size": 0.3, "color": [0.1, 0.8, 0.1]},
            {"name": "blue_sphere", "pos": [0.0, 2.0, 0.2], "size": 0.35, "color": [0.1, 0.1, 0.8]},
            {"name": "yellow_box", "pos": [-2.0, 1.5, 0.2], "size": 0.3, "color": [0.8, 0.8, 0.1]},
            {"name": "purple_box", "pos": [2.0, -1.5, 0.2], "size": 0.3, "color": [0.8, 0.1, 0.8]}
        ]

        for i, obj_config in enumerate(objects_config):
            self.world.scene.add(
                DynamicCuboid(
                    prim_path=f"/World/Object{i}",
                    name=obj_config["name"],
                    position=np.array(obj_config["pos"]),
                    size=obj_config["size"],
                    color=np.array(obj_config["color"])
                )
            )

        print("Environment with objects setup completed")

    def setup_robot(self):
        """Set up the robot."""
        self.robot = self.world.scene.add(
            Robot(
                prim_path="/World/Robot",
                name="sensor_fusion_robot",
                usd_path="/Isaac/Robots/Carter/carter_model.usd",
                position=np.array([0.0, 0.0, 0.5]),
                orientation=np.array([0.0, 0.0, 0.0, 1.0])
            )
        )

        print("Robot setup completed")

    def setup_sensors(self):
        """Set up multiple sensors for fusion."""
        # Add RGB camera
        self.camera = Camera(
            prim_path="/World/Robot/RGB_Camera",
            position=np.array([0.2, 0.0, 0.1]),
            frequency=30,
            resolution=(640, 480)
        )
        self.world.scene.add(self.camera)

        # Add depth camera
        self.depth_camera = Camera(
            prim_path="/World/Robot/Depth_Camera",
            position=np.array([0.2, 0.05, 0.1]),
            frequency=30,
            resolution=(640, 480)
        )
        self.world.scene.add(self.depth_camera)

        # Add LiDAR sensor
        self.lidar = LidarRtx(
            prim_path="/World/Robot/Lidar",
            name="Fusion_Lidar",
            translation=np.array([0.0, 0.0, 0.3]),
            orientation=np.array([0, 0.0, 0.0, 1.0]),
            config="Example_Rotary_Lidar",
            depth_range=20.0,
            frequency=20,
            horizontal_resolution=0.5,
            vertical_resolution=0.5,
            horizontal_fov=360,
            vertical_fov=30
        )
        self.world.scene.add(self.lidar)

        print("Sensors setup completed")

    def process_camera_data(self, rgb_image, depth_image):
        """Process camera data for object detection and analysis."""
        if rgb_image is None or depth_image is None:
            return None

        # Convert Isaac Sim format to OpenCV format
        # Note: Isaac Sim returns data in different formats depending on the sensor
        # This is a simplified example - actual implementation may vary
        try:
            # For demonstration, we'll just return basic info
            height, width, channels = rgb_image.shape
            avg_color = np.mean(rgb_image, axis=(0, 1))

            processed_data = {
                "resolution": (width, height),
                "avg_color": avg_color,
                "depth_avg": np.mean(depth_image) if depth_image is not None else 0
            }

            return processed_data
        except Exception as e:
            print(f"Error processing camera data: {e}")
            return None

    def process_lidar_data(self, lidar_points):
        """Process LiDAR data for obstacle detection and mapping."""
        if lidar_points is None:
            return None

        try:
            # Convert to numpy array if needed
            points = np.array(lidar_points)

            # Basic processing: find nearest obstacle
            if len(points) > 0:
                # Remove invalid points (inf, nan)
                valid_points = points[np.isfinite(points)]

                if len(valid_points) > 0:
                    # Calculate basic statistics
                    min_distance = np.min(valid_points)
                    max_distance = np.max(valid_points)
                    avg_distance = np.mean(valid_points)

                    # Find points within certain range (obstacle detection)
                    obstacle_threshold = 2.0  # meters
                    obstacles = valid_points[valid_points < obstacle_threshold]

                    processed_data = {
                        "min_distance": min_distance,
                        "max_distance": max_distance,
                        "avg_distance": avg_distance,
                        "num_obstacles": len(obstacles),
                        "obstacle_threshold": obstacle_threshold
                    }

                    return processed_data

            return None
        except Exception as e:
            print(f"Error processing LiDAR data: {e}")
            return None

    def fuse_sensor_data(self, camera_processed, lidar_processed):
        """Fuse processed camera and LiDAR data."""
        if camera_processed is None or lidar_processed is None:
            return None

        # Simple fusion: combine information from both sensors
        fused_data = {
            "camera_info": camera_processed,
            "lidar_info": lidar_processed,
            "environment_analysis": {
                "obstacle_detected": lidar_processed["num_obstacles"] > 0,
                "obstacle_distance": lidar_processed["min_distance"] if lidar_processed["num_obstacles"] > 0 else float('inf'),
                "color_info": camera_processed["avg_color"],
                "depth_info": camera_processed["depth_avg"]
            }
        }

        return fused_data

    def run_sensor_fusion_simulation(self, steps=500):
        """Run the sensor fusion simulation."""
        print(f"Starting sensor fusion simulation for {steps} steps...")

        # Reset the world to initialize physics
        self.world.reset()

        for step in range(steps):
            # Step the physics simulation
            self.world.step(render=True)

            # Capture sensor data periodically
            if step % 30 == 0:  # Every 1 second at 30Hz
                try:
                    # Capture camera data
                    rgb_data = self.camera.get_rgb()
                    depth_data = self.depth_camera.get_depth()

                    # Process camera data
                    camera_processed = self.process_camera_data(rgb_data, depth_data)

                    # Capture and process LiDAR data
                    lidar_raw = self.lidar.get_linear_depth_data()
                    lidar_processed = self.process_lidar_data(lidar_raw)

                    # Fuse the data
                    if camera_processed and lidar_processed:
                        fused_data = self.fuse_sensor_data(camera_processed, lidar_processed)

                        if fused_data:
                            env_analysis = fused_data["environment_analysis"]
                            print(f"Step {step}: Fused sensor analysis:")
                            print(f"  - Obstacle detected: {env_analysis['obstacle_detected']}")
                            print(f"  - Nearest obstacle: {env_analysis['obstacle_distance']:.2f}m")
                            print(f"  - Average color: [{env_analysis['color_info'][0]:.2f}, {env_analysis['color_info'][1]:.2f}, {env_analysis['color_info'][2]:.2f}]")
                            print(f"  - Average depth: {env_analysis['depth_info']:.2f}m")

                except Exception as e:
                    print(f"Error in sensor fusion step {step}: {e}")

            # Print robot status periodically
            if step % 100 == 0 and self.robot:
                pos, ori = self.robot.get_world_pose()
                print(f"Step {step}: Robot position ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

        print("Sensor fusion simulation completed!")

    def cleanup(self):
        """Clean up the simulation."""
        self.world.clear()
        print("Sensor fusion simulation cleaned up")


def main():
    """Main function to run the Isaac Sim sensor fusion example."""
    print("Starting Isaac Sim Sensor Fusion Example")

    # Create and setup the simulation
    sim = IsaacSimSensorFusion()

    try:
        # Set up the environment
        sim.setup_environment()

        # Set up the robot
        sim.setup_robot()

        # Set up sensors
        sim.setup_sensors()

        # Run the sensor fusion simulation
        sim.run_sensor_fusion_simulation(steps=500)

    except Exception as e:
        print(f"Error during sensor fusion simulation: {e}")
        carb.log_error(f"Sensor fusion simulation error: {e}")

    finally:
        # Clean up
        sim.cleanup()


if __name__ == "__main__":
    main()