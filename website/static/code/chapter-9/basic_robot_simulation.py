#!/usr/bin/env python3
"""
File: basic_robot_simulation.py
Purpose: Basic Isaac Sim robot simulation example
Chapter: 9 - NVIDIA Isaac Sim
Dependencies: omni.isaac.core, omni.isaac.range_sensor
Hardware: Isaac Sim simulation environment
"""

import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.prims import get_prim_at_path
from omni.isaac.core.robots import Robot
from omni.isaac.core.objects import DynamicCuboid
from omni.isaac.sensor import Camera
from omni.isaac.range_sensor import LidarRtx
import numpy as np
import carb


class BasicIsaacSimRobot:
    """
    Basic robot simulation in Isaac Sim demonstrating core concepts.
    """
    def __init__(self):
        # Initialize Isaac Sim world
        self.world = World(stage_units_in_meters=1.0)
        self.robot = None
        self.camera = None
        self.lidar = None

        # Robot properties
        self.initial_position = np.array([0.0, 0.0, 0.5])
        self.target_position = np.array([2.0, 2.0, 0.0])

        print("Initialized BasicIsaacSimRobot")

    def setup_environment(self):
        """Set up the simulation environment with ground plane and objects."""
        # Add default ground plane
        self.world.scene.add_default_ground_plane()

        # Add some objects to the environment
        self.world.scene.add(
            DynamicCuboid(
                prim_path="/World/Box1",
                name="box1",
                position=np.array([1.0, 1.0, 0.25]),
                size=0.5,
                color=np.array([0.8, 0.1, 0.1])
            )
        )

        self.world.scene.add(
            DynamicCuboid(
                prim_path="/World/Box2",
                name="box2",
                position=np.array([-1.0, -1.0, 0.25]),
                size=0.5,
                color=np.array([0.1, 0.8, 0.1])
            )
        )

        print("Environment setup completed")

    def setup_robot(self):
        """Set up the robot with sensors."""
        # Add robot to the scene - using a basic differential drive robot
        self.robot = self.world.scene.add(
            Robot(
                prim_path="/World/Robot",
                name="my_robot",
                # Using a standard Isaac robot model - adjust path as needed
                usd_path="/Isaac/Robots/Carter/carter_model.usd",
                position=self.initial_position,
                orientation=np.array([0.0, 0.0, 0.0, 1.0])
            )
        )

        print("Robot setup completed")

    def setup_sensors(self):
        """Add sensors to the robot."""
        # Add camera sensor
        self.camera = Camera(
            prim_path="/World/Robot/Camera",
            position=np.array([0.2, 0.0, 0.1]),
            frequency=30,
            resolution=(640, 480)
        )
        self.world.scene.add(self.camera)

        # Add LiDAR sensor
        self.lidar = LidarRtx(
            prim_path="/World/Robot/Lidar",
            name="Lidar_Sensor",
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

    def simple_navigation(self):
        """Simple navigation function to move robot toward target."""
        if self.robot is None:
            return False

        # Get current robot position
        current_pos, current_ori = self.robot.get_world_pose()

        # Calculate direction to target (only X,Y for 2D navigation)
        direction = self.target_position[:2] - current_pos[:2]
        distance = np.linalg.norm(direction)

        # If close enough to target, return True
        if distance < 0.5:
            print(f"Reached target! Distance: {distance:.2f}")
            return True

        # Normalize direction
        if distance > 0:
            direction = direction / distance

        print(f"Moving toward target, current pos: ({current_pos[0]:.2f}, {current_pos[1]:.2f}), distance: {distance:.2f}")
        return False

    def run_simulation(self, steps=1000):
        """Run the simulation for a specified number of steps."""
        print(f"Starting simulation for {steps} steps...")

        # Reset the world to initialize physics
        self.world.reset()

        reached_target = False

        for step in range(steps):
            # Step the physics simulation
            self.world.step(render=True)

            # Simple navigation - move toward target
            if not reached_target:
                reached_target = self.simple_navigation()

            # Capture sensor data periodically
            if step % 60 == 0:  # Every 2 seconds at 30Hz
                try:
                    camera_data = self.camera.get_rgb()
                    if camera_data is not None:
                        print(f"Step {step}: Captured camera image with shape {camera_data.shape}")
                except Exception as e:
                    print(f"Camera capture error: {e}")

            if step % 40 == 0:  # Every 2 seconds at 20Hz
                try:
                    lidar_data = self.lidar.get_linear_depth_data()
                    if lidar_data is not None:
                        print(f"Step {step}: Captured LiDAR data with {len(lidar_data)} points")
                except Exception as e:
                    print(f"LiDAR capture error: {e}")

            # Print status periodically
            if step % 100 == 0:
                if self.robot:
                    pos, _ = self.robot.get_world_pose()
                    print(f"Step {step}: Robot position ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

        print("Simulation completed!")

    def cleanup(self):
        """Clean up the simulation."""
        self.world.clear()
        print("Simulation cleaned up")


def main():
    """Main function to run the basic Isaac Sim robot simulation."""
    print("Starting Basic Isaac Sim Robot Simulation")

    # Create and setup the simulation
    sim = BasicIsaacSimRobot()

    try:
        # Set up the environment
        sim.setup_environment()

        # Set up the robot
        sim.setup_robot()

        # Set up sensors
        sim.setup_sensors()

        # Run the simulation
        sim.run_simulation(steps=1000)

    except Exception as e:
        print(f"Error during simulation: {e}")
        carb.log_error(f"Simulation error: {e}")

    finally:
        # Clean up
        sim.cleanup()


if __name__ == "__main__":
    main()