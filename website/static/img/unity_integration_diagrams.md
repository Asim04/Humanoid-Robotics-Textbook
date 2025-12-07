# Unity Integration Diagrams

This document describes the Unity integration diagrams for Chapter 8 of the Physical AI & Humanoid Robotics textbook. These diagrams illustrate the architecture and data flow for Unity-ROS2 integration.

## 1. Unity-ROS2 Architecture Overview

```
┌─────────────────┐    TCP/IP     ┌──────────────────┐
│   Unity 3D      │ ◄───────────► │    ROS2 Nodes    │
│   Application   │   Messages    │                  │
│                 │               │ ┌───────────────┐ │
│ ┌─────────────┐ │               │ │ Robot Control │ │
│ │ Robot Model │ │               │ │    Nodes      │ │
│ └─────────────┘ │               │ └───────────────┘ │
│                 │               │ ┌───────────────┐ │
│ ┌─────────────┐ │               │ │  Sensor Data  │ │
│ │  Sensors    │ │               │ │   Processors  │ │
│ │  (LiDAR,    │ │               │ └───────────────┘ │
│ │  Camera,    │ │               │ ┌───────────────┐ │
│ │  IMU)       │ │               │ │ Visualization │ │
│ └─────────────┘ │               │ │    Tools      │ │
│                 │               │ └───────────────┘ │
│ ┌─────────────┐ │               └──────────────────┘
│ │  UI/UX      │ │
│ │ Dashboard   │ │
│ └─────────────┘ │
└─────────────────┘
```

This diagram shows the high-level architecture of the Unity-ROS2 integration, with bidirectional communication between the Unity application and ROS2 nodes.

## 2. Data Flow Architecture

```
ROS2 Topics ──────┐
                  │
┌─────────┐       ▼      ┌──────────────┐      ┌─────────────┐
│ Robot   │ ──► /cmd_vel │ ROS2 Bridge  │ ──►  │ Unity       │
│ Control │              │ (Python)     │      │ Application │
│ Nodes   │ ◄── /odom    └──────────────┘      │             │
└─────────┘                │                   │ ┌─────────┐ │
                           │                   │ │ Robot   │ │
┌─────────────┐            │                   │ │ Model   │ │
│ Perception  │ ◄── /scan  │                   │ │ (3D)    │ │
│ Nodes       │            │                   │ └─────────┘ │
└─────────────┘            │                   │      │      │
                           ▼                   │      ▼      │
┌─────────────┐      ┌──────────────┐          │ ┌─────────┐ │
│ Planning &  │ ◄──► │ Unity Bridge │ ◄───────┼─│ Sensors │ │
│ Navigation  │      │ (C# Scripts) │          │ │ (LiDAR, │ │
│ Nodes       │ ────►└──────────────┘          │ │ Camera, │ │
└─────────────┘                                 │ │ IMU)    │ │
                                              │ └─────────┘ │
                                              │      │      │
                                              │      ▼      │
                                              │ ┌─────────┐ │
                                              │ │ UI/UX   │ │
                                              │ │ Dashboard│ │
                                              │ └─────────┘ │
                                              └─────────────┘
```

This diagram illustrates the data flow between ROS2 nodes and Unity, showing how sensor data flows from ROS2 to Unity for visualization, and how control commands flow from Unity to ROS2 for robot control.

## 3. Unity Scene Hierarchy for Robot Visualization

```
Unity Scene Root
├── Robot_Base (Rigidbody)
│   ├── Chassis_Mesh (Visual)
│   ├── LiDAR_Sensor (LaserScan Visualizer)
│   ├── Camera_Sensor (Image Visualizer)
│   ├── IMU_Indicator (Orientation Visualizer)
│   ├── Wheel_Left (Hinge Joint)
│   │   └── Wheel_Left_Mesh
│   ├── Wheel_Right (Hinge Joint)
│   │   └── Wheel_Right_Mesh
│   └── Joint_Animators (Animation Controller)
├── Environment
│   ├── Ground_Plane
│   ├── Obstacles
│   └── Lighting
├── UI_Canvas
│   ├── Robot_Status_Panel
│   ├── Sensor_Data_Panel
│   └── Control_Panel
└── ROS2_Bridge_Manager
    ├── UnityROS2Bridge (C# Script)
    ├── SensorVisualization (C# Script)
    ├── RobotAnimationController (C# Script)
    └── UIDashboard (C# Script)
```

This diagram shows the typical Unity scene hierarchy for robot visualization, including the robot model, sensors, UI elements, and bridge components.

## 4. Message Routing Schema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ROS2 Node     │    │  ROS2 Bridge    │    │  Unity App      │
│   (C++)         │    │  (Python)       │    │  (C#)           │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ Publish:        │───►│ Receive:        │───►│ Subscribe:      │
│ /scan (LaserScan)│   │ /scan (LaserScan)│   │ /scan (LaserScan)│
│ /odom (Odometry) │   │ /odom (Odometry) │   │ /odom (Odometry) │
│ /imu (Imu)      │   │ /imu (Imu)      │   │ /imu (Imu)      │
│ /joint_states   │   │ /joint_states   │   │ /joint_states   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ROS2 Node     │◄───│  ROS2 Bridge    │◄───│  Unity App      │
│   (C++)         │    │  (Python)       │    │  (C#)           │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ Subscribe:      │◄───│ Publish:        │◄───│ Publish:        │
│ /cmd_vel (Twist)│    │ /cmd_vel (Twist)│    │ /cmd_vel (Twist)│
│ /move_base/goal │    │ /move_base/goal │    │ /move_base/goal │
│ /set_pose       │    │ /set_pose       │    │ /set_pose       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

This diagram shows the bidirectional message routing between ROS2 and Unity, illustrating how messages are published and subscribed on both sides.

## 5. Sensor Data Processing Pipeline

```
Physical Robot Sensors
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ROS2 Drivers  │───►│ Unity Bridge    │───►│ Unity Sensor    │
│   (Hardware)    │    │  (Python/C#)    │    │  Visualizers    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ LaserScan Data  │───►│ TCP/IP Socket   │───►│ LiDAR Points    │
│ (ranges array)  │    │ JSON Messages   │    │ (3D Points)     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ IMU Data        │───►│ Data Parsing    │───►│ Orientation     │
│ (orientation,   │    │ & Validation    │    │ (Quaternion)    │
│ angular_vel,    │    │                 │    │ Arrow/Indicator │
│ linear_acc)     │    │                 │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ Camera Data     │───►│ Frame Buffer    │───►│ Image Texture   │
│ (image_raw)     │    │ Transfer        │    │ (Real-time)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

This diagram shows the complete sensor data processing pipeline from physical sensors to visual representation in Unity.

## 6. Performance Optimization Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Unity Application                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Robot      │  │  Sensor     │  │  UI         │             │
│  │  Model      │  │  Data       │  │  System     │             │
│  │  (LOD)      │  │  (Throttle) │  │  (Canvas)   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│         │                 │                   │                │
│         ▼                 ▼                   ▼                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           Unity Bridge Scripts                        │   │
│  │  ┌─────────────────┐ ┌─────────────────┐             │   │
│  │  │ Animation       │ │ Visualization   │             │   │
│  │  │ Controller      │ │ Optimizer       │             │   │
│  │  │ (Smooth Interp) │ │ (Point Culling) │             │   │
│  │  └─────────────────┘ └─────────────────┘             │   │
│  │         │                   │                        │   │
│  │         ▼                   ▼                        │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │           ROS2 Interface                        │ │   │
│  │  │  ┌─────────────────┐ ┌─────────────────┐       │ │   │
│  │  │  │ Message         │ │ Rate Limiter    │       │ │   │
│  │  │  │ Throttler       │ │ (Update Rates)  │       │ │   │
│  │  │  └─────────────────┘ └─────────────────┘       │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

This diagram shows the performance optimization strategies for Unity-ROS2 integration, including level of detail (LOD), message throttling, and visualization optimization techniques.

## File Organization

The diagrams above would be implemented as visual assets in the following structure:

```
website/static/img/
├── unity_integration/
│   ├── architecture_overview.png
│   ├── data_flow.png
│   ├── scene_hierarchy.png
│   ├── message_routing.png
│   ├── sensor_pipeline.png
│   └── performance_optimization.png
└── unity_ros2_bridge_schema.png
```

These diagrams would visually represent the key concepts and architectures discussed in Chapter 8, providing students with clear visual references for understanding Unity-ROS2 integration.