---
sidebar_position: 6
---

# Lab 6: Simulating a Robot in Gazebo

## Objective

In this lab, you will learn how to create a complete simulation environment in Gazebo, including a custom robot model, sensors, and a realistic world. You'll integrate the simulation with ROS 2 and implement basic robot control and sensor processing.

## Learning Outcomes

By the end of this lab, you will be able to:
- Create and configure a robot model for Gazebo simulation
- Set up a Gazebo world with realistic physics and lighting
- Integrate ROS 2 with Gazebo for robot control and sensor data
- Implement basic robot navigation and obstacle avoidance
- Debug common simulation issues and optimize performance

## Prerequisites

- Completion of Chapter 6: Gazebo Classic & Fortress
- Understanding of ROS 2 concepts (Chapters 3-5)
- Basic knowledge of URDF robot modeling
- Familiarity with launch files and parameters

## Equipment and Software

- Ubuntu 22.04 LTS
- ROS 2 Humble Hawksbill
- Gazebo Classic or Ignition Fortress
- Basic text editor or IDE

## Lab Duration

Estimated completion time: 3-4 hours

## 6.1 Setting Up the Workspace

### 6.1.1 Create the Simulation Package

First, create a new ROS 2 package for your simulation:

```bash
# Navigate to your ROS 2 workspace
cd ~/ros2_ws/src

# Create the simulation package
ros2 pkg create --build-type ament_cmake my_robot_gazebo --dependencies gazebo_ros_pkgs gazebo_plugins robot_state_publisher joint_state_publisher

# Navigate to the package directory
cd my_robot_gazebo
```

### 6.1.2 Create Directory Structure

Create the necessary directories for your simulation:

```bash
mkdir -p models worlds launch config
mkdir -p models/my_robot/meshes
mkdir -p models/my_robot/materials/textures
mkdir -p models/my_robot/materials/scripts
```

## 6.2 Creating the Robot Model

### 6.2.1 Create the URDF Model

Create a URDF file for your robot in `models/my_robot/urdf/my_robot.urdf`:

```xml
<?xml version="1.0"?>
<robot name="my_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Base Link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.3 0.15"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 0.8"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.5 0.3 0.15"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Left Wheel -->
  <link name="left_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.002"/>
    </inertial>
  </link>

  <!-- Right Wheel -->
  <link name="right_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.002"/>
    </inertial>
  </link>

  <!-- Camera -->
  <link name="camera_link">
    <visual>
      <geometry>
        <box size="0.05 0.05 0.05"/>
      </geometry>
      <material name="red">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.05 0.05 0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.1"/>
      <inertia ixx="0.0001" ixy="0.0" ixz="0.0" iyy="0.0001" iyz="0.0" izz="0.0001"/>
    </inertial>
  </link>

  <!-- Joints -->
  <joint name="base_to_left_wheel" type="continuous">
    <parent link="base_link"/>
    <child link="left_wheel"/>
    <origin xyz="0 0.2 -0.05" rpy="1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <joint name="base_to_right_wheel" type="continuous">
    <parent link="base_link"/>
    <child link="right_wheel"/>
    <origin xyz="0 -0.2 -0.05" rpy="1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <joint name="base_to_camera" type="fixed">
    <parent link="base_link"/>
    <child link="camera_link"/>
    <origin xyz="0.2 0 0.1"/>
  </joint>

  <!-- Gazebo Plugins -->
  <gazebo reference="base_link">
    <material>Gazebo/Blue</material>
  </gazebo>

  <gazebo reference="left_wheel">
    <material>Gazebo/Black</material>
    <mu1>1.0</mu1>
    <mu2>1.0</mu2>
    <kp>1000000.0</kp>
    <kd>100.0</kd>
  </gazebo>

  <gazebo reference="right_wheel">
    <material>Gazebo/Black</material>
    <mu1>1.0</mu1>
    <mu2>1.0</mu2>
    <kp>1000000.0</kp>
    <kd>100.0</kd>
  </gazebo>

  <gazebo reference="camera_link">
    <material>Gazebo/Red</material>
  </gazebo>

  <!-- Differential Drive Plugin -->
  <gazebo>
    <plugin name="differential_drive_controller" filename="libgazebo_ros_diff_drive.so">
      <ros>
        <namespace>/my_robot</namespace>
        <remapping>cmd_vel:=cmd_vel</remapping>
        <remapping>odom:=odom</remapping>
      </ros>
      <update_rate>30</update_rate>
      <left_joint>base_to_left_wheel</left_joint>
      <right_joint>base_to_right_wheel</right_joint>
      <wheel_separation>0.4</wheel_separation>
      <wheel_diameter>0.2</wheel_diameter>
      <max_wheel_torque>20</max_wheel_torque>
      <max_wheel_acceleration>1.0</max_wheel_acceleration>
      <command_topic>cmd_vel</command_topic>
      <odometry_topic>odom</odometry_topic>
      <odometry_frame>odom</odometry_frame>
      <robot_base_frame>base_link</robot_base_frame>
      <publish_odom>true</publish_odom>
      <publish_odom_tf>true</publish_odom_tf>
      <publish_wheel_tf>true</publish_wheel_tf>
    </plugin>
  </gazebo>

  <!-- Camera Plugin -->
  <gazebo reference="camera_link">
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
        <ros>
          <namespace>/my_robot</namespace>
          <remapping>~/image_raw:=image_raw</remapping>
          <remapping>~/camera_info:=camera_info</remapping>
        </ros>
        <frame_name>camera_link</frame_name>
      </plugin>
    </sensor>
  </gazebo>

</robot>
```

### 6.2.2 Create a Simplified Xacro Version

Create `models/my_robot/urdf/my_robot.xacro`:

```xml
<?xml version="1.0"?>
<robot name="my_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Properties -->
  <xacro:property name="base_width" value="0.5"/>
  <xacro:property name="base_length" value="0.3"/>
  <xacro:property name="base_height" value="0.15"/>
  <xacro:property name="wheel_radius" value="0.1"/>
  <xacro:property name="wheel_width" value="0.05"/>
  <xacro:property name="wheel_y_offset" value="0.2"/>
  <xacro:property name="camera_size" value="0.05"/>

  <!-- Base Link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="${base_width} ${base_length} ${base_height}"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 0.8"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="${base_width} ${base_length} ${base_height}"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Macro for wheels -->
  <xacro:macro name="wheel" params="prefix reflect">
    <link name="${prefix}_wheel">
      <visual>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_width}"/>
        </geometry>
        <material name="black">
          <color rgba="0 0 0 1"/>
        </material>
      </visual>
      <collision>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_width}"/>
        </geometry>
      </collision>
      <inertial>
        <mass value="0.5"/>
        <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.002"/>
      </inertial>
    </link>

    <joint name="base_to_${prefix}_wheel" type="continuous">
      <parent link="base_link"/>
      <child link="${prefix}_wheel"/>
      <origin xyz="0 ${reflect * wheel_y_offset} -${wheel_radius}" rpy="1.5708 0 0"/>
      <axis xyz="0 0 1"/>
    </joint>

    <gazebo reference="${prefix}_wheel">
      <material>Gazebo/Black</material>
      <mu1>1.0</mu1>
      <mu2>1.0</mu2>
      <kp>1000000.0</kp>
      <kd>100.0</kd>
    </gazebo>
  </xacro:macro>

  <!-- Instantiate wheels -->
  <xacro:wheel prefix="left" reflect="1"/>
  <xacro:wheel prefix="right" reflect="-1"/>

  <!-- Camera -->
  <link name="camera_link">
    <visual>
      <geometry>
        <box size="${camera_size} ${camera_size} ${camera_size}"/>
      </geometry>
      <material name="red">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="${camera_size} ${camera_size} ${camera_size}"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.1"/>
      <inertia ixx="0.0001" ixy="0.0" ixz="0.0" iyy="0.0001" iyz="0.0" izz="0.0001"/>
    </inertial>
  </link>

  <joint name="base_to_camera" type="fixed">
    <parent link="base_link"/>
    <child link="camera_link"/>
    <origin xyz="${base_width/2} 0 ${base_height/2}"/>
  </joint>

  <!-- Gazebo Materials -->
  <gazebo reference="base_link">
    <material>Gazebo/Blue</material>
  </gazebo>

  <gazebo reference="camera_link">
    <material>Gazebo/Red</material>
  </gazebo>

  <!-- Differential Drive Plugin -->
  <gazebo>
    <plugin name="differential_drive_controller" filename="libgazebo_ros_diff_drive.so">
      <ros>
        <namespace>/my_robot</namespace>
        <remapping>cmd_vel:=cmd_vel</remapping>
        <remapping>odom:=odom</remapping>
      </ros>
      <update_rate>30</update_rate>
      <left_joint>base_to_left_wheel</left_joint>
      <right_joint>base_to_right_wheel</right_joint>
      <wheel_separation>${2 * wheel_y_offset}</wheel_separation>
      <wheel_diameter>${2 * wheel_radius}</wheel_diameter>
      <max_wheel_torque>20</max_wheel_torque>
      <max_wheel_acceleration>1.0</max_wheel_acceleration>
      <command_topic>cmd_vel</command_topic>
      <odometry_topic>odom</odometry_topic>
      <odometry_frame>odom</odometry_frame>
      <robot_base_frame>base_link</robot_base_frame>
      <publish_odom>true</publish_odom>
      <publish_odom_tf>true</publish_odom_tf>
      <publish_wheel_tf>true</publish_wheel_tf>
    </plugin>
  </gazebo>

  <!-- Camera Plugin -->
  <gazebo reference="camera_link">
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
        <ros>
          <namespace>/my_robot</namespace>
          <remapping>~/image_raw:=image_raw</remapping>
          <remapping>~/camera_info:=camera_info</remapping>
        </ros>
        <frame_name>camera_link</frame_name>
      </plugin>
    </sensor>
  </gazebo>

</robot>
```

## 6.3 Creating the World File

Create `worlds/simple_room.world`:

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="simple_room">
    <!-- Physics Engine -->
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

    <!-- Environment -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Room walls -->
    <model name="wall_1">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>10 0.2 2</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>10 0.2 2</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.1 0.1 0.1 1</specular>
          </material>
        </visual>
      </link>
      <pose>-5 0 1 0 0 0</pose>
    </model>

    <model name="wall_2">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>10 0.2 2</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>10 0.2 2</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.1 0.1 0.1 1</specular>
          </material>
        </visual>
      </link>
      <pose>5 0 1 0 0 0</pose>
    </model>

    <model name="wall_3">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.2 10 2</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.2 10 2</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.1 0.1 0.1 1</specular>
          </material>
        </visual>
      </link>
      <pose>0 -5 1 0 0 0</pose>
    </model>

    <model name="wall_4">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.2 10 2</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.2 10 2</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.1 0.1 0.1 1</specular>
          </material>
        </visual>
      </link>
      <pose>0 5 1 0 0 0</pose>
    </model>

    <!-- Obstacles -->
    <model name="obstacle_1">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.5 0.5 0.5</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.5 0.5 0.5</size>
            </box>
          </geometry>
          <material>
            <ambient>0.2 0.8 0.2 1</ambient>
            <diffuse>0.2 0.8 0.2 1</diffuse>
            <specular>0.1 0.1 0.1 1</specular>
          </material>
        </visual>
      </link>
      <pose>2 2 0.25 0 0 0</pose>
    </model>

    <model name="obstacle_2">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <cylinder>
              <radius>0.3</radius>
              <length>1.0</length>
            </cylinder>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>0.3</radius>
              <length>1.0</length>
            </cylinder>
          </geometry>
          <material>
            <ambient>0.8 0.2 0.2 1</ambient>
            <diffuse>0.8 0.2 0.2 1</diffuse>
            <specular>0.1 0.1 0.1 1</specular>
          </material>
        </visual>
      </link>
      <pose>-2 -2 0.5 0 0 0</pose>
    </model>

  </world>
</sdf>
```

## 6.4 Creating Launch Files

Create `launch/my_robot_world.launch.py`:

```python
import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world = LaunchConfiguration('world', default='simple_room.world')

    # Get the package share directory
    pkg_share = FindPackageShare('my_robot_gazebo').find('my_robot_gazebo')

    # Launch Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            ])
        ]),
        launch_arguments={
            'world': PathJoinSubstitution([pkg_share, 'worlds', world]),
            'verbose': 'false',
        }.items()
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'robot_description': open(
                PathJoinSubstitution([pkg_share, 'models', 'my_robot', 'urdf', 'my_robot.xacro'])
            ).read()}
        ]
    )

    # Joint State Publisher
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # Spawn robot in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'my_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            'world',
            default_value='simple_room.world',
            description='Choose one of the world files from `/my_robot_gazebo/worlds`'
        ),
        gazebo,
        robot_state_publisher,
        joint_state_publisher,
        spawn_entity
    ])
```

## 6.5 Creating a Simple Controller Node

Create `my_robot_gazebo/simple_controller.py`:

```python
#!/usr/bin/env python3
"""
File: simple_controller.py
Purpose: Simple controller for the simulated robot in Gazebo
Chapter: 6 - Gazebo Classic & Fortress
Dependencies: rclpy, geometry_msgs, sensor_msgs
Hardware: Simulated robot in Gazebo
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32
import math


class SimpleController(Node):
    """
    A simple controller that moves the robot forward and turns when obstacles are detected.
    """

    def __init__(self):
        super().__init__('simple_controller')

        # Create publisher for velocity commands
        self.cmd_vel_pub = self.create_publisher(Twist, '/my_robot/cmd_vel', 10)

        # Create subscriber for laser scan data
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/my_robot/scan',
            self.scan_callback,
            10
        )

        # Timer for control loop
        self.timer = self.create_timer(0.1, self.control_loop)

        # Control parameters
        self.linear_speed = 0.5  # m/s
        self.angular_speed = 0.5  # rad/s
        self.min_distance = 0.5  # minimum distance to obstacles (m)
        self.obstacle_detected = False

        self.get_logger().info('Simple controller initialized')

    def scan_callback(self, msg):
        """Process laser scan data to detect obstacles."""
        # Get the front-facing range (around 0 degrees)
        if len(msg.ranges) > 0:
            # Get ranges from -30 to +30 degrees (front of robot)
            front_ranges = []
            for i in range(len(msg.ranges)):
                angle = msg.angle_min + i * msg.angle_increment
                if -math.pi/6 <= angle <= math.pi/6:  # -30 to +30 degrees
                    if msg.ranges[i] > msg.range_min and msg.ranges[i] < msg.range_max:
                        front_ranges.append(msg.ranges[i])

            if front_ranges:
                min_front_distance = min(front_ranges)
                self.obstacle_detected = min_front_distance < self.min_distance
                self.get_logger().debug(f'Min front distance: {min_front_distance:.2f}m, Obstacle: {self.obstacle_detected}')
            else:
                self.obstacle_detected = False

    def control_loop(self):
        """Main control loop."""
        cmd_vel = Twist()

        if self.obstacle_detected:
            # Turn in place to avoid obstacle
            cmd_vel.linear.x = 0.0
            cmd_vel.angular.z = self.angular_speed
            self.get_logger().info('Obstacle detected! Turning...')
        else:
            # Move forward
            cmd_vel.linear.x = self.linear_speed
            cmd_vel.angular.z = 0.0
            self.get_logger().info('Clear path, moving forward...')

        # Publish the command
        self.cmd_vel_pub.publish(cmd_vel)


def main(args=None):
    rclpy.init(args=args)

    controller = SimpleController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## 6.6 Running the Simulation

### 6.6.1 Build and Source the Package

```bash
# Navigate to your workspace
cd ~/ros2_ws

# Build the package
colcon build --packages-select my_robot_gazebo

# Source the workspace
source install/setup.bash
```

### 6.6.2 Launch the Simulation

```bash
# Launch the robot in Gazebo
ros2 launch my_robot_gazebo my_robot_world.launch.py
```

In another terminal, run the controller:

```bash
# Run the simple controller
ros2 run my_robot_gazebo simple_controller.py
```

### 6.6.3 Test the Simulation

1. Open RViz2 in another terminal:
```bash
# Set the ROS_DOMAIN_ID to match your simulation
export ROS_DOMAIN_ID=0
rviz2
```

2. Add displays for:
   - Robot model (RobotModel)
   - Laser scan (LaserScan) - topic: `/my_robot/scan`
   - Odometry (Odometry) - topic: `/my_robot/odom`

3. You can also manually control the robot:
```bash
# Send velocity commands manually
ros2 topic pub /my_robot/cmd_vel geometry_msgs/Twist '{linear: {x: 0.5}, angular: {z: 0.2}}'
```

## 6.7 Advanced Features

### 6.7.1 Adding a LiDAR Sensor

To add a LiDAR sensor to your robot, add this to your URDF/Xacro file:

```xml
<!-- LiDAR Link -->
<link name="lidar_link">
  <visual>
    <geometry>
      <cylinder radius="0.05" length="0.05"/>
    </geometry>
    <material name="silver">
      <color rgba="0.7 0.7 0.7 1"/>
    </material>
  </visual>
  <collision>
    <geometry>
      <cylinder radius="0.05" length="0.05"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="0.1"/>
    <inertia ixx="0.0001" ixy="0.0" ixz="0.0" iyy="0.0001" iyz="0.0" izz="0.0001"/>
  </inertial>
</link>

<joint name="base_to_lidar" type="fixed">
  <parent link="base_link"/>
  <child link="lidar_link"/>
  <origin xyz="0.1 0 0.1"/>
</joint>

<gazebo reference="lidar_link">
  <sensor name="lidar" type="ray">
    <always_on>true</always_on>
    <update_rate>40</update_rate>
    <ray>
      <scan>
        <horizontal>
          <samples>720</samples>
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.10</min>
        <max>30.0</max>
        <resolution>0.01</resolution>
      </range>
    </ray>
    <plugin name="lidar_controller" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <namespace>/my_robot</namespace>
        <remapping>~/out:=scan</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
    </plugin>
  </sensor>
</gazebo>
```

### 6.7.2 Creating a More Complex World

Create `worlds/maze.world` with a maze environment:

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="maze">
    <!-- Physics Engine -->
    <physics type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000.0</real_time_update_rate>
    </physics>

    <!-- Environment -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Maze walls -->
    <!-- Outer walls -->
    <model name="outer_wall_north">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>20 0.2 1</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>20 0.2 1</size></box>
          </geometry>
        </visual>
      </link>
      <pose>0 10 0.5 0 0 0</pose>
    </model>

    <model name="outer_wall_south">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>20 0.2 1</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>20 0.2 1</size></box>
          </geometry>
        </visual>
      </link>
      <pose>0 -10 0.5 0 0 0</pose>
    </model>

    <model name="outer_wall_east">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>0.2 20 1</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>0.2 20 1</size></box>
          </geometry>
        </visual>
      </link>
      <pose>10 0 0.5 0 0 0</pose>
    </model>

    <model name="outer_wall_west">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>0.2 20 1</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>0.2 20 1</size></box>
          </geometry>
        </visual>
      </link>
      <pose>-10 0 0.5 0 0 0</pose>
    </model>

    <!-- Inner maze walls -->
    <model name="maze_wall_1">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>0.2 8 1</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>0.2 8 1</size></box>
          </geometry>
        </visual>
      </link>
      <pose>5 0 0.5 0 0 0</pose>
    </model>

    <model name="maze_wall_2">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>6 0.2 1</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>6 0.2 1</size></box>
          </geometry>
        </visual>
      </link>
      <pose>0 5 0.5 0 0 0</pose>
    </model>

    <!-- Goal area -->
    <model name="goal">
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry>
            <box><size>1 1 0.1</size></box>
          </geometry>
          <material>
            <ambient>0 1 0 0.5</ambient>
            <diffuse>0 1 0 0.5</diffuse>
          </material>
        </visual>
      </link>
      <pose>8 8 0.05 0 0 0</pose>
    </model>

  </world>
</sdf>
```

## 6.8 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Robot falls through the ground
- **Cause**: Incorrect inertia parameters or physics settings
- **Solution**: Verify mass and inertia values in URDF, adjust physics parameters in world file

#### Issue 2: Robot doesn't respond to commands
- **Cause**: Plugin not loaded or namespace mismatch
- **Solution**: Check Gazebo console for plugin errors, verify namespace in launch files

#### Issue 3: Sensor data not published
- **Cause**: Sensor plugin not configured correctly
- **Solution**: Check sensor configuration in URDF, verify topic names

#### Issue 4: Performance issues
- **Cause**: Complex models or high update rates
- **Solution**: Simplify collision geometries, reduce update rates, optimize physics parameters

## 6.9 Lab Assignment

### Task 1: Navigation Challenge
Modify the simple controller to implement a more sophisticated navigation algorithm:
1. Use the LiDAR data to implement a wall-following algorithm
2. Add goal-seeking behavior to navigate to a specific location
3. Implement obstacle avoidance that doesn't just turn in place

### Task 2: World Extension
Create a new world file with:
1. Multiple rooms connected by doorways
2. Moving obstacles (using Gazebo's built-in models)
3. Different surface types with varying friction coefficients

### Task 3: Sensor Fusion
Add multiple sensors to your robot and implement:
1. An IMU sensor
2. A depth camera
3. A simple sensor fusion algorithm that combines data from different sensors

## 6.10 Summary

In this lab, you've learned how to:
- Create a complete robot model with appropriate physics properties
- Set up a Gazebo simulation environment with custom world files
- Integrate ROS 2 with Gazebo for robot control and sensor processing
- Implement basic robot behaviors in simulation
- Troubleshoot common simulation issues

This foundation will serve you well as you advance to more complex simulation scenarios in later chapters.

## Review Questions

1. What are the key components needed to create a robot model for Gazebo simulation?
2. How do Gazebo plugins enable communication with ROS 2?
3. What are the differences between visual and collision geometries in URDF?
4. How can you optimize simulation performance for complex environments?
5. What are the advantages of using Xacro over plain URDF for robot modeling?

## Further Exploration

- Experiment with different physics engines (ODE, Bullet, Simbody)
- Implement more sophisticated control algorithms (PID controllers, path planning)
- Explore Gazebo's built-in models and environments
- Investigate advanced sensor modeling and noise characteristics