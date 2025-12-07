---
sidebar_position: 2
---

# Gazebo Integration

## Introduction

Gazebo (now known as Ignition Gazebo) is one of the most popular simulation environments in the ROS ecosystem. It provides realistic physics simulation, high-quality graphics, and extensive sensor support. This guide covers how to integrate ROS 2 with Gazebo for robot simulation.

## Gazebo ROS Packages

The `gazebo_ros_pkgs` package provides the interface between ROS 2 and Gazebo. Key components include:

- **gazebo_ros**: Core ROS 2 plugins for Gazebo
- **gazebo_plugins**: Sensor and actuator plugins
- **gazebo_ros_control**: Integration with ros_control
- **gazebo_dev**: Development headers and libraries

## Setting Up a Gazebo Simulation

### 1. Robot URDF Configuration

For Gazebo simulation, your URDF needs additional Gazebo-specific tags:

```xml
<robot name="my_robot">
  <!-- Links and joints as usual -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.5 0.2"/>
      </geometry>
    </visual>
    <collision>
      <geometry>
        <box size="0.5 0.5 0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Gazebo-specific extensions -->
  <gazebo reference="base_link">
    <material>Gazebo/Blue</material>
    <mu1>0.2</mu1>
    <mu2>0.2</mu2>
  </gazebo>

  <!-- Sensors -->
  <gazebo>
    <plugin name="camera" filename="libgazebo_ros_camera.so">
      <frame_name>camera_frame</frame_name>
      <update_rate>30.0</update_rate>
    </plugin>
  </gazebo>
</robot>
```

### 2. Launch File for Gazebo Integration

Here's a complete launch file that starts Gazebo with a robot model:

```python
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    robot_name = LaunchConfiguration('robot_name', default='my_robot')
    world = LaunchConfiguration('world', default='empty.sdf')

    # Get the robot description parameter
    robot_description_path = os.path.join(
        FindPackageShare('my_robot_description').find('my_robot_description'),
        'urdf',
        'my_robot.urdf'
    )

    robot_description = {'robot_description': Command(['xacro ', robot_description_path])}

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': use_sim_time}]
    )

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('gazebo_ros'),
            'launch',
            'gazebo.launch.py'
        ]),
        launch_arguments={
            'world': world,
            'verbose': 'false',
        }.items()
    )

    # Spawn robot in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', robot_name,
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5'
        ],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true', description='Use simulation clock if true'),
        DeclareLaunchArgument('robot_name', default_value='my_robot', description='Name of the robot to spawn'),
        DeclareLaunchArgument('world', default_value='empty.sdf', description='Choose one of the world files from `/gazebo_ros/worlds`'),

        robot_state_publisher,
        gazebo,
        spawn_entity
    ])
```

## Common Gazebo Plugins

### 1. Differential Drive Controller

```xml
<gazebo>
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
  </plugin>
</gazebo>
```

### 2. IMU Sensor

```xml
<gazebo reference="imu_link">
  <sensor name="imu_sensor" type="imu">
    <always_on>true</always_on>
    <update_rate>100</update_rate>
    <visualize>true</visualize>
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
  </sensor>
</gazebo>
```

## Simulation Tips

1. **Physics Tuning**: Adjust physics parameters like step size and solver type for stability
2. **Realistic Sensors**: Add noise models and latency to match real sensors
3. **Performance**: Balance visual quality with simulation speed
4. **Debugging**: Use Gazebo's visualization tools to debug model issues
5. **Validation**: Compare simulation behavior with real robot when possible

## Running the Simulation

To run a Gazebo simulation with your robot:

```bash
# Terminal 1: Start the simulation
ros2 launch my_robot_gazebo my_robot_world.launch.py

# Terminal 2: Send commands to the robot
ros2 topic pub /my_robot/cmd_vel geometry_msgs/Twist '{linear: {x: 0.5}, angular: {z: 0.2}}'
```