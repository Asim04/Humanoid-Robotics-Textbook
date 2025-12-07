---
sidebar_position: 6
description: Learn about Gazebo Classic and Fortress simulation environments for robotics development
---

# Chapter 6: Gazebo Classic & Fortress

## Overview

Gazebo is a powerful 3D simulation environment that has been the cornerstone of robotics development for over a decade. This chapter covers both the traditional Gazebo Classic and the newer Ignition Gazebo (now called Fortress), focusing on their application in robotics research and development. You'll learn how to create realistic simulation environments, configure physics engines, and integrate with ROS 2 for comprehensive robot testing.

## Learning Objectives

By the end of this chapter, you will be able to:
- Set up and configure Gazebo Classic and Fortress environments
- Create custom world files and SDF models
- Configure physics engines (ODE, Bullet, Simbody)
- Integrate Gazebo with ROS 2 for sensor simulation and robot control
- Implement realistic sensor models and environmental conditions
- Debug common simulation issues and optimize performance

## Prerequisites

- Understanding of ROS 2 concepts (covered in Chapter 3-5)
- Basic knowledge of URDF robot modeling
- Familiarity with launch files and parameters

## 6.1 Introduction to Gazebo

Gazebo is a 3D dynamic simulator with the ability to accurately and efficiently simulate populations of robots in complex indoor and outdoor environments. It provides:
- High-fidelity physics simulation using ODE, Bullet, or Simbody
- High-quality graphics rendering with support for realistic lighting and shadows
- A library of common robot models and environments
- Integration with ROS and ROS 2 for robot control and sensor data

### Gazebo Classic vs. Ignition Gazebo (Fortress)

The robotics community has transitioned from the traditional Gazebo Classic to the newer Ignition Gazebo framework. Here's a comparison:

**Gazebo Classic:**
- Legacy system with mature plugin ecosystem
- Integrated with libgazebo and libsdformat
- Stable and well-documented
- Still widely used in existing projects

**Ignition Gazebo (Fortress):**
- Modern, modular architecture
- Better performance and scalability
- Improved plugin system with component-based entities
- Future-focused development path
- ROS 2 integration through ignition-ros2-bridge

## 6.2 Installing and Setting Up Gazebo

### Installing Gazebo Classic

For ROS 2 Humble on Ubuntu 22.04:

```bash
sudo apt update
sudo apt install gazebo libgazebo-dev
```

### Installing Ignition Fortress

For the newer Ignition Gazebo:

```bash
# Add the OSRF APT repository
sudo apt update && sudo apt install wget lsb-release gnupg
sudo sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list'
wget https://packages.osrfoundation.org/gazebo.key -O - | sudo apt-key add -
sudo apt update

# Install Ignition Fortress
sudo apt install ignition-fortress
```

## 6.3 World Building & SDF Format

### SDF (Simulation Description Format)

SDF is the XML-based format used to describe simulation environments in Gazebo. It defines:

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="my_world">
    <!-- Physics engine configuration -->
    <physics type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000.0</real_time_update_rate>
    </physics>

    <!-- Include models -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Define custom models -->
    <model name="my_robot">
      <!-- Model definition here -->
    </model>
  </world>
</sdf>
```

### World File Structure

A typical Gazebo world file includes:

1. **Physics Configuration**: Defines the physics engine and parameters
2. **Environment Models**: Ground plane, sky, sun, etc.
3. **Static Models**: Buildings, furniture, obstacles
4. **Dynamic Models**: Robots, movable objects
5. **Plugins**: Custom behavior and ROS 2 integration

## 6.4 Physics Engines

Gazebo supports multiple physics engines, each with different strengths:

### ODE (Open Dynamics Engine)
- Most mature and widely used
- Good for general-purpose simulation
- Supports complex joint types
- Configured as default in many systems

```xml
<physics type="ode">
  <max_step_size>0.001</max_step_size>
  <real_time_factor>1.0</real_time_factor>
  <real_time_update_rate>1000.0</real_time_update_rate>
  <ode>
    <solver>
      <type>quick</type>
      <iters>10</iters>
      <sor>1.3</sor>
    </solver>
    <constraints>
      <cfm>0.0</cfm>
      <erp>0.2</erp>
      <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
      <contact_surface_layer>0.001</contact_surface_layer>
    </constraints>
  </ode>
</physics>
```

### Bullet Physics
- Better for complex collision detection
- More stable for certain scenarios
- Supports more complex geometries

### Simbody
- Most accurate for biological simulations
- Good for complex multi-body dynamics
- More computationally expensive

## 6.5 Sensor Simulation

Gazebo provides realistic sensor simulation through plugins:

### Camera Sensors

```xml
<sensor name="camera" type="camera">
  <always_on>true</always_on>
  <update_rate>30.0</update_rate>
  <camera name="head">
    <horizontal_fov>1.047</horizontal_fov>
    <image>
      <width>640</width>
      <height>480</height>
      <format>R8G8B8</format>
    </image>
    <clip>
      <near>0.1</near>
      <far>100</far>
    </clip>
  </camera>
  <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
    <frame_name>camera_link</frame_name>
    <min_depth>0.1</min_depth>
    <max_depth>100.0</max_depth>
  </plugin>
</sensor>
```

### LiDAR Sensors

```xml
<sensor name="laser" type="ray">
  <always_on>true</always_on>
  <update_rate>40</update_rate>
  <ray>
    <scan>
      <horizontal>
        <samples>720</samples>
        <resolution>1</resolution>
        <min_angle>-1.570796</min_angle>
        <max_angle>1.570796</max_angle>
      </horizontal>
    </scan>
    <range>
      <min>0.10</min>
      <max>30.0</max>
      <resolution>0.01</resolution>
    </range>
  </ray>
  <plugin name="laser_controller" filename="libgazebo_ros_ray_sensor.so">
    <ros>
      <namespace>/laser</namespace>
      <remapping>~/out:=scan</remapping>
    </ros>
    <output_type>sensor_msgs/LaserScan</output_type>
  </plugin>
</sensor>
```

### IMU Sensors

```xml
<sensor name="imu" type="imu">
  <always_on>true</always_on>
  <update_rate>100</update_rate>
  <imu>
    <angular_velocity>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>2e-4</stddev>
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>2e-4</stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>2e-4</stddev>
        </noise>
      </z>
    </angular_velocity>
    <linear_acceleration>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>1.7e-2</stddev>
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>1.7e-2</stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>1.7e-2</stddev>
        </noise>
      </z>
    </linear_acceleration>
  </imu>
  <plugin name="imu_plugin" filename="libgazebo_ros_imu.so">
    <ros>
      <namespace>/imu</namespace>
      <remapping>~/out:=data</remapping>
    </ros>
    <frame_name>imu_link</frame_name>
  </plugin>
</sensor>
```

## 6.6 ROS 2 Integration

### Gazebo ROS Packages

The `gazebo_ros_pkgs` provide the bridge between Gazebo and ROS 2:

```bash
sudo apt install ros-humble-gazebo-ros-pkgs
```

### Launching Gazebo with ROS 2

```python
# launch/gazebo_simulation.launch.py
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Launch Gazebo with empty world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            ])
        ]),
        launch_arguments={
            'world': PathJoinSubstitution([
                FindPackageShare('my_robot_gazebo'),
                'worlds',
                'my_world.sdf'
            ])
        }.items()
    )

    return LaunchDescription([
        gazebo
    ])
```

### Spawning Robots in Gazebo

```python
# launch/spawn_robot.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Spawn robot in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'my_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5'
        ],
        output='screen'
    )

    return LaunchDescription([
        spawn_entity
    ])
```

## 6.7 Common Gazebo Plugins

### Differential Drive Controller

```xml
<plugin name="differential_drive_controller" filename="libgazebo_ros_diff_drive.so">
  <ros>
    <namespace>/my_robot</namespace>
    <remapping>cmd_vel:=cmd_vel</remapping>
    <remapping>odom:=odom</remapping>
  </ros>
  <update_rate>30</update_rate>
  <left_joint>left_wheel_joint</left_joint>
  <right_joint>right_wheel_joint</right_joint>
  <wheel_separation>0.3</wheel_separation>
  <wheel_diameter>0.1</wheel_diameter>
  <max_wheel_torque>20</max_wheel_torque>
  <max_wheel_acceleration>1.0</max_wheel_acceleration>
  <odometry_frame>odom</odometry_frame>
  <robot_base_frame>base_link</robot_base_frame>
  <publish_odom>true</publish_odom>
  <publish_odom_tf>true</publish_odom_tf>
  <publish_wheel_tf>true</publish_wheel_tf>
</plugin>
```

### Joint State Publisher

```xml
<plugin name="joint_state_publisher" filename="libgazebo_ros_joint_state_publisher.so">
  <ros>
    <namespace>/my_robot</namespace>
    <remapping>joint_states:=joint_states</remapping>
  </ros>
  <update_rate>30</update_rate>
  <joint_name>left_wheel_joint</joint_name>
  <joint_name>right_wheel_joint</joint_name>
</plugin>
```

## 6.8 Performance Optimization

### Simulation Parameters

```xml
<physics type="ode">
  <max_step_size>0.001</max_step_size>  <!-- Smaller for accuracy, larger for speed -->
  <real_time_factor>1.0</real_time_factor>  <!-- 1.0 for real-time -->
  <real_time_update_rate>1000.0</real_time_update_rate>  <!-- Hz -->
</physics>
```

### Model Optimization

- Use simple collision geometries when possible
- Reduce visual complexity for performance
- Limit update rates for sensors
- Use static models instead of dynamic when appropriate

## 6.9 Troubleshooting Common Issues

### Physics Instability
- **Issue**: Robot shakes or falls through surfaces
- **Solution**: Reduce step size, increase iterations, adjust ERP/CFM

### Sensor Noise
- **Issue**: Unrealistic sensor data
- **Solution**: Configure noise parameters appropriately

### Performance Issues
- **Issue**: Slow simulation
- **Solution**: Optimize world complexity, adjust physics parameters

## 6.10 Hands-On Practice

1. Create a simple world file with basic obstacles
2. Configure a robot model with differential drive
3. Add camera and LiDAR sensors to the robot
4. Launch the simulation and test robot control
5. Verify sensor data publication in ROS 2

## Review and Practice

### Questions
1. What are the key differences between Gazebo Classic and Ignition Gazebo?
2. How do you configure physics parameters for optimal simulation?
3. What are the essential plugins needed for ROS 2 integration?

### Exercises
1. Create a custom world file with multiple rooms and furniture
2. Configure a robot with realistic sensors for navigation tasks
3. Implement a simple navigation simulation with obstacle avoidance

## Further Learning

- Gazebo Tutorials: http://gazebosim.org/tutorials
- SDF Specification: http://sdformat.org/spec
- ROS 2 with Gazebo: https://classic.gazebosim.org/tutorials?tut=ros2_overview

## References

1. Koenig, N., & Howard, A. (2004). Design and use paradigms for Gazebo, an open-source multi-robot simulator. IEEE/RSJ International Conference on Intelligent Robots and Systems.
2. Open Source Robotics Foundation. (2021). Gazebo Documentation. Retrieved from http://gazebosim.org