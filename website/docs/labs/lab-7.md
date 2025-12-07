---
sidebar_position: 7
---

# Lab 7: Complex Environment Simulation

## Objective

In this lab, you will learn to create and simulate complex environments with multiple robots, dynamic obstacles, realistic physics, and environmental conditions. You'll implement advanced simulation techniques including contact forces, sensor noise modeling, and performance optimization for large-scale scenarios.

## Learning Outcomes

By the end of this lab, you will be able to:
- Create complex multi-robot environments with realistic physics
- Implement dynamic obstacles and environmental conditions
- Model sensor noise and environmental disturbances
- Optimize simulation performance for complex scenarios
- Validate simulation results against real-world expectations
- Debug complex simulation issues

## Prerequisites

- Completion of Lab 6: Simulating a Robot in Gazebo
- Understanding of Chapter 7: Advanced Simulation Techniques
- Knowledge of ROS 2 multi-robot systems
- Experience with URDF/Xacro modeling

## Equipment and Software

- Ubuntu 22.04 LTS
- ROS 2 Humble Hawksbill
- Gazebo Classic or Ignition Fortress
- Python 3.10+
- Basic text editor or IDE

## Lab Duration

Estimated completion time: 4-5 hours

## 7.1 Setting Up Complex Multi-Robot Simulation

### 7.1.1 Create the Multi-Robot Package

First, create a new ROS 2 package for your complex simulation:

```bash
# Navigate to your ROS 2 workspace
cd ~/ros2_ws/src

# Create the multi-robot simulation package
ros2 pkg create --build-type ament_python complex_env_sim --dependencies rclpy geometry_msgs sensor_msgs std_msgs gazebo_ros_pkgs gazebo_plugins robot_state_publisher joint_state_publisher

# Navigate to the package directory
cd complex_env_sim
```

### 7.1.2 Create Directory Structure

Create the necessary directories for your complex simulation:

```bash
mkdir -p models robots worlds launch config scripts
mkdir -p models/simple_robot/meshes
mkdir -p worlds/complex
mkdir -p scripts/controllers
```

## 7.2 Creating Multiple Robot Models

### 7.2.1 Create a Simple Robot Model (Xacro)

Create `models/simple_robot/urdf/simple_robot.xacro`:

```xml
<?xml version="1.0"?>
<robot name="simple_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Robot properties -->
  <xacro:property name="wheel_radius" value="0.1"/>
  <xacro:property name="wheel_width" value="0.05"/>
  <xacro:property name="base_width" value="0.3"/>
  <xacro:property name="base_length" value="0.4"/>
  <xacro:property name="base_height" value="0.15"/>
  <xacro:property name="wheel_y_offset" value="0.15"/>

  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="${base_length} ${base_width} ${base_height}"/>
      </geometry>
      <material name="light_blue">
        <color rgba="0.5 0.7 1.0 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="${base_length} ${base_width} ${base_height}"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="2.0"/>
      <inertia ixx="0.05" ixy="0.0" ixz="0.0" iyy="0.05" iyz="0.0" izz="0.05"/>
    </inertial>
  </link>

  <!-- Macro for wheels -->
  <xacro:macro name="simple_wheel" params="prefix reflect">
    <link name="${prefix}_wheel">
      <visual>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_width}"/>
        </geometry>
        <material name="black">
          <color rgba="0.1 0.1 0.1 1.0"/>
        </material>
      </visual>
      <collision>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_width}"/>
        </geometry>
      </collision>
      <inertial>
        <mass value="0.2"/>
        <inertia ixx="0.0005" ixy="0.0" ixz="0.0" iyy="0.0005" iyz="0.0" izz="0.001"/>
      </inertial>
    </link>

    <joint name="base_to_${prefix}_wheel" type="continuous">
      <parent link="base_link"/>
      <child link="${prefix}_wheel"/>
      <origin xyz="${base_length/2 - wheel_width/2} ${reflect * wheel_y_offset} -${base_height/2}" rpy="1.5708 0 0"/>
      <axis xyz="0 0 1"/>
    </joint>

    <gazebo reference="${prefix}_wheel">
      <mu1>1.0</mu1>
      <mu2>1.0</mu2>
      <kp>1000000.0</kp>
      <kd>100.0</kd>
    </gazebo>
  </xacro:macro>

  <!-- Instantiate wheels -->
  <xacro:simple_wheel prefix="left" reflect="1"/>
  <xacro:simple_wheel prefix="right" reflect="-1"/>

  <!-- LiDAR sensor -->
  <link name="lidar_link">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.05"/>
      </geometry>
      <material name="silver">
        <color rgba="0.7 0.7 0.7 1.0"/>
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
    <origin xyz="0.15 0 ${base_height/2}"/>
  </joint>

  <!-- Gazebo plugins -->
  <gazebo reference="base_link">
    <material>Gazebo/Blue</material>
  </gazebo>

  <gazebo>
    <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">
      <ros>
        <namespace>$(arg robot_name)</namespace>
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

  <gazebo reference="lidar_link">
    <sensor name="lidar" type="ray">
      <always_on>true</always_on>
      <update_rate>40</update_rate>
      <ray>
        <scan>
          <horizontal>
            <samples>360</samples>
            <resolution>1</resolution>
            <min_angle>-3.14159</min_angle>
            <max_angle>3.14159</max_angle>
          </horizontal>
        </scan>
        <range>
          <min>0.10</min>
          <max>10.0</max>
          <resolution>0.01</resolution>
        </range>
      </ray>
      <plugin name="lidar_controller" filename="libgazebo_ros_ray_sensor.so">
        <ros>
          <namespace>$(arg robot_name)</namespace>
          <remapping>~/out:=scan</remapping>
        </ros>
        <output_type>sensor_msgs/LaserScan</output_type>
      </plugin>
    </sensor>
  </gazebo>

</robot>
```

### 7.2.2 Create a More Complex Robot Model

Create `models/complex_robot/urdf/complex_robot.xacro`:

```xml
<?xml version="1.0"?>
<robot name="complex_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Robot properties -->
  <xacro:property name="chassis_length" value="0.8"/>
  <xacro:property name="chassis_width" value="0.6"/>
  <xacro:property name="chassis_height" value="0.3"/>
  <xacro:property name="wheel_radius" value="0.15"/>
  <xacro:property name="wheel_width" value="0.08"/>
  <xacro:property name="wheel_y_offset" value="0.35"/>

  <!-- Chassis -->
  <link name="chassis">
    <visual>
      <geometry>
        <box size="${chassis_length} ${chassis_width} ${chassis_height}"/>
      </geometry>
      <material name="orange">
        <color rgba="1.0 0.6 0.0 1.0"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="${chassis_length} ${chassis_width} ${chassis_height}"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="0.5" ixy="0.0" ixz="0.0" iyy="0.5" iyz="0.0" izz="0.5"/>
    </inertial>
  </link>

  <!-- Wheels -->
  <xacro:macro name="omni_wheel" params="prefix x_pos y_pos">
    <link name="${prefix}_wheel">
      <visual>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_width}"/>
        </geometry>
        <material name="black">
          <color rgba="0.1 0.1 0.1 1.0"/>
        </material>
      </visual>
      <collision>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_width}"/>
        </geometry>
      </collision>
      <inertial>
        <mass value="1.0"/>
        <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.02"/>
      </inertial>
    </link>

    <joint name="chassis_to_${prefix}_wheel" type="continuous">
      <parent link="chassis"/>
      <child link="${prefix}_wheel"/>
      <origin xyz="${x_pos} ${y_pos} -${chassis_height/2}" rpy="1.5708 0 0"/>
      <axis xyz="0 0 1"/>
    </joint>

    <gazebo reference="${prefix}_wheel">
      <mu1>0.1</mu1>  <!-- Lower friction for omni-directional movement -->
      <mu2>0.1</mu2>
      <kp>1000000.0</kp>
      <kd>100.0</kd>
    </gazebo>
  </xacro:macro>

  <!-- Create 4 omni wheels -->
  <xacro:omni_wheel prefix="front_left" x_pos="${chassis_length/2 - wheel_width/2}" y_pos="${wheel_y_offset}"/>
  <xacro:omni_wheel prefix="front_right" x_pos="${chassis_length/2 - wheel_width/2}" y_pos="${-wheel_y_offset}"/>
  <xacro:omni_wheel prefix="rear_left" x_pos="${-chassis_length/2 + wheel_width/2}" y_pos="${wheel_y_offset}"/>
  <xacro:omni_wheel prefix="rear_right" x_pos="${-chassis_length/2 + wheel_width/2}" y_pos="${-wheel_y_offset}"/>

  <!-- Camera -->
  <link name="camera_link">
    <visual>
      <geometry>
        <box size="0.05 0.05 0.05"/>
      </geometry>
      <material name="red">
        <color rgba="1.0 0.0 0.0 1.0"/>
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

  <joint name="chassis_to_camera" type="fixed">
    <parent link="chassis"/>
    <child link="camera_link"/>
    <origin xyz="${chassis_length/2 - 0.05} 0 ${chassis_height/2}"/>
  </joint>

  <!-- Gazebo plugins -->
  <gazebo reference="chassis">
    <material>Gazebo/Orange</material>
  </gazebo>

  <!-- Mecanum drive plugin -->
  <gazebo>
    <plugin name="mecanum_drive" filename="libgazebo_ros_skid_steer_drive.so">
      <ros>
        <namespace>$(arg robot_name)</namespace>
        <remapping>cmd_vel:=cmd_vel</remapping>
        <remapping>odom:=odom</remapping>
      </ros>
      <update_rate>30</update_rate>
      <left_front_joint>chassis_to_front_left_wheel</left_front_joint>
      <right_front_joint>chassis_to_front_right_wheel</right_front_joint>
      <left_rear_joint>chassis_to_rear_left_wheel</left_rear_joint>
      <right_rear_joint>chassis_to_rear_right_wheel</right_rear_joint>
      <wheel_separation>0.7</wheel_separation>
      <wheel_diameter>0.3</wheel_diameter>
      <max_wheel_torque>20</max_wheel_torque>
      <max_wheel_acceleration>1.0</max_wheel_acceleration>
      <command_topic>cmd_vel</command_topic>
      <odometry_topic>odom</odometry_topic>
      <odometry_frame>odom</odometry_frame>
      <robot_base_frame>chassis</robot_base_frame>
      <publish_odom>true</publish_odom>
      <publish_odom_tf>true</publish_odom_tf>
      <publish_wheel_tf>true</publish_wheel_tf>
    </plugin>
  </gazebo>

  <!-- Camera plugin -->
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
          <far>300</far>
        </clip>
      </camera>
      <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
        <ros>
          <namespace>$(arg robot_name)</namespace>
          <remapping>~/image_raw:=image_raw</remapping>
          <remapping>~/camera_info:=camera_info</remapping>
        </ros>
        <frame_name>camera_link</frame_name>
      </plugin>
    </sensor>
  </gazebo>

</robot>
```

## 7.3 Creating Complex World Environments

### 7.3.1 Create a Multi-Room World

Create `worlds/complex/multi_room.world`:

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="multi_room">
    <!-- Physics Engine -->
    <physics type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000.0</real_time_update_rate>
      <ode>
        <solver>
          <type>quick</type>
          <iters>50</iters>
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

    <!-- Room 1: Laboratory -->
    <model name="room1_walls">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>10 10 2</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>10 10 2</size></box>
          </geometry>
          <material>
            <ambient>0.9 0.9 0.9 1</ambient>
            <diffuse>0.9 0.9 0.9 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>0 0 1 0 0 0</pose>
    </model>

    <!-- Room 2: Office -->
    <model name="room2_walls">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>10 10 2</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>10 10 2</size></box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.9 1</ambient>
            <diffuse>0.8 0.8 0.9 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>0 12 1 0 0 0</pose>
    </model>

    <!-- Room 3: Warehouse -->
    <model name="room3_walls">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>15 15 3</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>15 15 3</size></box>
          </geometry>
          <material>
            <ambient>0.7 0.7 0.7 1</ambient>
            <diffuse>0.7 0.7 0.7 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>0 -12 1.5 0 0 0</pose>
    </model>

    <!-- Doorways connecting rooms -->
    <model name="doorway_12">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>2 0.2 2</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>2 0.2 2</size></box>
          </geometry>
          <material>
            <ambient>0.5 0.3 0.1 1</ambient>
            <diffuse>0.5 0.3 0.1 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>0 5 1 0 0 0</pose>
    </model>

    <model name="doorway_13">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>2 0.2 2</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>2 0.2 2</size></box>
          </geometry>
          <material>
            <ambient>0.5 0.3 0.1 1</ambient>
            <diffuse>0.5 0.3 0.1 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>0 -5 1 0 0 0</pose>
    </model>

    <!-- Room 1: Laboratory furniture -->
    <model name="lab_table_1">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>2 1 0.8</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>2 1 0.8</size></box>
          </geometry>
          <material>
            <ambient>0.4 0.4 0.4 1</ambient>
            <diffuse>0.4 0.4 0.4 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>-3 2 0.4 0 0 0</pose>
    </model>

    <model name="lab_table_2">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>1.5 0.8 0.75</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>1.5 0.8 0.75</size></box>
          </geometry>
          <material>
            <ambient>0.4 0.4 0.4 1</ambient>
            <diffuse>0.4 0.4 0.4 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>3 -2 0.375 0 0 0</pose>
    </model>

    <!-- Room 2: Office furniture -->
    <model name="office_desk">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>1.8 0.9 0.75</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>1.8 0.9 0.75</size></box>
          </geometry>
          <material>
            <ambient>0.6 0.4 0.2 1</ambient>
            <diffuse>0.6 0.4 0.2 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>0 10 0.375 0 0 0</pose>
    </model>

    <model name="office_chair">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <cylinder><radius>0.3</radius><length>0.5</length></cylinder>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <cylinder><radius>0.3</radius><length>0.5</length></cylinder>
          </geometry>
          <material>
            <ambient>0.2 0.2 0.6 1</ambient>
            <diffuse>0.2 0.2 0.6 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>0.8 10 0.25 0 0 0</pose>
    </model>

    <!-- Room 3: Warehouse obstacles -->
    <model name="pallet_1">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>1.2 1.0 1.5</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>1.2 1.0 1.5</size></box>
          </geometry>
          <material>
            <ambient>0.8 0.6 0.2 1</ambient>
            <diffuse>0.8 0.6 0.2 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>-5 -10 0.75 0 0 0</pose>
    </model>

    <model name="pallet_2">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>1.2 1.0 1.2</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>1.2 1.0 1.2</size></box>
          </geometry>
          <material>
            <ambient>0.8 0.6 0.2 1</ambient>
            <diffuse>0.8 0.6 0.2 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>5 -8 0.6 0 0 0</pose>
    </model>

    <model name="pallet_3">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>1.2 1.0 0.9</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>1.2 1.0 0.9</size></box>
          </geometry>
          <material>
            <ambient>0.8 0.6 0.2 1</ambient>
            <diffuse>0.8 0.6 0.2 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>-2 -14 0.45 0 0 0</pose>
    </model>

    <!-- Dynamic obstacles -->
    <model name="moving_obstacle_1">
      <link name="link">
        <collision name="collision">
          <geometry>
            <sphere><radius>0.3</radius></sphere>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <sphere><radius>0.3</radius></sphere>
          </geometry>
          <material>
            <ambient>1.0 0.0 0.0 0.7</ambient>
            <diffuse>1.0 0.0 0.0 0.7</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>5.0</mass>
          <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1"/>
        </inertial>
      </link>
      <pose>-4 0 0.3 0 0 0</pose>
      <plugin name="moving_obstacle_1_controller" filename="libgazebo_ros_p3d.so">
        <ros>
          <namespace>/moving_obstacles</namespace>
          <remapping>~/state:=moving_obstacle_1_state</remapping>
        </ros>
        <body_name>link</body_name>
        <update_rate>30</update_rate>
        <gaussian_noise>0.001</gaussian_noise>
        <frame_name>world</frame_name>
      </plugin>
    </model>

    <model name="moving_obstacle_2">
      <link name="link">
        <collision name="collision">
          <geometry>
            <cylinder><radius>0.25</radius><length>0.5</length></cylinder>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <cylinder><radius>0.25</radius><length>0.5</length></cylinder>
          </geometry>
          <material>
            <ambient>0.0 1.0 0.0 0.7</ambient>
            <diffuse>0.0 1.0 0.0 0.7</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>3.0</mass>
          <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1"/>
        </inertial>
      </link>
      <pose>3 8 0.25 0 0 0</pose>
    </model>

    <!-- Environmental conditions -->
    <model name="wind_generator">
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry>
            <box><size>0.1 0.1 0.1</size></box>
          </geometry>
        </visual>
      </link>
      <pose>0 0 2 0 0 0</pose>
      <plugin name="wind_plugin" filename="libgazebo_ros_wind.so">
        <ros>
          <namespace>/environment</namespace>
        </ros>
        <wind_direction>1 0 0</wind_direction>
        <wind_force>0.5 0.1 0</wind_force>
        <wind_velocity>1.0</wind_velocity>
      </plugin>
    </model>

  </world>
</sdf>
```

### 7.3.2 Create a Warehouse World

Create `worlds/complex/warehouse.world`:

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="warehouse">
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

    <!-- Warehouse structure -->
    <model name="warehouse_walls">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>30 20 8</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>30 20 8</size></box>
          </geometry>
          <material>
            <ambient>0.7 0.7 0.7 1</ambient>
            <diffuse>0.7 0.7 0.7 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>0 0 4 0 0 0</pose>
    </model>

    <!-- Warehouse floor (with different friction) -->
    <model name="warehouse_floor">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>29 19 0.1</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>29 19 0.1</size></box>
          </geometry>
          <material>
            <ambient>0.4 0.4 0.4 1</ambient>
            <diffuse>0.4 0.4 0.4 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>0 0 0.05 0 0 0</pose>
      <surface>
        <friction>
          <ode>
            <mu>0.8</mu>
            <mu2>0.8</mu2>
          </ode>
        </friction>
      </surface>
    </model>

    <!-- Warehouse shelves -->
    <xacro:macro name="shelf_unit" params="x_pos y_pos">
      <model name="shelf_${x_pos}_${y_pos}">
        <static>true</static>
        <link name="link">
          <collision name="collision">
            <geometry>
              <box><size>2.5 0.8 2.0</size></box>
            </geometry>
          </collision>
          <visual name="visual">
            <geometry>
              <box><size>2.5 0.8 2.0</size></box>
            </geometry>
            <material>
              <ambient>0.6 0.4 0.2 1</ambient>
              <diffuse>0.6 0.4 0.2 1</diffuse>
            </material>
          </visual>
        </link>
        <pose>${x_pos} ${y_pos} 1.0 0 0 0</pose>
      </model>
    </xacro:macro>

    <!-- Create a grid of shelves -->
    <xacro:shelf_unit x_pos="-12" y_pos="6"/>
    <xacro:shelf_unit x_pos="-12" y_pos="4"/>
    <xacro:shelf_unit x_pos="-12" y_pos="2"/>
    <xacro:shelf_unit x_pos="-12" y_pos="0"/>
    <xacro:shelf_unit x_pos="-12" y_pos="-2"/>
    <xacro:shelf_unit x_pos="-12" y_pos="-4"/>
    <xacro:shelf_unit x_pos="-12" y_pos="-6"/>

    <xacro:shelf_unit x_pos="12" y_pos="6"/>
    <xacro:shelf_unit x_pos="12" y_pos="4"/>
    <xacro:shelf_unit x_pos="12" y_pos="2"/>
    <xacro:shelf_unit x_pos="12" y_pos="0"/>
    <xacro:shelf_unit x_pos="12" y_pos="-2"/>
    <xacro:shelf_unit x_pos="12" y_pos="-4"/>
    <xacro:shelf_unit x_pos="12" y_pos="-6"/>

    <!-- Loading dock area -->
    <model name="loading_dock">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>5 10 0.1</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>5 10 0.1</size></box>
          </geometry>
          <material>
            <ambient>0.5 0.5 0.5 1</ambient>
            <diffuse>0.5 0.5 0.5 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>13 0 0.05 0 0 0</pose>
    </model>

    <!-- Conveyor belt area -->
    <model name="conveyor_area">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>8 2 0.1</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>8 2 0.1</size></box>
          </geometry>
          <material>
            <ambient>0.3 0.3 0.3 1</ambient>
            <diffuse>0.3 0.3 0.3 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>-8 0 0.05 0 0 0</pose>
    </model>

    <!-- Pallets -->
    <model name="pallet_1">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>1.2 1.0 0.15</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>1.2 1.0 0.15</size></box>
          </geometry>
          <material>
            <ambient>0.8 0.6 0.2 1</ambient>
            <diffuse>0.8 0.6 0.2 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>-5 5 0.075 0 0 0</pose>
    </model>

    <model name="pallet_2">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>1.2 1.0 0.15</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>1.2 1.0 0.15</size></box>
          </geometry>
          <material>
            <ambient>0.8 0.6 0.2 1</ambient>
            <diffuse>0.8 0.6 0.2 1</diffuse>
          </material>
        </visual>
      </link>
      <pose>-5 -5 0.075 0 0 0</pose>
    </model>

    <!-- Moving objects on conveyor -->
    <model name="moving_box_1">
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>0.5 0.5 0.5</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>0.5 0.5 0.5</size></box>
          </geometry>
          <material>
            <ambient>1.0 0.0 0.0 1</ambient>
            <diffuse>1.0 0.0 0.0 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>1.0</mass>
          <inertia ixx="0.05" ixy="0.0" ixz="0.0" iyy="0.05" iyz="0.0" izz="0.05"/>
        </inertial>
      </link>
      <pose>-6 0 0.25 0 0 0</pose>
    </model>

    <!-- Lighting -->
    <light name="warehouse_light_1" type="point">
      <pose>-10 8 6 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>20</range>
        <constant>0.2</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
    </light>

    <light name="warehouse_light_2" type="point">
      <pose>10 8 6 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>20</range>
        <constant>0.2</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
    </light>

    <light name="warehouse_light_3" type="point">
      <pose>-10 -8 6 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>20</range>
        <constant>0.2</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
    </light>

    <light name="warehouse_light_4" type="point">
      <pose>10 -8 6 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>20</range>
        <constant>0.2</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
    </light>

  </world>
</sdf>
```

## 7.4 Creating Launch Files for Complex Scenarios

### 7.4.1 Multi-Robot Launch File

Create `launch/multi_robot.launch.py`:

```python
import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world = LaunchConfiguration('world', default='multi_room.world')

    # Get package share directory
    pkg_share = FindPackageShare('complex_env_sim').find('complex_env_sim')

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
            'world': PathJoinSubstitution([pkg_share, 'worlds', 'complex', world]),
            'verbose': 'false',
        }.items()
    )

    # Robot 1: Simple robot in room 1
    robot1_group = GroupAction(
        actions=[
            PushRosNamespace('robot1'),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([
                        FindPackageShare('complex_env_sim'),
                        'launch',
                        'spawn_robot.launch.py'
                    ])
                ]),
                launch_arguments={
                    'robot_name': 'robot1',
                    'robot_type': 'simple',
                    'x_pose': '0.0',
                    'y_pose': '0.0',
                    'z_pose': '0.1'
                }.items()
            )
        ]
    )

    # Robot 2: Complex robot in room 2
    robot2_group = GroupAction(
        actions=[
            PushRosNamespace('robot2'),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([
                        FindPackageShare('complex_env_sim'),
                        'launch',
                        'spawn_robot.launch.py'
                    ])
                ]),
                launch_arguments={
                    'robot_name': 'robot2',
                    'robot_type': 'complex',
                    'x_pose': '0.0',
                    'y_pose': '10.0',  # In room 2
                    'z_pose': '0.1'
                }.items()
            )
        ]
    )

    # Robot 3: Simple robot in room 3
    robot3_group = GroupAction(
        actions=[
            PushRosNamespace('robot3'),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([
                        FindPackageShare('complex_env_sim'),
                        'launch',
                        'spawn_robot.launch.py'
                    ])
                ]),
                launch_arguments={
                    'robot_name': 'robot3',
                    'robot_type': 'simple',
                    'x_pose': '0.0',
                    'y_pose': '-10.0',  # In room 3
                    'z_pose': '0.1'
                }.items()
            )
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            'world',
            default_value='multi_room.world',
            description='Choose one of the world files from `/complex_env_sim/worlds/complex`'
        ),
        gazebo,
        robot1_group,
        robot2_group,
        robot3_group
    ])
```

### 7.4.2 Spawn Robot Launch File

Create `launch/spawn_robot.launch.py`:

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Launch arguments
    robot_name = LaunchConfiguration('robot_name')
    robot_type = LaunchConfiguration('robot_type')
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    z_pose = LaunchConfiguration('z_pose', default='0.1')

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'use_sim_time': True},
            {'robot_description':
                # This would be loaded from the appropriate URDF based on robot_type
                # For this example, we'll use a placeholder
                open(PathJoinSubstitution([
                    FindPackageShare('complex_env_sim'),
                    'models',
                    LaunchConfiguration('robot_type').perform(context) + '_robot',
                    'urdf',
                    LaunchConfiguration('robot_type').perform(context) + '_robot.xacro'
                ]).replace('$(arg robot_type)', robot_type.perform(context))).read()
            }
        ]
    )

    # Spawn entity
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', robot_name,
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose
        ],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('robot_name', description='Name of the robot to spawn'),
        DeclareLaunchArgument('robot_type', description='Type of robot (simple/complex)'),
        DeclareLaunchArgument('x_pose', default_value='0.0', description='X position'),
        DeclareLaunchArgument('y_pose', default_value='0.0', description='Y position'),
        DeclareLaunchArgument('z_pose', default_value='0.1', description='Z position'),
        robot_state_publisher,
        spawn_entity
    ])
```

Actually, let me create a simpler version of the spawn robot launch file:

```python
# Save as launch/spawn_simple_robot.launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Launch arguments
    robot_name = LaunchConfiguration('robot_name')
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    z_pose = LaunchConfiguration('z_pose', default='0.1')

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'use_sim_time': True},
            {'robot_description':
                open(PathJoinSubstitution([
                    FindPackageShare('complex_env_sim'),
                    'models',
                    'simple_robot',
                    'urdf',
                    'simple_robot.xacro'
                ]).perform()).read()
            }
        ]
    )

    # Spawn entity
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', robot_name,
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose
        ],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('robot_name', description='Name of the robot to spawn'),
        DeclareLaunchArgument('x_pose', default_value='0.0', description='X position'),
        DeclareLaunchArgument('y_pose', default_value='0.0', description='Y position'),
        DeclareLaunchArgument('z_pose', default_value='0.1', description='Z position'),
        robot_state_publisher,
        spawn_entity
    ])
```

## 7.5 Creating Advanced Controllers

### 7.5.1 Multi-Robot Coordination Controller

Create `scripts/controllers/multi_robot_coordinator.py`:

```python
#!/usr/bin/env python3
"""
File: multi_robot_coordinator.py
Purpose: Coordinating multiple robots in a complex environment
Chapter: 7 - Advanced Simulation Techniques
Dependencies: rclpy, geometry_msgs, std_msgs, tf2_ros
Hardware: Multiple simulated robots in Gazebo
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from std_msgs.msg import String, Float32
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
import math
import random


class MultiRobotCoordinator(Node):
    """
    Coordinates multiple robots in a complex environment to avoid collisions
    and achieve coordinated goals.
    """

    def __init__(self):
        super().__init__('multi_robot_coordinator')

        # Robot configuration
        self.robot_names = ['robot1', 'robot2', 'robot3']
        self.robots = {}
        self.active_goals = {}

        # TF2 buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Create publishers for each robot
        self.robot_publishers = {}
        for robot_name in self.robot_names:
            self.robot_publishers[robot_name] = self.create_publisher(
                Twist,
                f'/{robot_name}/cmd_vel',
                10
            )

        # Create subscribers for robot states
        for robot_name in self.robot_names:
            self.create_subscription(
                String,
                f'/{robot_name}/status',
                self.create_robot_status_callback(robot_name),
                10
            )

        # Timer for coordination
        self.coordination_timer = self.create_timer(0.5, self.coordination_callback)

        # Initialize robot states
        for robot_name in self.robot_names:
            self.robots[robot_name] = {
                'position': None,
                'velocity': None,
                'status': 'idle',
                'last_command': None
            }

        self.get_logger().info('Multi-robot coordinator initialized')

    def create_robot_status_callback(self, robot_name):
        """Create a callback function for a specific robot."""
        def callback(msg):
            self.robots[robot_name]['status'] = msg.data
        return callback

    def coordination_callback(self):
        """Main coordination logic."""
        # Get current positions of all robots
        for robot_name in self.robot_names:
            try:
                t = self.tf_buffer.lookup_transform(
                    'world',
                    f'{robot_name}/base_link',
                    rclpy.time.Time()
                )
                self.robots[robot_name]['position'] = [
                    t.transform.translation.x,
                    t.transform.translation.y,
                    t.transform.translation.z
                ]
            except TransformException as ex:
                self.get_logger().warning(f'Could not transform {robot_name}: {ex}')

        # Check for potential collisions and coordinate movements
        self.check_collisions_and_coordinate()

    def check_collisions_and_coordinate(self):
        """Check for potential collisions and coordinate robot movements."""
        for i, robot1_name in enumerate(self.robot_names):
            for j, robot2_name in enumerate(self.robot_names):
                if i >= j:  # Avoid duplicate checks
                    continue

                pos1 = self.robots[robot1_name]['position']
                pos2 = self.robots[robot2_name]['position']

                if pos1 and pos2:
                    distance = math.sqrt(
                        (pos1[0] - pos2[0])**2 +
                        (pos1[1] - pos2[1])**2
                    )

                    # If robots are too close, coordinate movement
                    if distance < 1.0:  # 1 meter threshold
                        self.get_logger().info(f'Potential collision between {robot1_name} and {robot2_name}')
                        self.coordinate_robots(robot1_name, robot2_name)

    def coordinate_robots(self, robot1_name, robot2_name):
        """Coordinate movement of two potentially colliding robots."""
        # Simple coordination: robot with higher alphabetical name moves first
        if robot1_name > robot2_name:
            self.move_robot_away(robot1_name, robot2_name)
        else:
            self.move_robot_away(robot2_name, robot1_name)

    def move_robot_away(self, robot_to_move, other_robot):
        """Move one robot away from another."""
        pos_to_move = self.robots[robot_to_move]['position']
        pos_other = self.robots[other_robot]['position']

        if pos_to_move and pos_other:
            # Calculate direction away from other robot
            dx = pos_to_move[0] - pos_other[0]
            dy = pos_to_move[1] - pos_other[1]
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 0:
                # Normalize and create movement command
                move_x = (dx / distance) * 0.2  # Move away at 0.2 m/s
                move_y = (dy / distance) * 0.2

                cmd_vel = Twist()
                cmd_vel.linear.x = move_x
                cmd_vel.linear.y = move_y
                cmd_vel.angular.z = random.uniform(-0.2, 0.2)  # Add some randomness

                self.robot_publishers[robot_to_move].publish(cmd_vel)
                self.get_logger().info(f'{robot_to_move} moving away from {other_robot}')


class RobotController(Node):
    """
    Individual robot controller with advanced behaviors.
    """

    def __init__(self, robot_name):
        super().__init__(f'{robot_name}_controller')
        self.robot_name = robot_name

        # Create publisher for velocity commands
        self.cmd_vel_pub = self.create_publisher(Twist, f'/{robot_name}/cmd_vel', 10)

        # Create subscriber for laser scan
        self.scan_sub = self.create_subscription(
            String,
            f'/{robot_name}/scan_processed',  # Processed scan data
            self.scan_callback,
            10
        )

        # Create publisher for robot status
        self.status_pub = self.create_publisher(String, f'/{robot_name}/status', 10)

        # Timer for control loop
        self.control_timer = self.create_timer(0.1, self.control_loop)

        # Robot state
        self.state = 'exploring'  # exploring, avoiding, following, etc.
        self.obstacle_detected = False
        self.target_direction = None

        # Publish initial status
        self.publish_status()

    def scan_callback(self, msg):
        """Process processed scan data."""
        # In a real implementation, this would process the scan
        # For this example, we'll just simulate obstacle detection
        pass

    def control_loop(self):
        """Main control loop."""
        cmd_vel = Twist()

        if self.state == 'exploring':
            cmd_vel.linear.x = 0.3
            cmd_vel.angular.z = random.uniform(-0.3, 0.3)
        elif self.state == 'avoiding':
            cmd_vel.linear.x = 0.0
            cmd_vel.angular.z = 0.5  # Turn to avoid
        elif self.state == 'following':
            cmd_vel.linear.x = 0.4
            cmd_vel.angular.z = 0.0

        self.cmd_vel_pub.publish(cmd_vel)
        self.publish_status()

    def publish_status(self):
        """Publish robot status."""
        status_msg = String()
        status_msg.data = self.state
        self.status_pub.publish(status_msg)


def main(args=None):
    rclpy.init(args=args)

    # Create coordinator node
    coordinator = MultiRobotCoordinator()

    # Create individual robot controllers
    robot_controllers = []
    for robot_name in ['robot1', 'robot2', 'robot3']:
        controller = RobotController(robot_name)
        robot_controllers.append(controller)

    # Create executor and add all nodes
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(coordinator)
    for controller in robot_controllers:
        executor.add_node(controller)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        coordinator.destroy_node()
        for controller in robot_controllers:
            controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### 7.5.2 Environmental Disturbance Simulator

Create `scripts/controllers/environmental_simulator.py`:

```python
#!/usr/bin/env python3
"""
File: environmental_simulator.py
Purpose: Simulating environmental disturbances and conditions
Chapter: 7 - Advanced Simulation Techniques
Dependencies: rclpy, std_msgs, geometry_msgs
Hardware: Simulated environment in Gazebo
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Bool
from geometry_msgs.msg import Vector3
from gazebo_msgs.srv import SetModelState
from gazebo_msgs.msg import ModelState
import random
import math


class EnvironmentalSimulator(Node):
    """
    Simulates environmental disturbances like wind, vibrations, and lighting changes.
    """

    def __init__(self):
        super().__init__('environmental_simulator')

        # Environmental disturbance publishers
        self.wind_pub = self.create_publisher(Vector3, '/environment/wind_force', 10)
        self.vibration_pub = self.create_publisher(Float32, '/environment/vibration_level', 10)
        self.light_pub = self.create_publisher(Float32, '/environment/light_intensity', 10)

        # Timer for environmental updates
        self.env_timer = self.create_timer(0.1, self.update_environment)

        # Service client for moving objects in environment
        self.set_model_state_cli = self.create_client(SetModelState, '/gazebo/set_model_state')

        # Environmental parameters
        self.wind_force = Vector3()
        self.vibration_level = 0.0
        self.light_intensity = 1.0
        self.time_of_day = 0.0  # 0-24 hours

        # Disturbance patterns
        self.wind_pattern = 'normal'  # normal, gusty, storm
        self.vibration_pattern = 'low'  # low, medium, high

        self.get_logger().info('Environmental simulator initialized')

    def update_environment(self):
        """Update environmental conditions."""
        # Update wind conditions
        self.update_wind()

        # Update vibration levels
        self.update_vibration()

        # Update lighting conditions
        self.update_lighting()

        # Publish environmental data
        self.wind_pub.publish(self.wind_force)
        self.vibration_pub.publish(Float32(data=self.vibration_level))
        self.light_pub.publish(Float32(data=self.light_intensity))

        # Update time of day
        self.time_of_day += 0.01  # Simulate time passing
        if self.time_of_day >= 24.0:
            self.time_of_day = 0.0

    def update_wind(self):
        """Update wind conditions based on pattern."""
        if self.wind_pattern == 'normal':
            # Gentle, variable wind
            self.wind_force.x = random.uniform(-0.2, 0.2)
            self.wind_force.y = random.uniform(-0.1, 0.1)
            self.wind_force.z = 0.0
        elif self.wind_pattern == 'gusty':
            # More variable wind with occasional gusts
            self.wind_force.x = random.uniform(-0.5, 0.5)
            self.wind_force.y = random.uniform(-0.3, 0.3)
            self.wind_force.z = 0.0

            # Occasional gusts
            if random.random() < 0.05:  # 5% chance per update
                self.wind_force.x += random.uniform(-1.0, 1.0)
                self.wind_force.y += random.uniform(-0.5, 0.5)
        elif self.wind_pattern == 'storm':
            # Strong, chaotic wind
            self.wind_force.x = random.uniform(-1.0, 1.0)
            self.wind_force.y = random.uniform(-0.8, 0.8)
            self.wind_force.z = random.uniform(-0.2, 0.2)

    def update_vibration(self):
        """Update vibration levels."""
        if self.vibration_pattern == 'low':
            self.vibration_level = random.uniform(0.0, 0.1)
        elif self.vibration_pattern == 'medium':
            self.vibration_level = random.uniform(0.1, 0.3)
        elif self.vibration_pattern == 'high':
            self.vibration_level = random.uniform(0.3, 0.6)

    def update_lighting(self):
        """Update lighting based on time of day and weather."""
        # Base lighting based on time of day (simplified)
        hour_factor = math.sin((self.time_of_day / 24.0) * 2 * math.pi - math.pi/2)  # -1 to 1, peaks at noon
        base_light = 0.5 + 0.5 * hour_factor  # 0 to 1

        # Apply weather effects
        if self.wind_pattern == 'storm':
            base_light *= 0.3  # Much darker during storms
        elif self.wind_pattern == 'gusty':
            base_light *= 0.7  # Somewhat darker during gusty conditions

        self.light_intensity = max(0.1, min(1.0, base_light))  # Clamp between 0.1 and 1.0

    def set_wind_pattern(self, pattern):
        """Set the wind pattern."""
        if pattern in ['normal', 'gusty', 'storm']:
            self.wind_pattern = pattern
            self.get_logger().info(f'Wind pattern set to {pattern}')

    def set_vibration_pattern(self, pattern):
        """Set the vibration pattern."""
        if pattern in ['low', 'medium', 'high']:
            self.vibration_pattern = pattern
            self.get_logger().info(f'Vibration pattern set to {pattern}')


def main(args=None):
    rclpy.init(args=args)

    simulator = EnvironmentalSimulator()

    try:
        rclpy.spin(simulator)
    except KeyboardInterrupt:
        pass
    finally:
        simulator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## 7.6 Running Complex Simulations

### 7.6.1 Build and Source the Package

```bash
# Navigate to your workspace
cd ~/ros2_ws

# Build the package
colcon build --packages-select complex_env_sim

# Source the workspace
source install/setup.bash
```

### 7.6.2 Launch the Multi-Robot Simulation

```bash
# Launch the multi-robot simulation in the multi-room world
ros2 launch complex_env_sim multi_robot.launch.py world:=multi_room.world
```

In another terminal, run the coordinator:

```bash
# Run the multi-robot coordinator
ros2 run complex_env_sim multi_robot_coordinator.py
```

And in another terminal, run the environmental simulator:

```bash
# Run the environmental simulator
ros2 run complex_env_sim environmental_simulator.py
```

## 7.7 Performance Optimization Techniques

### 7.7.1 Physics Optimization

For complex environments, optimize physics parameters in your world files:

```xml
<physics type="ode">
  <max_step_size>0.01</max_step_size>  <!-- Increase for performance -->
  <real_time_factor>0.5</real_time_factor>  <!-- Allow simulation to run slower -->
  <real_time_update_rate>100.0</real_time_update_rate>
  <ode>
    <solver>
      <type>quick</type>
      <iters>20</iters>  <!-- Reduce iterations for performance -->
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

### 7.7.2 Sensor Optimization

Reduce sensor update rates for performance:

```xml
<sensor name="lidar" type="ray">
  <always_on>true</always_on>
  <update_rate>20</update_rate>  <!-- Reduce from 40 to 20 Hz -->
  <!-- ... other parameters ... -->
</sensor>
```

## 7.8 Advanced Simulation Features

### 7.8.1 Creating Dynamic Obstacles

Create `models/dynamic_obstacle/urdf/dynamic_obstacle.xacro`:

```xml
<?xml version="1.0"?>
<robot name="dynamic_obstacle" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <link name="obstacle_base">
    <visual>
      <geometry>
        <sphere radius="0.3"/>
      </geometry>
      <material name="red">
        <color rgba="1.0 0.0 0.0 0.7"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.3"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Add simple controller plugin -->
  <gazebo>
    <plugin name="simple_controller" filename="libgazebo_ros_p3d.so">
      <ros>
        <namespace>/dynamic_obstacle</namespace>
        <remapping>~/state:=pose</remapping>
      </ros>
      <body_name>obstacle_base</body_name>
      <update_rate>30</update_rate>
      <gaussian_noise>0.001</gaussian_noise>
      <frame_name>world</frame_name>
    </plugin>
  </gazebo>

</robot>
```

### 7.8.2 Adding Sensor Noise Models

Add realistic sensor noise to your robot models:

```xml
<sensor name="noisy_camera" type="camera">
  <camera name="head">
    <noise>
      <type>gaussian</type>
      <mean>0.0</mean>
      <stddev>0.007</stddev>
    </noise>
  </camera>
  <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
    <ros>
      <namespace>$(arg robot_name)</namespace>
      <remapping>~/image_raw:=image_raw</remapping>
      <remapping>~/camera_info:=camera_info</remapping>
    </ros>
    <frame_name>camera_link</frame_name>
    <distortion_k1>0.1</distortion_k1>
    <distortion_k2>-0.2</distortion_k2>
    <distortion_k3>0.1</distortion_k3>
    <distortion_t1>0.0</distortion_t1>
    <distortion_t2>0.0</distortion_t2>
  </plugin>
</sensor>
```

## 7.9 Troubleshooting Complex Simulations

### Common Issues and Solutions

#### Issue 1: Performance Degradation
- **Cause**: Too many objects or high update rates
- **Solution**:
  - Reduce physics update rate
  - Simplify collision geometries
  - Reduce sensor update rates
  - Use fewer but more strategic objects

#### Issue 2: Robot Interference
- **Cause**: Multiple robots affecting each other's sensors
- **Solution**:
  - Use robot namespaces properly
  - Isolate TF trees if needed
  - Use collision filtering

#### Issue 3: Memory Leaks in Long-Running Simulations
- **Cause**: Accumulated data or callbacks not properly cleaned
- **Solution**:
  - Implement proper cleanup in node destruction
  - Use fixed-size buffers for data storage
  - Monitor memory usage regularly

## 7.10 Lab Assignment

### Task 1: Warehouse Navigation Challenge
Implement a navigation system for the warehouse environment:
1. Create a fleet of robots that can navigate between warehouse shelves
2. Implement path planning that considers dynamic obstacles
3. Add a task management system where robots can receive and complete orders

### Task 2: Environmental Adaptation
Add environmental adaptation capabilities:
1. Modify robot controllers to adapt to changing lighting conditions
2. Implement wind compensation for outdoor robots
3. Create sensor fusion that accounts for environmental disturbances

### Task 3: Large-Scale Performance
Optimize your simulation for 10+ robots:
1. Profile your simulation to identify bottlenecks
2. Implement level-of-detail (LOD) for distant robots
3. Optimize physics parameters for scalability

## 7.11 Summary

In this lab, you've learned how to:
- Create complex multi-robot environments with realistic physics
- Implement dynamic obstacles and environmental conditions
- Model sensor noise and environmental disturbances
- Coordinate multiple robots to avoid collisions
- Optimize simulation performance for complex scenarios
- Troubleshoot complex simulation issues

These skills are essential for developing and testing robotic systems in realistic, challenging environments that closely approximate real-world conditions.

## Review Questions

1. What are the key challenges when simulating multiple robots in the same environment?
2. How do environmental disturbances affect robot perception and navigation?
3. What techniques can be used to optimize simulation performance for large-scale scenarios?
4. How can you implement collision avoidance between multiple simulated robots?
5. What are the differences between simulating indoor vs. outdoor environments?

## Further Exploration

- Experiment with different physics engines and their performance characteristics
- Implement more sophisticated multi-robot coordination algorithms
- Explore domain randomization techniques for robust robot learning
- Investigate realistic sensor modeling with complex noise patterns
- Research large-scale simulation optimization techniques