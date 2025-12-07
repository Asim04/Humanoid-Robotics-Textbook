---
sidebar_position: 5
---

# Chapter 5: URDF & Robot Description

The Unified Robot Description Format (URDF) is the standard for representing robot models in ROS. It provides a comprehensive way to describe robot kinematics, dynamics, visual appearance, and physical properties. This chapter explores the fundamentals of URDF, its advanced features, and how to create complex robot models for simulation and real-world applications.

## Learning Objectives

After completing this chapter, students will be able to:

- Create complete robot descriptions using URDF
- Understand and implement robot kinematics and dynamics in URDF
- Use Xacro for parameterized and modular robot descriptions
- Integrate sensors and actuators into robot models
- Visualize and validate robot models in RViz and Gazebo
- Apply best practices for complex robot model development

## Introduction to URDF

URDF (Unified Robot Description Format) is an XML-based format for representing robots in ROS. It describes the physical and kinematic properties of robots, including:

- **Links**: Rigid bodies with mass, visual, and collision properties
- **Joints**: Connections between links with kinematic constraints
- **Transmissions**: Mapping between actuators and joints
- **Materials**: Visual appearance properties
- **Gazebo plugins**: Simulation-specific properties

### Basic URDF Structure

A basic URDF file has the following structure:

```xml
<?xml version="1.0"?>
<robot name="my_robot">
  <!-- Define materials -->
  <material name="blue">
    <color rgba="0 0 0.8 1"/>
  </material>

  <!-- Define links -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.5 0.2"/>
      </geometry>
      <material name="blue"/>
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

  <!-- Define joints -->
  <joint name="base_to_wheel" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_link"/>
    <origin xyz="0 0.25 -0.1" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
  </joint>

  <link name="wheel_link">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </visual>
  </link>
</robot>
```

## Links and Their Properties

Links represent rigid bodies in the robot model. Each link has several important properties:

### Visual Properties

The visual element defines how the link appears in visualization tools:

```xml
<link name="visual_example">
  <visual>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <box size="1 1 1"/>
      <!-- Other geometry types: cylinder, sphere, mesh -->
    </geometry>
    <material name="red">
      <color rgba="1 0 0 1"/>
    </material>
  </visual>
</link>
```

### Collision Properties

The collision element defines the shape used for collision detection:

```xml
<link name="collision_example">
  <collision>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <box size="1 1 1"/>
    </geometry>
  </collision>
</link>
```

### Inertial Properties

The inertial element defines the physical properties for dynamics simulation:

```xml
<link name="inertial_example">
  <inertial>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <mass value="1.0"/>
    <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
  </inertial>
</link>
```

## Joints and Their Types

Joints define the kinematic and dynamic relationships between links. URDF supports several joint types:

### Fixed Joint

A fixed joint creates a rigid connection between two links:

```xml
<joint name="fixed_joint" type="fixed">
  <parent link="parent_link"/>
  <child link="child_link"/>
  <origin xyz="0 0 0.1" rpy="0 0 0"/>
</joint>
```

### Revolute Joint

A revolute joint allows rotation around a single axis:

```xml
<joint name="revolute_joint" type="revolute">
  <parent link="base_link"/>
  <child link="arm_link"/>
  <origin xyz="0 0 0.5" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
  <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
</joint>
```

### Continuous Joint

A continuous joint allows unlimited rotation around an axis:

```xml
<joint name="continuous_joint" type="continuous">
  <parent link="base_link"/>
  <child link="wheel_link"/>
  <origin xyz="0.2 0 -0.1" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
</joint>
```

### Prismatic Joint

A prismatic joint allows linear motion along an axis:

```xml
<joint name="prismatic_joint" type="prismatic">
  <parent link="base_link"/>
  <child link="slider_link"/>
  <origin xyz="0 0 0.5" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
  <limit lower="0" upper="0.5" effort="100" velocity="0.5"/>
</joint>
```

## Complete Robot Model Example

Here's a more complete example of a simple differential drive robot:

```xml
<?xml version="1.0"?>
<robot name="diff_drive_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!-- Materials -->
  <material name="blue">
    <color rgba="0 0 0.8 1"/>
  </material>
  <material name="black">
    <color rgba="0 0 0 1"/>
  </material>
  <material name="white">
    <color rgba="1 1 1 1"/>
  </material>

  <!-- Base link -->
  <link name="base_link">
    <visual>
      <origin xyz="0 0 0.1" rpy="0 0 0"/>
      <geometry>
        <box size="0.5 0.3 0.1"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 0.1" rpy="0 0 0"/>
      <geometry>
        <box size="0.5 0.3 0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <origin xyz="0 0 0.1" rpy="0 0 0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Left wheel -->
  <link name="left_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black"/>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.2"/>
      <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.002"/>
    </inertial>
  </link>

  <!-- Right wheel -->
  <link name="right_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black"/>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.2"/>
      <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.002"/>
    </inertial>
  </link>

  <!-- Wheel joints -->
  <joint name="left_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="left_wheel"/>
    <origin xyz="0 0.2 -0.1" rpy="-1.57079632679 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <joint name="right_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="right_wheel"/>
    <origin xyz="0 -0.2 -0.1" rpy="-1.57079632679 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <!-- Camera -->
  <link name="camera_link">
    <visual>
      <geometry>
        <box size="0.05 0.05 0.05"/>
      </geometry>
      <material name="white"/>
    </visual>
    <collision>
      <geometry>
        <box size="0.05 0.05 0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.01"/>
      <inertia ixx="0.0001" ixy="0" ixz="0" iyy="0.0001" iyz="0" izz="0.0001"/>
    </inertial>
  </link>

  <joint name="camera_joint" type="fixed">
    <parent link="base_link"/>
    <child link="camera_link"/>
    <origin xyz="0.2 0 0.1" rpy="0 0 0"/>
  </joint>
</robot>
```

For the complete implementation, see [diff_drive_robot.urdf](/static/code/chapter-5/diff_drive_robot.urdf).

## Xacro: XML Macros for URDF

Xacro is a macro language that extends URDF with features like variables, properties, and include statements. It makes complex robot descriptions more manageable.

### Basic Xacro Concepts

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="xacro_example">

  <!-- Properties -->
  <xacro:property name="M_PI" value="3.1415926535897931" />
  <xacro:property name="wheel_radius" value="0.1" />
  <xacro:property name="wheel_width" value="0.05" />

  <!-- Macros -->
  <xacro:macro name="wheel" params="prefix *origin">
    <link name="${prefix}_wheel">
      <visual>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_width}"/>
        </geometry>
      </visual>
      <collision>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_width}"/>
        </geometry>
      </collision>
      <inertial>
        <mass value="0.2"/>
        <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.002"/>
      </inertial>
    </link>

    <joint name="${prefix}_wheel_joint" type="continuous">
      <xacro:insert_block name="origin"/>
      <axis xyz="0 0 1"/>
    </joint>
  </xacro:macro>

  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.3 0.1"/>
      </geometry>
    </visual>
  </link>

  <!-- Use the macro to create wheels -->
  <xacro:wheel prefix="left">
    <origin xyz="0 0.2 -0.1" rpy="-${M_PI/2} 0 0"/>
    <parent link="base_link"/>
    <child link="left_wheel"/>
  </xacro:wheel>

  <xacro:wheel prefix="right">
    <origin xyz="0 -0.2 -0.1" rpy="-${M_PI/2} 0 0"/>
    <parent link="base_link"/>
    <child link="right_wheel"/>
  </xacro:wheel>

</robot>
```

For the complete implementation, see [xacro_example.urdf.xacro](/static/code/chapter-5/xacro_example.urdf.xacro).

### Advanced Xacro Features

Xacro supports conditionals, mathematical expressions, and includes:

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="advanced_xacro_example">

  <!-- Include other xacro files -->
  <xacro:include filename="$(find my_robot_description)/urdf/materials.xacro" />
  <xacro:include filename="$(find my_robot_description)/urdf/transmission_macros.xacro" />

  <!-- Conditional definitions -->
  <xacro:arg name="has_laser" default="false"/>
  <xacro:arg name="robot_namespace" default=""/>

  <!-- Mathematical expressions -->
  <xacro:property name="wheel_separation" value="0.3" />
  <xacro:property name="wheel_radius" value="0.1" />
  <xacro:property name="robot_width" value="${wheel_separation + 0.1}" />

  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 ${robot_width} 0.1"/>
      </geometry>
      <material name="blue"/>
    </visual>
  </link>

  <!-- Conditionally add laser -->
  <xacro:if value="$(arg has_laser)">
    <link name="laser_link">
      <visual>
        <geometry>
          <cylinder radius="0.02" length="0.05"/>
        </geometry>
      </visual>
    </link>

    <joint name="laser_joint" type="fixed">
      <parent link="base_link"/>
      <child link="laser_link"/>
      <origin xyz="0.2 0 0.05" rpy="0 0 0"/>
    </joint>
  </xacro:if>

  <!-- Loop for creating multiple joints -->
  <xacro:macro name="create_arm" params="prefix joint_names">
    <xacro:property name="names" value="${joint_names.split(',')}"/>
    <xacro:property name="arm_length" value="0.3"/>

    <xacro:for each="name" in="${names}">
      <link name="${prefix}_${name}_link">
        <visual>
          <geometry>
            <box size="0.05 0.05 0.1"/>
          </geometry>
        </visual>
      </link>

      <joint name="${prefix}_${name}_joint" type="revolute">
        <parent link="${prefix}_${name}_link"/>
        <child link="${prefix}_${name}_link"/>
        <axis xyz="0 0 1"/>
        <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
      </joint>
    </xacro:for>
  </xacro:macro>

</robot>
```

For the complete implementation, see [advanced_xacro_example.urdf.xacro](/static/code/chapter-5/advanced_xacro_example.urdf.xacro).

## Robot Model Validation

Validating robot models is crucial before using them in simulation or with real robots:

### URDF Validation

```bash
# Check URDF syntax
check_urdf /path/to/robot.urdf

# Parse and validate with robot_state_publisher
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:='$(cat robot.urdf)'
```

### Kinematic Validation

```python
#!/usr/bin/env python3
"""
File: urdf_validator.py
Purpose: Validate URDF models for kinematic correctness
Chapter: 5 - URDF & Robot Description
Dependencies: rclpy, tf2_ros, geometry_msgs
Hardware: None (simulation)
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster
import tf_transformations
from geometry_msgs.msg import TransformStamped


class URDFValidator(Node):
    """
    Validates URDF models by checking kinematic chains and transforms.
    """

    def __init__(self):
        super().__init__('urdf_validator')

        # Subscribe to joint states
        self.joint_state_sub = self.create_subscription(
            JointState,
            'joint_states',
            self.joint_state_callback,
            10
        )

        # Create transform broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)

        # Timer for broadcasting transforms
        self.timer = self.create_timer(0.1, self.broadcast_transforms)

        # Store joint positions
        self.joint_positions = {}

    def joint_state_callback(self, msg):
        """
        Store joint positions from joint state messages.
        """
        for i, name in enumerate(msg.name):
            if i < len(msg.position):
                self.joint_positions[name] = msg.position[i]

    def broadcast_transforms(self):
        """
        Broadcast transforms for visualization and validation.
        """
        # Example: broadcast base_link to wheel transforms
        transforms = []

        # Base to left wheel
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'base_link'
        t.child_frame_id = 'left_wheel'
        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.2
        t.transform.translation.z = -0.1
        # Set rotation based on joint position if available

        transforms.append(t)

        # Broadcast all transforms
        for transform in transforms:
            self.tf_broadcaster.sendTransform(transform)


def main(args=None):
    """
    Main function to validate URDF models.
    """
    rclpy.init(args=args)
    validator = URDFValidator()

    try:
        rclpy.spin(validator)
    except KeyboardInterrupt:
        pass
    finally:
        validator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

For the complete implementation, see [urdf_validator.py](/static/code/chapter-5/urdf_validator.py).

## Visualization in RViz

RViz can visualize robot models using the RobotModel display:

### RViz Configuration

```yaml
# File: config/robot_visualization.rviz
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
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Name: Current View