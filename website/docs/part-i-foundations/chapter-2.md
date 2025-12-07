---
sidebar_position: 2
---

# Chapter 2: Sensor Systems & Perception

Sensors form the foundation of Physical AI systems, providing the necessary information to understand and interact with the physical world. This chapter explores the fundamental sensor technologies that enable robots to perceive their environment and internal state, including LIDAR, RGB-D cameras, IMUs, and force/torque sensors.

## Learning Objectives

After completing this chapter, students will be able to:

- Explain the fundamental principles of LIDAR sensing and its applications
- Describe RGB-D camera technology and its advantages over traditional cameras
- Understand IMU and proprioception concepts for robot state estimation
- Identify force/torque sensing applications in robotic manipulation
- Apply sensor fusion techniques to integrate multiple sensor modalities
- Analyze challenges in sensor systems and their impact on Physical AI

## Introduction to Sensor Systems

Physical AI systems rely on multiple sensor modalities to gather information about their environment and internal state. Unlike traditional digital AI systems that operate on well-defined inputs, Physical AI must contend with continuous, noisy, and uncertain sensor data. The integration of multiple sensor types through sensor fusion enables robots to build comprehensive models of their surroundings and make informed decisions.

### Key Sensor Categories

Physical AI systems typically employ four primary sensor categories:

1. **Environmental Perception Sensors**: LIDAR, cameras, ultrasonic sensors
2. **Inertial Sensors**: IMUs, gyroscopes, accelerometers
3. **Proprioceptive Sensors**: Joint encoders, force/torque sensors
4. **Exteroceptive Sensors**: Tactile sensors, proximity sensors

## LIDAR Fundamentals

Light Detection and Ranging (LIDAR) sensors provide high-accuracy distance measurements by emitting laser pulses and measuring the time-of-flight to reflective surfaces. LIDAR systems generate dense 3D point clouds that enable precise mapping, localization, and obstacle detection.

### How LIDAR Works

LIDAR sensors operate by emitting laser pulses and measuring the time it takes for the light to return after reflecting off objects. The distance is calculated using the formula:

$$ d = \frac{c \cdot \Delta t}{2} $$

where $d$ is the distance, $c$ is the speed of light, and $\Delta t$ is the time-of-flight.

### LIDAR Data Processing

The following code example demonstrates how to process LIDAR data and extract meaningful information:

```python
#!/usr/bin/env python3
"""
File: sensor_fusion_example.py (LIDAR section)
Purpose: Demonstrates LIDAR data processing concepts
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

    def process_lidar_data(self, lidar_data: np.ndarray) -> dict:
        """
        Process LIDAR data to extract meaningful information
        """
        processed_data = {}

        # Find nearest obstacle
        min_distance_idx = np.argmin(lidar_data)
        processed_data['nearest_obstacle_distance'] = lidar_data[min_distance_idx]
        processed_data['nearest_obstacle_angle'] = np.degrees(min_distance_idx)  # Approximate

        # Find all obstacles within a certain range
        obstacle_threshold = 3.0  # meters
        obstacle_indices = np.where(lidar_data < obstacle_threshold)[0]
        processed_data['obstacle_count'] = len(obstacle_indices)

        # Calculate free space
        free_space_indices = np.where(lidar_data >= obstacle_threshold)[0]
        processed_data['free_space_percentage'] = len(free_space_indices) / len(lidar_data) * 100

        return processed_data

# Example usage
fusion_system = SensorFusionSystem()
lidar_data = fusion_system.simulate_lidar_data()
lidar_processed = fusion_system.process_lidar_data(lidar_data)

print("LIDAR Data Processing Results:")
print(f"Nearest obstacle: {lidar_processed['nearest_obstacle_distance']:.2f}m at angle {lidar_processed['nearest_obstacle_angle']:.1f}°")
print(f"Obstacles detected: {lidar_processed['obstacle_count']}")
print(f"Free space: {lidar_processed['free_space_percentage']:.1f}%")
```

For the complete implementation, see [sensor_fusion_example.py](/static/code/chapter-2/sensor_fusion_example.py).

### LIDAR Applications

LIDAR sensors are particularly valuable for:

- **Mapping and SLAM**: Creating detailed 2D/3D maps of environments
- **Obstacle Detection**: Identifying and localizing obstacles for navigation
- **Localization**: Determining robot position in known maps
- **Perimeter Monitoring**: Detecting intrusions or safety zones

## RGB-D Cameras (RealSense)

RGB-D cameras provide both color (RGB) and depth information, enabling rich 3D scene understanding. Popular sensors like Intel RealSense cameras combine traditional color imaging with active depth sensing technologies such as structured light or time-of-flight.

### RGB-D Data Integration

RGB-D cameras provide complementary information: color data for object recognition and texture, and depth data for 3D structure and spatial relationships.

```python
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

        print("\nProcessing steps:")
        print("1. RGB-D frame acquisition (color + depth)")
        print("2. Depth to 3D point cloud conversion")
        print("3. Object segmentation using depth threshold")
        print("4. 3D centroid calculation")

        return frame, point_cloud, object_points

# Example usage
processor = RGBDProcessor()
processor.process_rgbd_demo()
```

For the complete implementation, see [rgbd_processing.py](/static/code/chapter-2/rgbd_processing.py).

### RGB-D vs. Traditional Cameras

RGB-D cameras offer several advantages over traditional cameras:

- **Depth Information**: Direct 3D structure without complex stereo processing
- **Robustness**: Works in low-light conditions where stereo fails
- **Dense Data**: Provides depth for every pixel rather than sparse features
- **Real-time Processing**: Depth data available at full frame rate

## IMUs and Proprioception

Inertial Measurement Units (IMUs) and proprioceptive sensors provide critical information about the robot's internal state and movement. IMUs measure linear acceleration and angular velocity, while proprioceptive sensors monitor joint positions, velocities, and efforts.

### IMU Fundamentals

An IMU typically contains three types of sensors:

1. **Accelerometer**: Measures linear acceleration along three axes
2. **Gyroscope**: Measures angular velocity around three axes
3. **Magnetometer**: Measures magnetic field for heading reference

```python
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

# Example usage
fusion_system = IMUProprioceptionFusion(num_joints=6)
fusion_system.run_state_estimation_demo(steps=20)
```

For the complete implementation, see [imu_proprioception.py](/static/code/chapter-2/imu_proprioception.py).

### Proprioception in Robotics

Proprioception refers to a robot's awareness of its own body state. This includes:

- **Joint Position**: Current configuration of all joints
- **Joint Velocity**: Speed of joint movement
- **Joint Effort**: Torque/force applied at each joint
- **Contact Sensing**: Detection of external forces and contacts

## Force/Torque Sensors

Force/Torque sensors provide critical information about physical interactions between the robot and its environment. These sensors are essential for tasks requiring precise contact control, such as assembly, manipulation, and human-robot interaction.

### Six-Axis Force/Torque Sensing

Force/Torque sensors typically measure forces in three directions (Fx, Fy, Fz) and torques around three axes (Tx, Ty, Tz), providing complete information about the interaction forces.

```python
#!/usr/bin/env python3
"""
File: sensor_fusion_example.py (Force/Torque section)
Purpose: Demonstrates force/torque sensor processing concepts
Chapter: 2 - Sensor Systems & Perception
Dependencies: numpy
Hardware: None (simulation)
"""

import numpy as np
import time
from dataclasses import dataclass
from typing import Tuple, Optional
import math

class ForceTorqueProcessor:
    """
    Processes force/torque sensor data for physical interaction understanding
    """

    def __init__(self):
        self.force_threshold = 5.0  # Newtons
        self.torque_threshold = 1.0  # Newton-meters
        self.contact_history = []

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

    def detect_contact(self, force_torque_data: np.ndarray) -> dict:
        """
        Detect contact and characterize the interaction
        """
        # Check if significant force is detected (indicating contact)
        force_magnitude = np.linalg.norm(force_torque_data[:3])
        torque_magnitude = np.linalg.norm(force_torque_data[3:])

        contact_detected = force_magnitude > self.force_threshold or torque_magnitude > self.torque_threshold

        contact_info = {
            'contact_detected': contact_detected,
            'force_magnitude': force_magnitude,
            'torque_magnitude': torque_magnitude,
            'forces': {
                'fx': force_torque_data[0],
                'fy': force_torque_data[1],
                'fz': force_torque_data[2]
            },
            'torques': {
                'tx': force_torque_data[3],
                'ty': force_torque_data[4],
                'tz': force_torque_data[5]
            }
        }

        return contact_info

    def process_interaction_demo(self, steps: int = 10):
        """
        Demonstrate force/torque processing for interaction understanding
        """
        print("Force/Torque Sensor Processing Demo")
        print("="*40)

        for step in range(steps):
            # Simulate force/torque data
            ft_data = self.simulate_force_torque_data()

            # Process the data
            contact_info = self.detect_contact(ft_data)

            print(f"\nStep {step + 1}:")
            print(f"  Force magnitude: {contact_info['force_magnitude']:.2f}N")
            print(f"  Torque magnitude: {contact_info['torque_magnitude']:.2f}Nm")

            contact_status = "CONTACT" if contact_info['contact_detected'] else "NO CONTACT"
            print(f"  Contact status: {contact_status}")

            if contact_info['contact_detected']:
                print(f"  Forces - Fx: {contact_info['forces']['fx']:.2f}N, "
                      f"Fy: {contact_info['forces']['fy']:.2f}N, "
                      f"Fz: {contact_info['forces']['fz']:.2f}N")
                print(f"  Torques - Tx: {contact_info['torques']['tx']:.2f}Nm, "
                      f"Ty: {contact_info['torques']['ty']:.2f}Nm, "
                      f"Tz: {contact_info['torques']['tz']:.2f}Nm")

# Example usage
ft_processor = ForceTorqueProcessor()
ft_processor.process_interaction_demo(steps=5)
```

For the complete implementation, see [sensor_fusion_example.py](/static/code/chapter-2/sensor_fusion_example.py).

### Applications of Force/Torque Sensing

Force/Torque sensors enable several critical robotic capabilities:

- **Assembly Operations**: Precise force control for inserting parts
- **Surface Following**: Maintaining consistent contact force
- **Grasping**: Detecting object contact and adjusting grip
- **Human-Robot Safety**: Limiting interaction forces for safe operation

## Sensor Fusion

The true power of Physical AI emerges when multiple sensor modalities are combined through sensor fusion. Each sensor type has strengths and limitations, but together they provide a comprehensive understanding of the robot's state and environment.

### Multi-Modal Integration Example

```python
#!/usr/bin/env python3
"""
File: sensor_fusion_example.py (Complete)
Purpose: Demonstrates complete sensor fusion system
Chapter: 2 - Sensor Systems & Perception
Dependencies: numpy
Hardware: None (simulation)
"""

import numpy as np
import time
from dataclasses import dataclass
from typing import Tuple, Optional
import math

class CompleteSensorFusionSystem:
    """
    Complete sensor fusion system integrating all sensor modalities
    """

    def __init__(self):
        self.sensor_data_history = []
        self.environment_map = {}  # Simulated environment map
        self.gravity = 9.81

    def simulate_all_sensors(self) -> dict:
        """
        Simulate data from all sensor types simultaneously
        """
        timestamp = time.time()

        # LIDAR simulation
        lidar_angles = np.linspace(0, 2*np.pi, 360)
        lidar_distances = np.full_like(lidar_angles, 10.0)
        for angle_idx in [45, 90, 180, 270]:
            if angle_idx < len(lidar_distances):
                lidar_distances[angle_idx] = 2.5
                if angle_idx > 0:
                    lidar_distances[angle_idx-1] = 2.6
                    lidar_distances[angle_idx+1] = 2.6

        # Camera simulation
        rgb_image = np.random.randint(0, 255, size=(480, 640, 3), dtype=np.uint8)
        center_y, center_x = 240, 320
        rgb_image[center_y-50:center_y+50, center_x-50:center_x+50] = [255, 0, 0]  # Red object
        depth_map = np.full((480, 640), 5.0, dtype=np.float32)
        depth_map[center_y-50:center_y+50, center_x-50:center_x+50] = 2.0  # Object at 2m

        # IMU simulation
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

        # Force/Torque simulation
        force_torque = np.array([
            np.random.normal(0, 0.5),    # Fx
            np.random.normal(0, 0.5),    # Fy
            np.random.normal(0, 1.0),    # Fz
            np.random.normal(0, 0.1),    # Tx
            np.random.normal(0, 0.1),    # Ty
            np.random.normal(0, 0.1)     # Tz
        ])

        return {
            'timestamp': timestamp,
            'lidar_distances': lidar_distances,
            'camera_rgb': rgb_image,
            'camera_depth': depth_map,
            'imu_orientation': orientation,
            'imu_angular_velocity': angular_velocity,
            'imu_linear_acceleration': linear_acceleration,
            'force_torque': force_torque
        }

    def process_fusion(self, sensor_data: dict) -> dict:
        """
        Process and fuse data from all sensors to create comprehensive understanding
        """
        fused_state = {}

        # Process LIDAR data
        min_distance_idx = np.argmin(sensor_data['lidar_distances'])
        fused_state['nearest_obstacle_distance'] = sensor_data['lidar_distances'][min_distance_idx]

        # Process camera data
        red_pixels = np.sum((sensor_data['camera_rgb'][:, :, 0] > 200) &
                           (sensor_data['camera_rgb'][:, :, 1] < 100) &
                           (sensor_data['camera_rgb'][:, :, 2] < 100))
        fused_state['red_objects_detected'] = red_pixels > 1000

        # Process IMU data
        roll_deg = math.degrees(sensor_data['imu_orientation'][0])
        pitch_deg = math.degrees(sensor_data['imu_orientation'][1])
        fused_state['tilt'] = {'roll': roll_deg, 'pitch': pitch_deg}

        # Process force/torque data
        force_magnitude = np.linalg.norm(sensor_data['force_torque'][:3])
        fused_state['contact_detected'] = force_magnitude > 2.0

        # Fused understanding
        fused_state['environment_confidence'] = 0.9  # High confidence when all sensors agree
        fused_state['navigation_safety'] = 'safe' if fused_state['nearest_obstacle_distance'] > 1.0 else 'caution'
        fused_state['manipulation_status'] = 'ready' if not fused_state['contact_detected'] else 'contact'

        return fused_state

    def run_complete_fusion_demo(self, steps: int = 10):
        """
        Run complete sensor fusion demonstration
        """
        print("Complete Sensor Fusion Demo")
        print("="*40)

        for step in range(steps):
            print(f"\nStep {step + 1}:")

            # Acquire all sensor data
            sensor_data = self.simulate_all_sensors()
            print(f"  Acquired data from all sensors at timestamp: {sensor_data['timestamp']:.2f}")

            # Process fusion
            fused_state = self.process_fusion(sensor_data)

            # Display fused information
            print(f"  Nearest obstacle: {fused_state['nearest_obstacle_distance']:.2f}m")
            print(f"  Red objects: {'DETECTED' if fused_state['red_objects_detected'] else 'NOT DETECTED'}")
            print(f"  Tilt - Roll: {fused_state['tilt']['roll']:.2f}°, Pitch: {fused_state['tilt']['pitch']:.2f}°")
            print(f"  Contact: {'YES' if fused_state['contact_detected'] else 'NO'}")
            print(f"  Navigation: {fused_state['navigation_safety']}")
            print(f"  Manipulation: {fused_state['manipulation_status']}")

            time.sleep(0.1)  # Simulate real-time acquisition interval

        print("\n" + "="*40)
        print("Complete Sensor Fusion Demo Finished")

# Example usage
fusion_system = CompleteSensorFusionSystem()
fusion_system.run_complete_fusion_demo(steps=5)

print("\nKey concepts demonstrated:")
print("1. Multi-modal sensing (LIDAR, camera, IMU, force/torque)")
print("2. Sensor data integration for comprehensive understanding")
print("3. Real-time processing of sensor streams")
print("4. State estimation from multiple sensor inputs")
print("5. Environmental perception through sensor fusion")
```

For the complete implementation, see [sensor_fusion_example.py](/static/code/chapter-2/sensor_fusion_example.py).

## Challenges in Sensor Systems

Physical AI sensor systems face several unique challenges:

### Noise and Uncertainty

Sensor data is inherently noisy and uncertain. Physical sensors are affected by environmental conditions, electromagnetic interference, and mechanical vibrations. Robust algorithms must account for this uncertainty in decision-making processes.

### Temporal Synchronization

Different sensors may operate at different frequencies and have varying latencies. Proper temporal synchronization is critical for accurate sensor fusion and state estimation.

### Calibration and Maintenance

Sensors require regular calibration to maintain accuracy. Physical sensors can drift over time due to temperature changes, mechanical wear, and other factors.

## Visualizing Sensor Concepts

To better understand the sensor systems discussed in this chapter, here are some visual representations:

### LIDAR Fundamentals
![LIDAR Fundamentals](/static/img/lidar-fundamentals.svg)
*This diagram illustrates how LIDAR sensors generate 360° distance measurements for mapping and navigation, with beams detecting surfaces in the environment.*

### RGB-D Camera Concept
![RGB-D Camera Concept](/static/img/rgbd-camera-concept.svg)
*This visualization shows how RGB-D cameras provide both color and depth information, enabling 3D reconstruction and object recognition.*

### IMU Concept
![IMU Concept](/static/img/imu-concept.svg)
*This diagram demonstrates how IMUs measure 3-axis acceleration, rotation, and magnetic field measurements for navigation and stabilization.*

### Force/Torque Sensor Concept
![Force/Torque Sensor Concept](/static/img/force-torque-sensor-concept.svg)
*This visualization shows how force/torque sensors measure 6-axis forces and torques, essential for precise manipulation and contact-based tasks.*

## Chapter Summary

This chapter introduced the fundamental sensor systems that enable Physical AI systems to perceive and interact with the physical world. We explored LIDAR for mapping and obstacle detection, RGB-D cameras for 3D scene understanding, IMUs for state estimation, and force/torque sensors for contact-aware manipulation.

The integration of multiple sensor modalities through sensor fusion provides robots with comprehensive environmental awareness and enables sophisticated behaviors. Each sensor type has unique strengths and limitations, but together they form the perceptual foundation for Physical AI systems.

In the next chapter, we will explore ROS 2 architecture and core concepts, learning how to build distributed robotic systems that integrate these sensor systems effectively.

## Lab Exercise 2.1: Sensor Data Collection & Visualization

### Objective
Collect and visualize data from simulated sensors to understand their characteristics and limitations.

### Requirements
- Python 3.10+ environment
- NumPy and Matplotlib installed
- Basic understanding of sensor concepts

### Steps
1. Run the sensor fusion example code and observe the output
2. Modify the simulation parameters to see how they affect sensor readings
3. Create visualizations of the different sensor data types
4. Analyze the noise characteristics in each sensor modality

### Expected Outcome
You should understand how different sensors provide complementary information and how their data can be fused to create a comprehensive understanding of the environment.

## Exercises and Review Questions

### Conceptual Questions
1. Explain the fundamental differences between LIDAR and RGB-D cameras in terms of their sensing principles and applications.
2. Describe how IMUs measure orientation, angular velocity, and linear acceleration.
3. What are the key advantages of force/torque sensors in robotic manipulation tasks?
4. Compare the advantages and disadvantages of different sensor modalities for obstacle detection.

### Application Questions
5. Design a sensor fusion approach that combines LIDAR, RGB-D camera, and IMU data for robot navigation in an indoor environment.
6. Explain how proprioception contributes to robot safety and control in physical interaction tasks.
7. Describe a scenario where all four sensor types (LIDAR, RGB-D, IMU, force/torque) would be necessary for a successful robotic task.

### Technical Problems
8. Calculate the distance to an object if a LIDAR sensor measures a time-of-flight of 10 nanoseconds for the laser pulse.
9. Given a 640x480 RGB-D camera with focal lengths fx=fy=320 and principal point cx=320, cy=240, convert a depth pixel at (320, 240) with depth value 2.5m to 3D coordinates in camera frame.
10. A robot arm is equipped with a 6-axis force/torque sensor. If the sensor measures [10, 5, 2, 0.5, 0.3, 0.1] in [N, N, N, Nm, Nm, Nm], explain what each value represents and what type of interaction this might indicate.

## Key Terms
- **Sensor Fusion**: Combining data from multiple sensors to improve perception accuracy
- **Proprioception**: Self-awareness of body position and movement
- **Exteroception**: Sensing the external environment
- **Point Cloud**: 3D representation of space using discrete points
- **Time-of-Flight**: Distance measurement based on signal travel time