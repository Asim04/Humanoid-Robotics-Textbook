---
sidebar_position: 5
---

# Lab 5: Building a Humanoid URDF Model

## Objective

In this lab, you will learn to create complex robot models using URDF (Unified Robot Description Format), specifically focusing on humanoid robots. You'll build a simplified humanoid model with multiple joints and links, gaining hands-on experience with advanced URDF concepts including kinematic chains, joint constraints, and visual/collision properties.

## Learning Outcomes

After completing this lab, you will be able to:

- Create complex multi-link robot models in URDF
- Define different joint types for humanoid articulation
- Implement proper kinematic chains for leg and arm structures
- Apply Xacro macros for parameterized robot descriptions
- Validate and visualize robot models in RViz
- Integrate sensors and actuators into humanoid models

## Prerequisites

- Lab 3 and Lab 4 completed (basic ROS 2 and multi-node concepts)
- Understanding of URDF concepts from Chapter 5
- ROS 2 Humble Hawksbill installed
- Basic knowledge of 3D geometry and kinematics
- RViz and Gazebo experience

## Setup and Environment

### 1. Create a New Package for Humanoid Models

```bash
cd ~/ros2_labs/src
ros2 pkg create --build-type ament_python humanoid_models
```

### 2. Create Directory Structure

```bash
mkdir -p ~/ros2_labs/src/humanoid_models/humanoid_models
mkdir -p ~/ros2_labs/src/humanoid_models/urdf
mkdir -p ~/ros2_labs/src/humanoid_models/meshes
mkdir -p ~/ros2_labs/src/humanoid_models/launch
mkdir -p ~/ros2_labs/src/humanoid_models/config
```

## Implementation Steps

### Step 1: Create a Basic Humanoid Skeleton

Create a simplified humanoid model with torso, head, arms, and legs. Start with a basic URDF file:

```bash
touch ~/ros2_labs/src/humanoid_models/urdf/basic_humanoid.urdf
```

Add the following content to `basic_humanoid.urdf`:

```xml
<?xml version="1.0"?>
<robot name="basic_humanoid" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!-- Materials -->
  <material name="gray">
    <color rgba="0.5 0.5 0.5 1.0"/>
  </material>
  <material name="white">
    <color rgba="1.0 1.0 1.0 1.0"/>
  </material>
  <material name="black">
    <color rgba="0.0 0.0 0.0 1.0"/>
  </material>
  <material name="red">
    <color rgba="0.8 0.2 0.2 1.0"/>
  </material>
  <material name="blue">
    <color rgba="0.2 0.2 0.8 1.0"/>
  </material>

  <!-- Torso (base link) -->
  <link name="torso">
    <visual>
      <origin xyz="0 0 0.5" rpy="0 0 0"/>
      <geometry>
        <box size="0.3 0.3 1.0"/>
      </geometry>
      <material name="gray"/>
    </visual>
    <collision>
      <origin xyz="0 0 0.5" rpy="0 0 0"/>
      <geometry>
        <box size="0.3 0.3 1.0"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 0.5" rpy="0 0 0"/>
      <mass value="10.0"/>
      <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0"/>
    </inertial>
  </link>

  <!-- Head -->
  <link name="head">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <sphere radius="0.15"/>
      </geometry>
      <material name="white"/>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <sphere radius="0.15"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="2.0"/>
      <inertia ixx="0.05" ixy="0.0" ixz="0.0" iyy="0.05" iyz="0.0" izz="0.05"/>
    </inertial>
  </link>

  <joint name="neck_joint" type="revolute">
    <parent link="torso"/>
    <child link="head"/>
    <origin xyz="0 0 1.0" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.5" upper="0.5" effort="100" velocity="1"/>
  </joint>

  <!-- Left Arm -->
  <link name="left_upper_arm">
    <visual>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.05" length="0.2"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.05" length="0.2"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <mass value="1.0"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>
  </link>

  <joint name="left_shoulder_joint" type="revolute">
    <parent link="torso"/>
    <child link="left_upper_arm"/>
    <origin xyz="0.2 0 0.8" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="50" velocity="1"/>
  </joint>

  <link name="left_lower_arm">
    <visual>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.04" length="0.2"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.04" length="0.2"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <mass value="0.5"/>
      <inertia ixx="0.005" ixy="0.0" ixz="0.0" iyy="0.005" iyz="0.0" izz="0.005"/>
    </inertial>
  </link>

  <joint name="left_elbow_joint" type="revolute">
    <parent link="left_upper_arm"/>
    <child link="left_lower_arm"/>
    <origin xyz="0 0 -0.3" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="30" velocity="1"/>
  </joint>

  <!-- Right Arm -->
  <link name="right_upper_arm">
    <visual>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.05" length="0.2"/>
      </geometry>
      <material name="red"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.05" length="0.2"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <mass value="1.0"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>
  </link>

  <joint name="right_shoulder_joint" type="revolute">
    <parent link="torso"/>
    <child link="right_upper_arm"/>
    <origin xyz="-0.2 0 0.8" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="50" velocity="1"/>
  </joint>

  <link name="right_lower_arm">
    <visual>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.04" length="0.2"/>
      </geometry>
      <material name="red"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.04" length="0.2"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 -0.15" rpy="0 0 0"/>
      <mass value="0.5"/>
      <inertia ixx="0.005" ixy="0.0" ixz="0.0" iyy="0.005" iyz="0.0" izz="0.005"/>
    </inertial>
  </link>

  <joint name="right_elbow_joint" type="revolute">
    <parent link="right_upper_arm"/>
    <child link="right_lower_arm"/>
    <origin xyz="0 0 -0.3" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="30" velocity="1"/>
  </joint>

  <!-- Left Leg -->
  <link name="left_thigh">
    <visual>
      <origin xyz="0 0 -0.2" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.06" length="0.3"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.2" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.06" length="0.3"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 -0.2" rpy="0 0 0"/>
      <mass value="2.0"/>
      <inertia ixx="0.05" ixy="0.0" ixz="0.0" iyy="0.05" iyz="0.0" izz="0.05"/>
    </inertial>
  </link>

  <joint name="left_hip_joint" type="revolute">
    <parent link="torso"/>
    <child link="left_thigh"/>
    <origin xyz="0.1 0 0" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
  </joint>

  <link name="left_shin">
    <visual>
      <origin xyz="0 0 -0.2" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.05" length="0.3"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.2" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.05" length="0.3"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 -0.2" rpy="0 0 0"/>
      <mass value="1.5"/>
      <inertia ixx="0.03" ixy="0.0" ixz="0.0" iyy="0.03" iyz="0.0" izz="0.03"/>
    </inertial>
  </link>

  <joint name="left_knee_joint" type="revolute">
    <parent link="left_thigh"/>
    <child link="left_shin"/>
    <origin xyz="0 0 -0.4" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="0.0" effort="80" velocity="1"/>
  </joint>

  <link name="left_foot">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.2 0.1 0.05"/>
      </geometry>
      <material name="black"/>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.2 0.1 0.05"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="0.5"/>
      <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.001"/>
    </inertial>
  </link>

  <joint name="left_ankle_joint" type="revolute">
    <parent link="left_shin"/>
    <child link="left_foot"/>
    <origin xyz="0 0 -0.4" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.5" upper="0.5" effort="40" velocity="1"/>
  </joint>

  <!-- Right Leg -->
  <link name="right_thigh">
    <visual>
      <origin xyz="0 0 -0.2" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.06" length="0.3"/>
      </geometry>
      <material name="red"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.2" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.06" length="0.3"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 -0.2" rpy="0 0 0"/>
      <mass value="2.0"/>
      <inertia ixx="0.05" ixy="0.0" ixz="0.0" iyy="0.05" iyz="0.0" izz="0.05"/>
    </inertial>
  </link>

  <joint name="right_hip_joint" type="revolute">
    <parent link="torso"/>
    <child link="right_thigh"/>
    <origin xyz="-0.1 0 0" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
  </joint>

  <link name="right_shin">
    <visual>
      <origin xyz="0 0 -0.2" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.05" length="0.3"/>
      </geometry>
      <material name="red"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.2" rpy="0 0 0"/>
      <geometry>
        <capsule radius="0.05" length="0.3"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 -0.2" rpy="0 0 0"/>
      <mass value="1.5"/>
      <inertia ixx="0.03" ixy="0.0" ixz="0.0" iyy="0.03" iyz="0.0" izz="0.03"/>
    </inertial>
  </link>

  <joint name="right_knee_joint" type="revolute">
    <parent link="right_thigh"/>
    <child link="right_shin"/>
    <origin xyz="0 0 -0.4" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="0.0" effort="80" velocity="1"/>
  </joint>

  <link name="right_foot">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.2 0.1 0.05"/>
      </geometry>
      <material name="black"/>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.2 0.1 0.05"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="0.5"/>
      <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.001"/>
    </inertial>
  </link>

  <joint name="right_ankle_joint" type="revolute">
    <parent link="right_shin"/>
    <child link="right_foot"/>
    <origin xyz="0 0 -0.4" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.5" upper="0.5" effort="40" velocity="1"/>
  </joint>
</robot>
```

### Step 2: Create an Enhanced Humanoid Model with Xacro

Now create a more sophisticated version using Xacro for parameterization:

```bash
touch ~/ros2_labs/src/humanoid_models/urdf/humanoid_model.xacro
```

Add the following content:

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="humanoid_model">

  <!-- Properties -->
  <xacro:property name="M_PI" value="3.1415926535897931" />
  <xacro:property name="torso_height" value="1.0" />
  <xacro:property name="torso_width" value="0.3" />
  <xacro:property name="torso_depth" value="0.3" />
  <xacro:property name="head_radius" value="0.15" />
  <xacro:property name="upper_arm_length" value="0.3" />
  <xacro:property name="lower_arm_length" value="0.3" />
  <xacro:property name="upper_leg_length" value="0.4" />
  <xacro:property name="lower_leg_length" value="0.4" />
  <xacro:property name="foot_size" value="0.2 0.1 0.05" />

  <!-- Materials -->
  <material name="gray">
    <color rgba="0.5 0.5 0.5 1.0"/>
  </material>
  <material name="white">
    <color rgba="1.0 1.0 1.0 1.0"/>
  </material>
  <material name="black">
    <color rgba="0.0 0.0 0.0 1.0"/>
  </material>
  <material name="blue">
    <color rgba="0.2 0.2 0.8 1.0"/>
  </material>
  <material name="red">
    <color rgba="0.8 0.2 0.2 1.0"/>
  </material>

  <!-- Macro for creating limbs -->
  <xacro:macro name="limb" params="name side parent_link origin_xyz axis_xyz lower_limit upper_limit">
    <!-- Upper limb -->
    <link name="${side}_${name}_upper">
      <visual>
        <origin xyz="0 0 -${upper_arm_length/2}" rpy="0 0 0"/>
        <geometry>
          <capsule radius="0.05" length="${upper_arm_length}"/>
        </geometry>
        <material name="${side}"/>
      </visual>
      <collision>
        <origin xyz="0 0 -${upper_arm_length/2}" rpy="0 0 0"/>
        <geometry>
          <capsule radius="0.05" length="${upper_arm_length}"/>
        </geometry>
      </collision>
      <inertial>
        <origin xyz="0 0 -${upper_arm_length/2}" rpy="0 0 0"/>
        <mass value="1.0"/>
        <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
      </inertial>
    </link>

    <joint name="${side}_${name}_joint1" type="revolute">
      <parent link="${parent_link}"/>
      <child link="${side}_${name}_upper"/>
      <origin xyz="${origin_xyz}" rpy="0 0 0"/>
      <axis xyz="${axis_xyz}"/>
      <limit lower="${lower_limit}" upper="${upper_limit}" effort="50" velocity="1"/>
    </joint>

    <!-- Lower limb -->
    <link name="${side}_${name}_lower">
      <visual>
        <origin xyz="0 0 -${lower_arm_length/2}" rpy="0 0 0"/>
        <geometry>
          <capsule radius="0.04" length="${lower_arm_length}"/>
        </geometry>
        <material name="${side}"/>
      </visual>
      <collision>
        <origin xyz="0 0 -${lower_arm_length/2}" rpy="0 0 0"/>
        <geometry>
          <capsule radius="0.04" length="${lower_arm_length}"/>
        </geometry>
      </collision>
      <inertial>
        <origin xyz="0 0 -${lower_arm_length/2}" rpy="0 0 0"/>
        <mass value="0.5"/>
        <inertia ixx="0.005" ixy="0.0" ixz="0.0" iyy="0.005" iyz="0.0" izz="0.005"/>
      </inertial>
    </link>

    <joint name="${side}_${name}_joint2" type="revolute">
      <parent link="${side}_${name}_upper"/>
      <child link="${side}_${name}_lower"/>
      <origin xyz="0 0 -${upper_arm_length}" rpy="0 0 0"/>
      <axis xyz="${axis_xyz}"/>
      <limit lower="${lower_limit}" upper="${upper_limit}" effort="30" velocity="1"/>
    </joint>
  </xacro:macro>

  <!-- Torso (base link) -->
  <link name="torso">
    <visual>
      <origin xyz="0 0 ${torso_height/2}" rpy="0 0 0"/>
      <geometry>
        <box size="${torso_depth} ${torso_width} ${torso_height}"/>
      </geometry>
      <material name="gray"/>
    </visual>
    <collision>
      <origin xyz="0 0 ${torso_height/2}" rpy="0 0 0"/>
      <geometry>
        <box size="${torso_depth} ${torso_width} ${torso_height}"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 ${torso_height/2}" rpy="0 0 0"/>
      <mass value="10.0"/>
      <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0"/>
    </inertial>
  </link>

  <!-- Head -->
  <link name="head">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <sphere radius="${head_radius}"/>
      </geometry>
      <material name="white"/>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <sphere radius="${head_radius}"/>
      </geometry>
    </collision>
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="2.0"/>
      <inertia ixx="0.05" ixy="0.0" ixz="0.0" iyy="0.05" iyz="0.0" izz="0.05"/>
    </inertial>
  </link>

  <joint name="neck_joint" type="revolute">
    <parent link="torso"/>
    <child link="head"/>
    <origin xyz="0 0 ${torso_height}" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.5" upper="0.5" effort="100" velocity="1"/>
  </joint>

  <!-- Arms using the macro -->
  <xacro:limb name="arm" side="left" parent_link="torso"
              origin_xyz="${torso_depth/2} 0 ${torso_height*0.8}"
              axis_xyz="0 1 0" lower_limit="-1.57" upper_limit="1.57"/>

  <xacro:limb name="arm" side="right" parent_link="torso"
              origin_xyz="${-torso_depth/2} 0 ${torso_height*0.8}"
              axis_xyz="0 1 0" lower_limit="-1.57" upper_limit="1.57"/>

  <!-- Legs -->
  <xacro:macro name="leg" params="side parent_link origin_xyz axis_xyz hip_limit knee_limit ankle_limit">
    <!-- Thigh -->
    <link name="${side}_thigh">
      <visual>
        <origin xyz="0 0 -${upper_leg_length/2}" rpy="0 0 0"/>
        <geometry>
          <capsule radius="0.06" length="${upper_leg_length}"/>
        </geometry>
        <material name="${side}"/>
      </visual>
      <collision>
        <origin xyz="0 0 -${upper_leg_length/2}" rpy="0 0 0"/>
        <geometry>
          <capsule radius="0.06" length="${upper_leg_length}"/>
        </geometry>
      </collision>
      <inertial>
        <origin xyz="0 0 -${upper_leg_length/2}" rpy="0 0 0"/>
        <mass value="2.0"/>
        <inertia ixx="0.05" ixy="0.0" ixz="0.0" iyy="0.05" iyz="0.0" izz="0.05"/>
      </inertial>
    </link>

    <joint name="${side}_hip_joint" type="revolute">
      <parent link="${parent_link}"/>
      <child link="${side}_thigh"/>
      <origin xyz="${origin_xyz}" rpy="0 0 0"/>
      <axis xyz="0 1 0"/>
      <limit lower="${hip_limit}" upper="${-hip_limit}" effort="100" velocity="1"/>
    </joint>

    <!-- Shin -->
    <link name="${side}_shin">
      <visual>
        <origin xyz="0 0 -${lower_leg_length/2}" rpy="0 0 0"/>
        <geometry>
          <capsule radius="0.05" length="${lower_leg_length}"/>
        </geometry>
        <material name="${side}"/>
      </visual>
      <collision>
        <origin xyz="0 0 -${lower_leg_length/2}" rpy="0 0 0"/>
        <geometry>
          <capsule radius="0.05" length="${lower_leg_length}"/>
        </geometry>
      </collision>
      <inertial>
        <origin xyz="0 0 -${lower_leg_length/2}" rpy="0 0 0"/>
        <mass value="1.5"/>
        <inertia ixx="0.03" ixy="0.0" ixz="0.0" iyy="0.03" iyz="0.0" izz="0.03"/>
      </inertial>
    </link>

    <joint name="${side}_knee_joint" type="revolute">
      <parent link="${side}_thigh"/>
      <child link="${side}_shin"/>
      <origin xyz="0 0 -${upper_leg_length}" rpy="0 0 0"/>
      <axis xyz="0 1 0"/>
      <limit lower="${knee_limit}" upper="0.0" effort="80" velocity="1"/>
    </joint>

    <!-- Foot -->
    <link name="${side}_foot">
      <visual>
        <origin xyz="0 0 0" rpy="0 0 0"/>
        <geometry>
          <box size="${foot_size}"/>
        </geometry>
        <material name="black"/>
      </visual>
      <collision>
        <origin xyz="0 0 0" rpy="0 0 0"/>
        <geometry>
          <box size="${foot_size}"/>
        </geometry>
      </collision>
      <inertial>
        <origin xyz="0 0 0" rpy="0 0 0"/>
        <mass value="0.5"/>
        <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.001"/>
      </inertial>
    </link>

    <joint name="${side}_ankle_joint" type="revolute">
      <parent link="${side}_shin"/>
      <child link="${side}_foot"/>
      <origin xyz="0 0 -${lower_leg_length}" rpy="0 0 0"/>
      <axis xyz="0 1 0"/>
      <limit lower="${ankle_limit}" upper="${-ankle_limit}" effort="40" velocity="1"/>
    </joint>
  </xacro:macro>

  <!-- Create legs using the macro -->
  <xacro:leg side="left" parent_link="torso"
             origin_xyz="${torso_depth*0.3} 0 0"
             axis_xyz="0 1 0" hip_limit="-1.57" knee_limit="-1.57" ankle_limit="-0.5"/>

  <xacro:leg side="right" parent_link="torso"
             origin_xyz="${-torso_depth*0.3} 0 0"
             axis_xyz="0 1 0" hip_limit="-1.57" knee_limit="-1.57" ankle_limit="-0.5"/>

  <!-- Add ROS Control interface -->
  <ros2_control name="FakeSystem" type="system">
    <hardware>
      <plugin>fake_components/GenericSystem</plugin>
    </hardware>
    <joint name="neck_joint">
      <command_interface name="position"/>
      <state_interface name="position"/>
    </joint>
    <joint name="left_shoulder_joint">
      <command_interface name="position"/>
      <state_interface name="position"/>
    </joint>
    <joint name="left_elbow_joint">
      <command_interface name="position"/>
      <state_interface name="position"/>
    </joint>
    <joint name="right_shoulder_joint">
      <command_interface name="position"/>
      <state_interface name="position"/>
    </joint>
    <joint name="right_elbow_joint">
      <command_interface name="position"/>
      <state_interface name="position"/>
    </joint>
    <joint name="left_hip_joint">
      <command_interface name="position"/>
      <state_interface name="position"/>
    </joint>
    <joint name="left_knee_joint">
      <command_interface name="position"/>
      <state_interface name="position"/>
    </joint>
    <joint name="left_ankle_joint">
      <command_interface name="position"/>
      <state_interface name="position"/>
    </joint>
    <joint name="right_hip_joint">
      <command_interface name="position"/>
      <state_interface name="position"/>
    </joint>
    <joint name="right_knee_joint">
      <command_interface name="position"/>
      <state_interface name="position"/>
    </joint>
    <joint name="right_ankle_joint">
      <command_interface name="position"/>
      <state_interface name="position"/>
    </joint>
  </ros2_control>

</robot>
```

### Step 3: Create a Launch File to Visualize the Model

Create a launch file to load and visualize the humanoid model:

```bash
touch ~/ros2_labs/src/humanoid_models/launch/view_humanoid.launch.py
```

Add the following content:

```python
"""
File: view_humanoid.launch.py
Purpose: Launch file to visualize the humanoid robot model in RViz
Lab: Lab 5 - Building a Humanoid URDF Model
Dependencies: launch, launch_ros, xacro, robot_state_publisher, joint_state_publisher_gui
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """
    Generate the launch description for viewing the humanoid model.
    """
    # Declare launch arguments
    model_arg = DeclareLaunchArgument(
        'model',
        default_value='urdf/humanoid_model.xacro',
        description='URDF/SDF filename from the humanoid_models package'
    )

    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Whether to start RViz'
    )

    # Get launch configurations
    model = LaunchConfiguration('model')
    use_rviz = LaunchConfiguration('use_rviz')

    # Path to the robot description file
    robot_description_path = PathJoinSubstitution([
        FindPackageShare('humanoid_models'),
        model
    ])

    # Robot State Publisher node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_path.perform({}),
            'publish_frequency': 50.0
        }]
    )

    # Joint State Publisher GUI node
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    # RViz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', PathJoinSubstitution([
            FindPackageShare('humanoid_models'),
            'config',
            'view_robot.rviz'
        ])],
        condition=IfCondition(use_rviz)
    )

    return LaunchDescription([
        model_arg,
        use_rviz_arg,
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])
```

### Step 4: Create a Configuration File for RViz

Create the RViz configuration file:

```bash
mkdir -p ~/ros2_labs/src/humanoid_models/config
touch ~/ros2_labs/src/humanoid_models/config/view_robot.rviz
```

Add the following content to the RViz config file:

```yaml
Panels:
  - Class: rviz_common/Displays
    Name: Displays
  - Class: rviz_common/Views
    Name: Views

Visualization Manager:
  Displays:
    - Class: rviz_default_plugins/RobotModel
      Name: RobotModel
      Enabled: true
      Description: URDF Robot Model
      Topic:
        Name: /robot_description
      Update Interval: 0
      Alpha: 1
      Links:
        All Links Enabled: true
        Expand Joint Details: false
        Expand Link Details: false
        Expand Tree: false
        Link Tree Style: Links in Alphabetic Order
        head:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        left_ankle:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        left_elbow:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        left_foot:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        left_hand:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        left_hip:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        left_knee:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        left_shin:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        left_shoulder:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        left_thigh:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        left_upper_arm:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        neck:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        pelvis:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        right_ankle:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        right_elbow:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        right_foot:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        right_hand:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        right_hip:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        right_knee:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        right_shin:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        right_shoulder:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        right_thigh:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        right_upper_arm:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        spine:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        torso:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
      Mass Properties:
        Inertia: false
        Mass: false
      TF Prefix: ""
      Update Interval: 0
      Value: true
    - Class: rviz_default_plugins/Grid
      Name: Grid
      Enabled: true
      Alpha: 0.5
      Cell Size: 1
      Color: 160; 160; 164
      Line Style:
        Line Width: 0.029999999329447746
        Value: Lines
      Normal Cell Count: 0
      Offset:
        X: 0
        Y: 0
        Z: 0
      Plane: XY
      Plane Cell Count: 10
      Reference Frame: <Fixed Frame>
      Value: true
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Name: Current View
      Target Frame: torso
      Value: Orbit (rviz)
      Distance: 3.0
      Pitch: 0.5
      Yaw: 0.5
</yaml>

### Step 5: Create a Python Script for Testing Kinematics

Create a Python script to test the kinematic properties of the humanoid model:

```bash
touch ~/ros2_labs/src/humanoid_models/humanoid_models/kinematics_tester.py
```

Add the following content:

```python
#!/usr/bin/env python3
"""
File: kinematics_tester.py
Purpose: Test kinematic properties of the humanoid model
Lab: Lab 5 - Building a Humanoid URDF Model
Dependencies: rclpy, moveit_core, kdl_parser
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import math
import time


class KinematicsTester(Node):
    """
    Tests kinematic properties of the humanoid model.
    This node demonstrates how to work with joint states and kinematic chains.
    """

    def __init__(self):
        super().__init__('kinematics_tester')

        # Publisher for joint states
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)

        # Timer to publish joint states
        self.timer = self.create_timer(0.1, self.publish_joint_states)

        # Initialize joint positions for testing
        self.joint_positions = {
            'neck_joint': 0.0,
            'left_shoulder_joint': 0.0,
            'left_elbow_joint': 0.0,
            'right_shoulder_joint': 0.0,
            'right_elbow_joint': 0.0,
            'left_hip_joint': 0.0,
            'left_knee_joint': 0.0,
            'left_ankle_joint': 0.0,
            'right_hip_joint': 0.0,
            'right_knee_joint': 0.0,
            'right_ankle_joint': 0.0
        }

        self.test_counter = 0
        self.get_logger().info('Kinematics Tester node initialized')

    def publish_joint_states(self):
        """
        Publish joint states for the humanoid model.
        """
        msg = JointState()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'torso'

        # Add joint names
        msg.name = list(self.joint_positions.keys())

        # Update joint positions in a wave pattern for visualization
        self.update_joint_positions()

        # Add joint positions
        msg.position = list(self.joint_positions.values())

        # Publish the message
        self.joint_pub.publish(msg)

    def update_joint_positions(self):
        """
        Update joint positions for visualization.
        Creates a wave-like motion to test the model.
        """
        t = time.time()

        # Create coordinated movements for different limbs
        self.joint_positions['neck_joint'] = 0.3 * math.sin(0.5 * t)

        # Left arm movement
        self.joint_positions['left_shoulder_joint'] = 0.5 * math.sin(0.3 * t)
        self.joint_positions['left_elbow_joint'] = 0.3 * math.sin(0.3 * t + 0.5)

        # Right arm movement
        self.joint_positions['right_shoulder_joint'] = 0.5 * math.sin(0.3 * t + math.pi)
        self.joint_positions['right_elbow_joint'] = 0.3 * math.sin(0.3 * t + 0.5 + math.pi)

        # Left leg movement
        self.joint_positions['left_hip_joint'] = 0.3 * math.sin(0.2 * t)
        self.joint_positions['left_knee_joint'] = 0.2 * math.sin(0.2 * t + 0.3)
        self.joint_positions['left_ankle_joint'] = 0.1 * math.sin(0.2 * t + 0.6)

        # Right leg movement
        self.joint_positions['right_hip_joint'] = 0.3 * math.sin(0.2 * t + math.pi)
        self.joint_positions['right_knee_joint'] = 0.2 * math.sin(0.2 * t + 0.3 + math.pi)
        self.joint_positions['right_ankle_joint'] = 0.1 * math.sin(0.2 * t + 0.6 + math.pi)


def main(args=None):
    """
    Main function for the kinematics tester node.
    """
    rclpy.init(args=args)

    kinematics_tester = KinematicsTester()

    try:
        rclpy.spin(kinematics_tester)
    except KeyboardInterrupt:
        print('Kinematics tester interrupted by user')
    finally:
        kinematics_tester.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Step 6: Update the Package Configuration

Update the package.xml file:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>humanoid_models</name>
  <version>0.0.0</version>
  <description>Humanoid robot models for Lab 5</description>
  <maintainer email="student@todo.todo">student</maintainer>
  <license>Apache License 2.0</license>

  <exec_depend>rclpy</exec_depend>
  <exec_depend>std_msgs</exec_depend>
  <exec_depend>sensor_msgs</exec_depend>
  <exec_depend>geometry_msgs</exec_depend>
  <exec_depend>robot_state_publisher</exec_depend>
  <exec_depend>joint_state_publisher_gui</exec_depend>
  <exec_depend>xacro</exec_depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

And update the setup.py file:

```python
from setuptools import setup

package_name = 'humanoid_models'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include URDF files
        ('share/' + package_name + '/urdf', [
            'urdf/basic_humanoid.urdf',
            'urdf/humanoid_model.xacro'
        ]),
        # Include launch files
        ('share/' + package_name + '/launch', [
            'launch/view_humanoid.launch.py'
        ]),
        # Include config files
        ('share/' + package_name + '/config', [
            'config/view_robot.rviz'
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='student@todo.todo',
    description='Humanoid robot models for Lab 5',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'kinematics_tester = humanoid_models.kinematics_tester:main',
        ],
    },
)
```

### Step 7: Make Files Executable and Build

Make the Python files executable:

```bash
chmod +x ~/ros2_labs/src/humanoid_models/humanoid_models/kinematics_tester.py
```

Now let me update the tasks file to mark T044 as completed:
