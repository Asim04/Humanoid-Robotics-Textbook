#!/usr/bin/env python3
"""
File: ai_training_example.py
Purpose: Example of AI training integration in Isaac Sim
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
import numpy as np
import carb


class IsaacSimAITrainingEnvironment:
    """
    Example of AI training environment in Isaac Sim.
    This class demonstrates how to set up a reinforcement learning environment.
    """
    def __init__(self):
        # Initialize Isaac Sim world
        self.world = World(stage_units_in_meters=1.0)
        self.robot = None
        self.camera = None
        self.lidar = None

        # Training environment properties
        self.episode_step = 0
        self.max_episode_steps = 500
        self.episode_reward = 0.0
        self.cumulative_reward = 0.0

        # Task-specific properties
        self.target_position = np.array([3.0, 3.0, 0.0])
        self.obstacle_positions = [
            np.array([1.0, 1.0, 0.2]),
            np.array([-1.0, -1.0, 0.2]),
            np.array([2.0, -2.0, 0.2]),
            np.array([-2.0, 2.0, 0.2])
        ]

        print("Initialized IsaacSimAITrainingEnvironment")

    def setup_environment(self):
        """Set up the training environment with target and obstacles."""
        # Add default ground plane
        self.world.scene.add_default_ground_plane()

        # Add target object (green cube)
        self.target = self.world.scene.add(
            DynamicCuboid(
                prim_path="/World/Target",
                name="training_target",
                position=self.target_position,
                size=0.3,
                color=np.array([0.1, 0.8, 0.1]),  # Green for target
                mass=0.1  # Light mass so it can be moved if needed
            )
        )

        # Add obstacles
        for i, pos in enumerate(self.obstacle_positions):
            self.world.scene.add(
                DynamicCuboid(
                    prim_path=f"/World/Obstacle{i}",
                    name=f"obstacle_{i}",
                    position=pos,
                    size=0.4,
                    color=np.array([0.8, 0.6, 0.2])  # Brown/orange for obstacles
                )
            )

        # Add walls to contain the environment
        wall_configs = [
            {"pos": [0, 5, 1], "size": [10, 0.2, 2]},
            {"pos": [0, -5, 1], "size": [10, 0.2, 2]},
            {"pos": [5, 0, 1], "size": [0.2, 10, 2]},
            {"pos": [-5, 0, 1], "size": [0.2, 10, 2]}
        ]

        for i, config in enumerate(wall_configs):
            self.world.scene.add(
                DynamicCuboid(
                    prim_path=f"/World/Wall{i}",
                    name=f"wall_{i}",
                    position=np.array(config["pos"]),
                    size=np.array(config["size"]),
                    color=np.array([0.5, 0.5, 0.5]),  # Gray for walls
                    mass=1000.0  # Heavy so they don't move
                )
            )

        print("Training environment setup completed")

    def setup_robot(self):
        """Set up the robot for training."""
        self.robot = self.world.scene.add(
            Robot(
                prim_path="/World/TrainingRobot",
                name="training_robot",
                usd_path="/Isaac/Robots/Carter/carter_model.usd",
                position=np.array([0.0, 0.0, 0.5]),
                orientation=np.array([0.0, 0.0, 0.0, 1.0])
            )
        )

        print("Training robot setup completed")

    def setup_sensors(self):
        """Set up sensors for the training robot."""
        # Add RGB camera for visual input
        self.camera = Camera(
            prim_path="/World/TrainingRobot/Camera",
            position=np.array([0.2, 0.0, 0.1]),
            frequency=30,
            resolution=(224, 224)  # Common size for neural networks
        )
        self.world.scene.add(self.camera)

        # Add LiDAR for proximity sensing
        self.lidar = LidarRtx(
            prim_path="/World/TrainingRobot/Lidar",
            name="Training_Lidar",
            translation=np.array([0.0, 0.0, 0.3]),
            orientation=np.array([0, 0.0, 0.0, 1.0]),
            config="Example_Rotary_Lidar",
            depth_range=10.0,
            frequency=20,
            horizontal_resolution=1.0,  # Lower resolution for faster training
            vertical_resolution=1.0,
            horizontal_fov=360,
            vertical_fov=30
        )
        self.world.scene.add(self.lidar)

        print("Training sensors setup completed")

    def get_observation(self):
        """Get the current observation from sensors."""
        observation = {}

        # Get robot state
        if self.robot:
            pos, ori = self.robot.get_world_pose()
            vel = self.robot.get_linear_velocity()
            ang_vel = self.robot.get_angular_velocity()

            observation["robot_state"] = {
                "position": pos,
                "orientation": ori,
                "linear_velocity": vel,
                "angular_velocity": ang_vel
            }

        # Get camera observation
        try:
            camera_data = self.camera.get_rgb()
            if camera_data is not None:
                observation["camera"] = camera_data
        except Exception:
            observation["camera"] = None

        # Get LiDAR observation
        try:
            lidar_data = self.lidar.get_linear_depth_data()
            if lidar_data is not None:
                observation["lidar"] = lidar_data
        except Exception:
            observation["lidar"] = None

        # Calculate relative target position
        if self.robot:
            robot_pos = observation["robot_state"]["position"]
            relative_target = self.target_position[:2] - robot_pos[:2]
            observation["relative_target"] = relative_target

        return observation

    def calculate_reward(self, action=None):
        """Calculate reward based on current state."""
        if not self.robot:
            return 0.0

        # Get current robot position
        robot_pos, _ = self.robot.get_world_pose()

        # Calculate distance to target
        distance_to_target = np.linalg.norm(self.target_position[:2] - robot_pos[:2])

        # Calculate reward components
        target_reward = -distance_to_target  # Negative distance (closer is better)

        # Bonus for reaching target
        target_bonus = 100.0 if distance_to_target < 0.5 else 0.0

        # Penalty for collision with obstacles
        collision_penalty = 0.0
        for obs_pos in self.obstacle_positions:
            obs_dist = np.linalg.norm(obs_pos[:2] - robot_pos[:2])
            if obs_dist < 0.5:  # Collision threshold
                collision_penalty -= 50.0

        # Small time penalty to encourage efficiency
        time_penalty = -0.1

        total_reward = target_reward * 0.1 + target_bonus + collision_penalty + time_penalty

        return total_reward

    def is_episode_done(self):
        """Check if the episode is done."""
        if not self.robot:
            return True

        # Get robot position
        robot_pos, _ = self.robot.get_world_pose()

        # Check if reached target
        distance_to_target = np.linalg.norm(self.target_position[:2] - robot_pos[:2])
        if distance_to_target < 0.5:
            print("Target reached! Episode completed successfully.")
            return True

        # Check if hit an obstacle
        for obs_pos in self.obstacle_positions:
            obs_dist = np.linalg.norm(obs_pos[:2] - robot_pos[:2])
            if obs_dist < 0.4:  # Collision threshold
                print("Collision with obstacle! Episode terminated.")
                return True

        # Check if exceeded maximum steps
        if self.episode_step >= self.max_episode_steps:
            print("Maximum steps exceeded! Episode terminated.")
            return True

        return False

    def reset_episode(self):
        """Reset the episode to initial state."""
        # Reset robot position
        if self.robot:
            self.robot.set_world_pose(
                position=np.array([0.0, 0.0, 0.5]),
                orientation=np.array([0.0, 0.0, 0.0, 1.0])
            )
            self.robot.set_linear_velocity(np.array([0.0, 0.0, 0.0]))
            self.robot.set_angular_velocity(np.array([0.0, 0.0, 0.0]))

        # Reset episode counters
        self.episode_step = 0
        self.episode_reward = 0.0

        print("Episode reset completed")

    def execute_action(self, action):
        """
        Execute an action in the environment.
        In a real implementation, this would control the robot's motors.
        For this example, we'll simulate movement based on action.
        """
        if not self.robot:
            return

        # Action is expected to be [linear_velocity, angular_velocity]
        # In a real implementation, you would command the robot's actuators
        linear_vel = np.clip(action[0], -1.0, 1.0)  # Limit linear velocity
        angular_vel = np.clip(action[1], -1.0, 1.0)  # Limit angular velocity

        # For demonstration purposes, we'll just print the action
        print(f"Executing action - Linear: {linear_vel:.2f}, Angular: {angular_vel:.2f}")

    def run_training_episode(self, max_steps=500):
        """Run a single training episode."""
        print(f"Starting training episode for {max_steps} steps...")

        # Reset episode
        self.reset_episode()

        # Reset the world to initialize physics
        self.world.reset()

        step_count = 0
        total_reward = 0.0

        while step_count < max_steps:
            # Step the physics simulation
            self.world.step(render=True)

            # Get current observation
            observation = self.get_observation()

            # Calculate reward
            reward = self.calculate_reward()
            total_reward += reward
            self.episode_reward += reward

            # Check if episode is done
            done = self.is_episode_done()

            # For this example, we'll use a simple random action
            # In a real RL implementation, this would come from the agent
            random_action = [np.random.uniform(-1.0, 1.0), np.random.uniform(-1.0, 1.0)]
            self.execute_action(random_action)

            # Print status periodically
            if step_count % 50 == 0:
                robot_pos, _ = self.robot.get_world_pose() if self.robot else (np.array([0, 0, 0]), None)
                distance_to_target = np.linalg.norm(self.target_position[:2] - robot_pos[:2])
                print(f"Step {step_count}: Pos=({robot_pos[0]:.2f}, {robot_pos[1]:.2f}), "
                      f"Dist to target={distance_to_target:.2f}, Reward={reward:.2f}, Total={total_reward:.2f}")

            # Increment step count
            self.episode_step += 1
            step_count += 1

            # Break if episode is done
            if done:
                break

        print(f"Episode completed after {step_count} steps. Total reward: {total_reward:.2f}")
        return total_reward

    def run_multiple_episodes(self, num_episodes=5):
        """Run multiple training episodes."""
        print(f"Starting {num_episodes} training episodes...")

        for episode in range(num_episodes):
            print(f"\n--- Episode {episode + 1} ---")
            episode_reward = self.run_training_episode(max_steps=300)
            self.cumulative_reward += episode_reward

            # Reset for next episode
            self.reset_episode()

            print(f"Episode {episode + 1} completed. Reward: {episode_reward:.2f}, "
                  f"Cumulative: {self.cumulative_reward:.2f}")

        print(f"\nAll {num_episodes} episodes completed. Average reward: {self.cumulative_reward / num_episodes:.2f}")

    def cleanup(self):
        """Clean up the simulation."""
        self.world.clear()
        print("AI training environment cleaned up")


def main():
    """Main function to run the Isaac Sim AI training example."""
    print("Starting Isaac Sim AI Training Example")

    # Create and setup the training environment
    env = IsaacSimAITrainingEnvironment()

    try:
        # Set up the environment
        env.setup_environment()

        # Set up the robot
        env.setup_robot()

        # Set up sensors
        env.setup_sensors()

        # Run multiple training episodes
        env.run_multiple_episodes(num_episodes=3)

    except Exception as e:
        print(f"Error during AI training simulation: {e}")
        carb.log_error(f"AI training simulation error: {e}")

    finally:
        # Clean up
        env.cleanup()


if __name__ == "__main__":
    main()