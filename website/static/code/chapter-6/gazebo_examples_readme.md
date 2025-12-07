# Gazebo World Files and SDF Examples

This directory contains Gazebo world files and SDF (Simulation Description Format) examples for Chapter 6 of the Physical AI & Humanoid Robotics textbook. These examples demonstrate how to create simulation environments, robot models, and sensor configurations in Gazebo.

## Files Included

### 1. basic_world.world
A simple Gazebo world file that includes:
- Ground plane and sun lighting
- Basic obstacles (box and cylinder)
- A simple differential drive robot model
- Physics engine configuration

### 2. complex_world.world
A more advanced Gazebo world file that includes:
- Multiple buildings and maze-like structures
- Two different colored robots
- A LiDAR sensor model
- Environmental effects plugin
- More complex physics configuration

### 3. robot_model.sdf
An SDF file defining a differential drive robot model with:
- Base link with proper inertial properties
- Left and right wheels with continuous joints
- Caster wheel for stability
- IMU, LiDAR, and camera sensors
- ROS2 integration plugins for control and communication

### 4. model.config
A configuration file for the robot model that includes metadata such as:
- Model name and version
- Author information
- Description of the model
- Dependencies

### 5. gazebo_launch.py
A ROS2 launch file that demonstrates how to:
- Launch Gazebo with a custom world
- Spawn the robot model in the simulation
- Configure robot state publisher
- Set up robot controllers

## Usage Instructions

### Setting up the Gazebo Environment

1. **Install Gazebo** (Classic or Fortress):
   ```bash
   # For Ubuntu with ROS2 Humble
   sudo apt update
   sudo apt install gazebo libgazebo-dev
   sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros-control
   ```

2. **Create a Gazebo models directory**:
   ```bash
   mkdir -p ~/.gazebo/models/differential_drive_robot
   ```

3. **Copy the robot model files**:
   ```bash
   cp robot_model.sdf ~/.gazebo/models/differential_drive_robot/
   cp model.config ~/.gazebo/models/differential_drive_robot/
   ```

### Running the Examples

1. **Launch Gazebo with a basic world**:
   ```bash
   gazebo basic_world.world
   ```

2. **Launch Gazebo with a complex world**:
   ```bash
   gazebo complex_world.world
   ```

3. **Use the ROS2 launch file**:
   ```bash
   ros2 launch gazebo_launch.py
   ```

### Customizing World Files

World files use the SDF (Simulation Description Format) to define the simulation environment. Key components include:

- **Models**: Physical objects in the simulation (robots, obstacles, etc.)
- **Lights**: Lighting sources (sun, directional, point lights)
- **Physics**: Physics engine configuration (ODE, Bullet, Simbody)
- **Plugins**: Additional functionality (controllers, sensors, custom logic)

### Creating Custom Models

SDF (Simulation Description Format) files define individual models with:

- **Links**: Rigid bodies with mass, geometry, and inertial properties
- **Joints**: Connections between links (revolute, prismatic, fixed, etc.)
- **Sensors**: Perception capabilities (cameras, LiDAR, IMU, etc.)
- **Plugins**: Additional functionality for ROS2 integration

## Advanced Features Demonstrated

### Physics Configuration
- Custom physics parameters for realistic simulation
- Solver settings for stability and performance
- Constraint parameters for contact behavior

### Sensor Integration
- LiDAR sensors for obstacle detection
- IMU sensors for orientation and acceleration
- Camera sensors for visual perception
- Proper noise models for realistic sensor data

### ROS2 Integration
- Diff drive controller plugin
- Sensor data publishing to ROS topics
- Coordinate frame management
- Real-time control capabilities

## Troubleshooting

- **Model not appearing**: Ensure the model directory is in `~/.gazebo/models/` or use `GAZEBO_MODEL_PATH`
- **Physics instability**: Adjust physics parameters in the world file (step size, solver iterations)
- **Sensor data not publishing**: Check plugin configurations and ROS topic names
- **Performance issues**: Reduce the number of objects or lower the update rates

## Best Practices

1. **Use proper inertial properties** for stable physics simulation
2. **Set appropriate collision and visual geometries** for performance
3. **Configure sensors with realistic noise parameters** for robust algorithm development
4. **Use fixed joints instead of complex link hierarchies** when possible
5. **Test with different physics engines** to ensure robustness