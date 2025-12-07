# Unity Code Examples for Chapter 8: Unity for Robot Visualization

This directory contains Unity code examples that demonstrate how to integrate Unity with ROS2 for robot visualization and control. These examples show how to create a Unity-ROS2 bridge, visualize sensor data, animate robot models, and create UI dashboards.

## Files Included

### 1. unity_ros2_bridge.cs
A Unity C# script that establishes a connection between Unity and ROS2, allowing for bidirectional communication. It handles subscribing to ROS topics like `/odom`, `/scan`, and publishing to `/cmd_vel` for robot control.

**Key Features:**
- Connects to ROS bridge at specified IP and port
- Subscribes to odometry and laser scan topics
- Visualizes laser scan data in the Unity scene
- Sends velocity commands to control the robot

### 2. sensor_visualization.cs
A Unity C# script focused on visualizing various sensor data from ROS2, including LiDAR, IMU, and point cloud data.

**Key Features:**
- Visualizes laser scan points in 3D space
- Processes and displays IMU orientation data
- Handles point cloud visualization (with binary data parsing)
- Configurable visualization parameters

### 3. robot_animation_controller.cs
A Unity C# script that controls robot model animations based on ROS2 joint state messages.

**Key Features:**
- Maps ROS joint names to Unity transforms
- Supports different joint types (revolute, prismatic, continuous, fixed)
- Smooth interpolation for realistic joint movement
- Configurable joint limits and transformation axes

### 4. unity_ui_dashboard.cs
A Unity C# script that creates an in-scene UI dashboard to display robot status and sensor data.

**Key Features:**
- Displays position, velocity, and IMU data
- Shows battery level with color-coded visualization
- Provides emergency stop functionality
- Real-time updates of robot status

### 5. unity_ros2_setup.py
A Python script that sets up the ROS2 side of the Unity bridge, handling message routing and connection management.

**Key Features:**
- Establishes socket connection to Unity application
- Handles bidirectional message routing between ROS and Unity
- Processes odometry, sensor, and joint state messages
- Includes heartbeat and connection status monitoring

## Setup Instructions

### Prerequisites
- Unity 2021.3 LTS or later
- ROS2 (Humble Hawksbill recommended)
- Unity-Robotics-Hub package
- rosbridge_suite

### Installation Steps

1. **Install Unity-Robotics-Hub:**
   ```bash
   # Clone the Unity Robotics Hub
   git clone https://github.com/Unity-Technologies/Unity-Robotics-Hub.git
   ```

2. **Set up ROS2 environment:**
   ```bash
   source /opt/ros/humble/setup.bash
   source install/setup.bash  # If you built ROS2 packages from source
   ```

3. **Launch ROS bridge:**
   ```bash
   ros2 launch rosbridge_server rosbridge_websocket_launch.xml
   ```

4. **In Unity:**
   - Import the Unity-Robotics-Hub packages
   - Add the scripts to your Unity project
   - Configure the IP address and port in the Unity scripts
   - Set up the robot model hierarchy with appropriate joint transforms

5. **Run the simulation:**
   - Start your ROS2 nodes
   - Launch Unity scene with the bridge scripts
   - Verify connection and data flow

## Usage Examples

### Basic Robot Control
1. Attach `UnityROS2Bridge.cs` to a GameObject in your scene
2. Assign your robot model to the robotModel field
3. Configure the ROS connection parameters
4. Run the Unity scene and ROS nodes
5. The robot should respond to velocity commands and publish its state

### Sensor Visualization
1. Attach `SensorVisualization.cs` to a GameObject
2. Optionally assign a prefab for laser point visualization
3. Configure the sensor topics to match your robot
4. Run to see real-time sensor data visualization

### UI Dashboard
1. Create a Canvas in your Unity scene
2. Add UI elements (TextMeshPro, Sliders, etc.) and assign to the script
3. Attach `UnityUIDashboard.cs` to a GameObject
4. Configure the ROS topics to match your system
5. Run to see real-time robot status information

## Important Notes

- Unity uses a different coordinate system than ROS (Y-up vs Z-up), so transformations may need adjustment
- Network latency can affect real-time performance, consider this in your application design
- For large point clouds, consider downsampling for better performance in Unity
- The Unity-Robotics-Hub provides additional examples and documentation for more advanced features

## Troubleshooting

- **Connection Issues:** Verify IP addresses and ports match between Unity and ROS
- **Performance Issues:** Reduce the update rate of visualizations or downsample sensor data
- **Coordinate System Issues:** Check that position and rotation conversions account for coordinate system differences
- **Missing Messages:** Ensure topic names match exactly between Unity and ROS nodes