#!/usr/bin/env python3
"""
File: imu_proprioception.py
Purpose: Demonstrates IMU and proprioception concepts for robot state estimation
Chapter: 2 - Sensor Systems & Perception
Dependencies: numpy, math
Hardware: None (simulation)
"""

import numpy as np
import math
from dataclasses import dataclass
from typing import Tuple, Optional
import time


@dataclass
class IMUData:
    """
    Container for IMU sensor data
    """
    timestamp: float
    orientation: np.ndarray      # [roll, pitch, yaw] in radians
    angular_velocity: np.ndarray # [wx, wy, wz] in rad/s
    linear_acceleration: np.ndarray # [ax, ay, az] in m/s^2
    temperature: Optional[float] = None  # Temperature in Celsius


@dataclass
class JointState:
    """
    Container for joint position/proprioception data
    """
    timestamp: float
    joint_positions: np.ndarray    # Joint angles in radians
    joint_velocities: np.ndarray   # Joint velocities in rad/s
    joint_efforts: np.ndarray      # Joint torques in Nm


class IMUProprioceptionFusion:
    """
    Demonstrates integration of IMU and proprioception data
    for robot state estimation and awareness
    """

    def __init__(self, num_joints: int = 6):
        self.num_joints = num_joints
        self.gravity = 9.81  # m/s^2
        self.orientation_history = []
        self.position_history = []

    def simulate_imu_data(self, dt: float = 0.01) -> IMUData:
        """
        Simulate IMU data with realistic noise and bias
        """
        current_time = time.time()

        # Simulate a robot moving with some acceleration
        # Add some oscillation to simulate walking or movement
        movement_freq = 0.5  # Hz
        movement_amplitude = 0.2  # m/s^2

        # Simulate orientation changes (small movements)
        roll = 0.1 * math.sin(2 * math.pi * movement_freq * current_time)
        pitch = 0.05 * math.cos(2 * math.pi * movement_freq * current_time)
        yaw = 0.02 * math.sin(2 * math.pi * movement_freq * current_time)

        # Simulate angular velocities
        w_roll = 0.1 * 2 * math.pi * movement_freq * math.cos(2 * math.pi * movement_freq * current_time)
        w_pitch = -0.05 * 2 * math.pi * movement_freq * math.sin(2 * math.pi * movement_freq * current_time)
        w_yaw = 0.02 * 2 * math.pi * movement_freq * math.cos(2 * math.pi * movement_freq * current_time)

        # Simulate linear accelerations (with gravity)
        ax = movement_amplitude * math.cos(2 * math.pi * movement_freq * current_time)
        ay = movement_amplitude * math.sin(2 * math.pi * movement_freq * current_time)
        az = self.gravity + movement_amplitude * math.sin(4 * math.pi * movement_freq * current_time)

        # Add realistic sensor noise
        noise_std = 0.001
        ax += np.random.normal(0, noise_std)
        ay += np.random.normal(0, noise_std)
        az += np.random.normal(0, noise_std)

        # Add angular velocity noise
        w_noise_std = 0.0005
        w_roll += np.random.normal(0, w_noise_std)
        w_pitch += np.random.normal(0, w_noise_std)
        w_yaw += np.random.normal(0, w_noise_std)

        return IMUData(
            timestamp=current_time,
            orientation=np.array([roll, pitch, yaw]),
            angular_velocity=np.array([w_roll, w_pitch, w_yaw]),
            linear_acceleration=np.array([ax, ay, az]),
            temperature=25.0 + np.random.normal(0, 0.5)  # Room temperature + noise
        )

    def simulate_joint_states(self) -> JointState:
        """
        Simulate proprioceptive joint state data
        """
        current_time = time.time()

        # Simulate joint positions (oscillating pattern)
        joint_positions = np.zeros(self.num_joints)
        for i in range(self.num_joints):
            freq = 0.5 + i * 0.1  # Different frequencies for each joint
            joint_positions[i] = 0.5 * math.sin(2 * math.pi * freq * current_time)

        # Calculate velocities (derivative of positions)
        joint_velocities = np.zeros(self.num_joints)
        for i in range(self.num_joints):
            freq = 0.5 + i * 0.1
            joint_velocities[i] = 0.5 * 2 * math.pi * freq * math.cos(2 * math.pi * freq * current_time)

        # Simulate efforts (torques) based on movement
        joint_efforts = 0.1 * joint_positions + 0.05 * joint_velocities  # Simple model

        return JointState(
            timestamp=current_time,
            joint_positions=joint_positions,
            joint_velocities=joint_velocities,
            joint_efforts=joint_efforts
        )

    def integrate_imu_for_position(self, imu_data: IMUData, dt: float = 0.01) -> np.ndarray:
        """
        Integrate IMU acceleration data to estimate position change
        This demonstrates dead reckoning using IMU
        """
        # Remove gravity from z-axis acceleration
        linear_acc_no_gravity = imu_data.linear_acceleration.copy()
        # This is a simplified approach - in reality, you'd need to transform gravity
        # based on orientation
        gravity_vector = np.array([0, 0, self.gravity])

        # For this simulation, assume we roughly know orientation
        # and can remove gravity component
        roll, pitch, yaw = imu_data.orientation
        gravity_x = self.gravity * math.sin(pitch)
        gravity_y = -self.gravity * math.sin(roll) * math.cos(pitch)
        gravity_z = self.gravity * math.cos(roll) * math.cos(pitch)

        gravity_compensated = np.array([
            linear_acc_no_gravity[0] - gravity_x,
            linear_acc_no_gravity[1] - gravity_y,
            linear_acc_no_gravity[2] - gravity_z
        ])

        # Integrate acceleration to get velocity change
        velocity_change = gravity_compensated * dt

        # For position change, we'd need to integrate velocity too
        # For this demo, just return the velocity change
        return velocity_change

    def estimate_robot_state(self, imu_data: IMUData, joint_states: JointState) -> dict:
        """
        Estimate overall robot state by fusing IMU and proprioception data
        """
        state = {}

        # Extract orientation from IMU
        roll, pitch, yaw = imu_data.orientation
        state['imu_orientation'] = {
            'roll_deg': math.degrees(roll),
            'pitch_deg': math.degrees(pitch),
            'yaw_deg': math.degrees(yaw)
        }

        # Extract body velocity from IMU integration (simplified)
        # In practice, this would be more complex due to drift
        acc_x, acc_y, acc_z = imu_data.linear_acceleration
        # Remove gravity approximation
        approx_body_acc_x = acc_x
        approx_body_acc_y = acc_y
        approx_body_acc_z = acc_z - self.gravity

        state['estimated_body_acceleration'] = [approx_body_acc_x, approx_body_acc_y, approx_body_acc_z]

        # Joint information from proprioception
        state['joint_positions'] = joint_states.joint_positions.tolist()
        state['joint_velocities'] = joint_states.joint_velocities.tolist()
        state['joint_efforts'] = joint_states.joint_efforts.tolist()

        # Estimate if robot is moving based on IMU
        linear_acc_magnitude = np.linalg.norm(imu_data.linear_acceleration)
        state['is_moving'] = linear_acc_magnitude > (self.gravity * 1.1)  # Threshold

        # Estimate stability based on angular velocity
        ang_vel_magnitude = np.linalg.norm(imu_data.angular_velocity)
        state['stability'] = 'stable' if ang_vel_magnitude < 0.1 else 'unstable'

        return state

    def run_state_estimation_demo(self, steps: int = 50):
        """
        Run a demonstration of state estimation using IMU and proprioception
        """
        print("IMU and Proprioception State Estimation Demo")
        print("="*50)

        dt = 0.02  # 50Hz update rate

        for step in range(steps):
            # Acquire sensor data
            imu_data = self.simulate_imu_data(dt)
            joint_states = self.simulate_joint_states()

            # Estimate robot state
            robot_state = self.estimate_robot_state(imu_data, joint_states)

            if step % 10 == 0:  # Print every 10 steps
                print(f"\nStep {step + 1}:")
                print(f"  IMU Orientation - Roll: {robot_state['imu_orientation']['roll_deg']:.2f}°, "
                      f"Pitch: {robot_state['imu_orientation']['pitch_deg']:.2f}°, "
                      f"Yaw: {robot_state['imu_orientation']['yaw_deg']:.2f}°")
                print(f"  Joint 0 position: {robot_state['joint_positions'][0]:.3f} rad")
                print(f"  Robot moving: {robot_state['is_moving']}")
                print(f"  Stability: {robot_state['stability']}")

            # Store for history
            self.orientation_history.append(imu_data.orientation.copy())
            time.sleep(0.001)  # Small delay to simulate real-time

        print(f"\nCompleted {steps} estimation steps")
        print(f"Collected {len(self.orientation_history)} orientation samples")

        # Calculate statistics
        if self.orientation_history:
            orientations = np.array(self.orientation_history)
            avg_roll = np.mean(orientations[:, 0])
            avg_pitch = np.mean(orientations[:, 1])
            avg_yaw = np.mean(orientations[:, 2])

            print(f"Average orientation - Roll: {math.degrees(avg_roll):.2f}°, "
                  f"Pitch: {math.degrees(avg_pitch):.2f}°, "
                  f"Yaw: {math.degrees(avg_yaw):.2f}°")

    def demonstrate_sensor_fusion_benefits(self):
        """
        Demonstrate the benefits of combining IMU and proprioception
        """
        print("\nSensor Fusion Benefits Demonstration")
        print("="*40)

        print("Individual sensor limitations:")
        print("• IMU alone:")
        print("  - Good for orientation and external motion")
        print("  - Subject to drift over time")
        print("  - Cannot distinguish between robot movement and joint movement")
        print("  - Affected by vibration and external forces")

        print("\n• Proprioception alone:")
        print("  - Good for joint configuration and internal state")
        print("  - Cannot determine absolute orientation in world")
        print("  - Cannot detect external forces or movement")

        print("\nCombined benefits:")
        print("• Complete state estimation (position, orientation, joint states)")
        print("• Compensation for individual sensor limitations")
        print("• Robust detection of robot-environment interactions")
        print("• Accurate motion planning and control")

        # Simulate a scenario where both sensors are needed
        print("\nExample scenario: Robot arm reaching")
        print("- IMU detects overall robot movement/tilt")
        print("- Proprioception detects joint angles for precise positioning")
        print("- Combined: Know exact end-effector position in world frame")


def main():
    """
    Main function demonstrating IMU and proprioception concepts from Chapter 2.
    Shows how these sensors provide robot self-awareness and environmental interaction.
    """
    print("IMU and Proprioception - Chapter 2: Sensor Systems & Perception")
    print("Demonstrating IMU and proprioception for robot state estimation\n")

    # Create and run the fusion system
    fusion_system = IMUProprioceptionFusion(num_joints=6)
    fusion_system.run_state_estimation_demo(steps=20)

    # Demonstrate benefits
    fusion_system.demonstrate_sensor_fusion_benefits()

    print("\n" + "="*60)
    print("Key concepts demonstrated:")
    print("1. IMU data acquisition (orientation, angular velocity, linear acceleration)")
    print("2. Proprioceptive joint state sensing")
    print("3. State estimation by fusing multiple sensor modalities")
    print("4. Dead reckoning and position estimation from IMU")
    print("5. Robot self-awareness through sensor fusion")
    print("6. Compensation for individual sensor limitations")


if __name__ == '__main__':
    main()