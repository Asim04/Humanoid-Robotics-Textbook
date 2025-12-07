---
sidebar_position: 4
---

# Lab 4: Multi-Node Communication System

## Objective

In this lab, you will build a more complex ROS 2 system consisting of multiple interconnected nodes that communicate through various communication patterns (topics, services, actions). You'll learn how to design and implement distributed robotic systems with proper communication architecture, error handling, and system integration.

## Learning Outcomes

After completing this lab, you will be able to:

- Design and implement multi-node robotic systems
- Use different ROS 2 communication patterns effectively
- Create and use custom message, service, and action types
- Implement proper error handling and system monitoring
- Use launch files to coordinate complex multi-node systems
- Debug and troubleshoot communication issues in distributed systems

## Prerequisites

- Lab 3 completed (basic ROS 2 node development)
- ROS 2 Humble Hawksbill installed
- Python 3.8+ environment
- Understanding of ROS 2 communication patterns
- Basic knowledge of custom message types

## System Overview

For this lab, we'll create a "Robot Control System" with the following nodes:

1. **Navigation Node**: Handles path planning and navigation goals
2. **Sensor Fusion Node**: Integrates data from multiple sensors
3. **Control Node**: Controls robot actuators based on commands
4. **Monitoring Node**: Monitors system health and status
5. **Interface Node**: Provides external interface for commanding the robot

## Setup and Environment

### 1. Create a New Package

First, create a new package for our multi-node system:

```bash
cd ~/ros2_labs/src
ros2 pkg create --build-type ament_python robot_control_system
```

### 2. Create Directories

Create the necessary directories for our system:

```bash
mkdir -p ~/ros2_labs/src/robot_control_system/robot_control_system/{msgs,srvs,actions}
mkdir -p ~/ros2_labs/src/robot_control_system/launch
mkdir -p ~/ros2_labs/src/robot_control_system/config
```

## Implementation Steps

### Step 1: Define Custom Message Types

Create custom messages for our robot control system.

**RobotPose.msg** - Represents robot position and orientation:

```bash
# Create the message file
cat > ~/ros2_labs/src/robot_control_system/robot_control_system/msgs/RobotPose.msg << 'EOF'
# Robot pose with position and orientation
float64 x
float64 y
float64 theta
float64 linear_velocity
float64 angular_velocity
uint8[] status_flags
string robot_name
---
# Additional fields can be added as needed
EOF
```

**RobotStatus.msg** - Represents robot status information:

```bash
# Create the status message file
cat > ~/ros2_labs/src/robot_control_system/robot_control_system/msgs/RobotStatus.msg << 'EOF'
# Robot status information
string status
float64 battery_level
bool is_connected
bool is_moving
bool has_error
float64[] joint_positions
float64[] joint_velocities
string error_message
builtin_interfaces/Time timestamp
---
# Status constants
uint8 STATUS_IDLE = 0
uint8 STATUS_MOVING = 1
uint8 STATUS_ERROR = 2
uint8 STATUS_CHARGING = 3
EOF
```

### Step 2: Define Custom Service Types

**NavigateTo.srv** - Service for requesting navigation to a specific location:

```bash
# Create the service file
cat > ~/ros2_labs/src/robot_control_system/robot_control_system/srvs/NavigateTo.srv << 'EOF'
# Request fields
float64 target_x
float64 target_y
float64 target_theta
string navigation_mode
---
# Response fields
bool success
string message
float64 estimated_time
string route_id
EOF
```

### Step 3: Define Custom Action Types

**MoveToGoal.action** - Action for moving robot to a goal with feedback:

```bash
# Create the action file
cat > ~/ros2_labs/src/robot_control_system/robot_control_system/actions/MoveToGoal.action << 'EOF'
# Goal definition
float64 target_x
float64 target_y
float64 target_theta
float64 tolerance
---
# Result definition
bool success
string message
float64 distance_traveled
float64 time_taken
---
# Feedback definition
float64 current_x
float64 current_y
float64 current_theta
float64 distance_to_goal
float64 progress_percentage
string status
EOF
```

### Step 4: Update package.xml

Update the package.xml file to include dependencies and message generation:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>robot_control_system</name>
  <version>0.0.0</version>
  <description>Multi-node robot control system for Lab 4</description>
  <maintainer email="student@todo.todo">student</maintainer>
  <license>Apache License 2.0</license>

  <exec_depend>rclpy</exec_depend>
  <exec_depend>std_msgs</exec_depend>
  <exec_depend>geometry_msgs</exec_depend>
  <exec_depend>sensor_msgs</exec_depend>
  <exec_depend>builtin_interfaces</exec_depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

### Step 5: Create the Navigation Node

Create the navigation node that handles path planning and navigation requests:

```bash
touch ~/ros2_labs/src/robot_control_system/robot_control_system/navigation_node.py
```

Add the following content:

```python
#!/usr/bin/env python3
"""
File: navigation_node.py
Purpose: Navigation node that handles path planning and goal execution
Lab: Lab 4 - Multi-Node Communication System
Dependencies: rclpy, geometry_msgs, custom messages
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import math
import threading
from rcl_interfaces.msg import ParameterDescriptor


class NavigationNode(Node):
    """
    Navigation node that handles path planning and goal execution.
    Implements both service-based navigation and action-based navigation.
    """

    def __init__(self):
        super().__init__('navigation_node')

        # State variables
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_theta = 0.0
        self.is_navigating = False
        self.navigation_thread = None

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.status_pub = self.create_publisher(String, 'navigation_status', 10)

        # Subscribers
        self.odom_sub = self.create_subscription(
            String,  # Using String for simplicity; in real systems, use Odometry
            'robot_pose',
            self.odom_callback,
            10
        )

        # Timers
        self.nav_timer = self.create_timer(0.1, self.navigation_callback)

        # Declare parameters
        self.declare_parameter('linear_speed', 0.5,
                              ParameterDescriptor(description='Linear speed for navigation'))
        self.declare_parameter('angular_speed', 0.5,
                              ParameterDescriptor(description='Angular speed for navigation'))
        self.declare_parameter('tolerance', 0.1,
                              ParameterDescriptor(description='Position tolerance'))

        self.get_logger().info('Navigation node initialized')

    def odom_callback(self, msg):
        """
        Callback for robot odometry/pose updates.
        """
        # In a real system, this would parse actual pose data
        # For this lab, we'll just log the update
        self.get_logger().debug(f'Received pose update: {msg.data}')

    def navigation_callback(self):
        """
        Main navigation callback that executes navigation if active.
        """
        if self.is_navigating:
            # Navigation logic would go here
            cmd_msg = Twist()
            cmd_msg.linear.x = 0.0  # Placeholder - would implement actual navigation
            cmd_msg.angular.z = 0.0
            self.cmd_vel_pub.publish(cmd_msg)

    def start_navigation(self, target_x, target_y, target_theta):
        """
        Start navigation to target position.
        """
        self.get_logger().info(f'Starting navigation to ({target_x}, {target_y}, {target_theta})')
        self.is_navigating = True
        # In a real system, this would implement path planning and execution

    def stop_navigation(self):
        """
        Stop current navigation.
        """
        self.get_logger().info('Stopping navigation')
        self.is_navigating = False
        # Publish zero velocity to stop the robot
        cmd_msg = Twist()
        cmd_msg.linear.x = 0.0
        cmd_msg.angular.z = 0.0
        self.cmd_vel_pub.publish(cmd_msg)


def main(args=None):
    """
    Main function for the navigation node.
    """
    rclpy.init(args=args)

    navigation_node = NavigationNode()

    try:
        rclpy.spin(navigation_node)
    except KeyboardInterrupt:
        print('Navigation node interrupted by user')
    finally:
        navigation_node.stop_navigation()
        navigation_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Step 6: Create the Sensor Fusion Node

Create the sensor fusion node that integrates data from multiple sensors:

```bash
touch ~/ros2_labs/src/robot_control_system/robot_control_system/sensor_fusion_node.py
```

Add the following content:

```python
#!/usr/bin/env python3
"""
File: sensor_fusion_node.py
Purpose: Sensor fusion node that integrates data from multiple sensors
Lab: Lab 4 - Multi-Node Communication System
Dependencies: rclpy, sensor_msgs, geometry_msgs, custom messages
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Imu
from geometry_msgs.msg import Vector3
from std_msgs.msg import Float32, Bool
import numpy as np
from collections import deque


class SensorFusionNode(Node):
    """
    Sensor fusion node that integrates data from multiple sensors.
    Processes laser, IMU, and other sensor data to create a unified perception.
    """

    def __init__(self):
        super().__init__('sensor_fusion_node')

        # Sensor data storage
        self.laser_data = None
        self.imu_data = None
        self.sonar_data = None

        # Sensor history for filtering
        self.imu_history = deque(maxlen=10)

        # Publishers
        self.fused_pose_pub = self.create_publisher(Float32, 'fused_pose', 10)
        self.obstacle_detected_pub = self.create_publisher(Bool, 'obstacle_detected', 10)
        self.fused_imu_pub = self.create_publisher(Vector3, 'fused_imu', 10)

        # Subscribers
        self.laser_sub = self.create_subscription(
            LaserScan,
            'scan',
            self.laser_callback,
            10
        )

        self.imu_sub = self.create_subscription(
            Imu,
            'imu/data',
            self.imu_callback,
            10
        )

        self.sonar_sub = self.create_subscription(
            Float32,
            'sonar/range',
            self.sonar_callback,
            10
        )

        # Timer for fusion processing
        self.fusion_timer = self.create_timer(0.05, self.fusion_callback)

        self.get_logger().info('Sensor fusion node initialized')

    def laser_callback(self, msg):
        """
        Callback for laser scan data.
        """
        self.laser_data = msg
        self.process_laser_data(msg)

    def imu_callback(self, msg):
        """
        Callback for IMU data.
        """
        self.imu_data = msg
        # Add to history for filtering
        self.imu_history.append({
            'linear_acceleration': msg.linear_acceleration,
            'angular_velocity': msg.angular_velocity,
            'orientation': msg.orientation
        })
        self.process_imu_data(msg)

    def sonar_callback(self, msg):
        """
        Callback for sonar range data.
        """
        self.sonar_data = msg
        self.process_sonar_data(msg)

    def process_laser_data(self, msg):
        """
        Process laser scan data to detect obstacles.
        """
        if len(msg.ranges) == 0:
            return

        # Find minimum distance in front of robot (±30 degrees)
        front_ranges = msg.ranges[int(len(msg.ranges)*0.33):int(len(msg.ranges)*0.66)]
        min_distance = min([r for r in front_ranges if r != float('inf') and r > 0], default=float('inf'))

        # Publish obstacle detection
        obstacle_msg = Bool()
        obstacle_msg.data = min_distance < 1.0  # Obstacle within 1 meter
        self.obstacle_detected_pub.publish(obstacle_msg)

        if min_distance < 1.0:
            self.get_logger().warn(f'Obstacle detected at {min_distance:.2f}m')

    def process_imu_data(self, msg):
        """
        Process IMU data.
        """
        # In a real system, this would integrate IMU data for pose estimation
        # For this lab, we'll just publish the raw data
        vec_msg = Vector3()
        vec_msg.x = msg.linear_acceleration.x
        vec_msg.y = msg.linear_acceleration.y
        vec_msg.z = msg.linear_acceleration.z
        self.fused_imu_pub.publish(vec_msg)

    def process_sonar_data(self, msg):
        """
        Process sonar data.
        """
        # In a real system, this would fuse with other sensors
        # For this lab, we'll just log the data
        self.get_logger().debug(f'Sonar range: {msg.data}')

    def fusion_callback(self):
        """
        Main fusion processing callback.
        """
        # Perform sensor fusion
        if self.laser_data and self.imu_data:
            # Calculate fused pose estimate (simplified)
            fused_estimate = 0.0  # Placeholder for actual fusion algorithm

            # Publish fused data
            pose_msg = Float32()
            pose_msg.data = fused_estimate
            self.fused_pose_pub.publish(pose_msg)


def main(args=None):
    """
    Main function for the sensor fusion node.
    """
    rclpy.init(args=args)

    sensor_fusion_node = SensorFusionNode()

    try:
        rclpy.spin(sensor_fusion_node)
    except KeyboardInterrupt:
        print('Sensor fusion node interrupted by user')
    finally:
        sensor_fusion_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Step 7: Create the Control Node

Create the control node that manages robot actuators:

```bash
touch ~/ros2_labs/src/robot_control_system/robot_control_system/control_node.py
```

Add the following content:

```python
#!/usr/bin/env python3
"""
File: control_node.py
Purpose: Control node that manages robot actuators and motion
Lab: Lab 4 - Multi-Node Communication System
Dependencies: rclpy, geometry_msgs, std_msgs, custom messages
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Vector3
from std_msgs.msg import Bool, Float32
from sensor_msgs.msg import JointState
import math


class ControlNode(Node):
    """
    Control node that manages robot actuators and motion.
    Converts high-level commands to low-level actuator commands.
    """

    def __init__(self):
        super().__init__('control_node')

        # Robot state
        self.current_cmd = Twist()
        self.emergency_stop = False
        self.safety_enabled = True

        # Publishers
        self.joint_cmd_pub = self.create_publisher(JointState, 'joint_commands', 10)
        self.wheel_vel_pub = self.create_publisher(Twist, 'wheel_velocities', 10)
        self.system_status_pub = self.create_publisher(Bool, 'system_active', 10)

        # Subscribers
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            'cmd_vel',
            self.cmd_vel_callback,
            10
        )

        self.emergency_stop_sub = self.create_subscription(
            Bool,
            'emergency_stop',
            self.emergency_stop_callback,
            10
        )

        self.obstacle_sub = self.create_subscription(
            Bool,
            'obstacle_detected',
            self.obstacle_callback,
            10
        )

        # Timer for control loop
        self.control_timer = self.create_timer(0.01, self.control_loop)  # 100Hz control loop

        # PID controller parameters
        self.kp_linear = 1.0
        self.ki_linear = 0.1
        self.kd_linear = 0.05
        self.kp_angular = 1.0
        self.ki_angular = 0.1
        self.kd_angular = 0.05

        self.get_logger().info('Control node initialized')

    def cmd_vel_callback(self, msg):
        """
        Callback for velocity commands.
        """
        if not self.emergency_stop and self.safety_enabled:
            self.current_cmd = msg
            self.get_logger().debug(f'Received command: linear={msg.linear.x}, angular={msg.angular.z}')
        else:
            # Emergency stop is active, ignore commands
            self.current_cmd = Twist()  # Zero command

    def emergency_stop_callback(self, msg):
        """
        Callback for emergency stop commands.
        """
        self.emergency_stop = msg.data
        if self.emergency_stop:
            self.get_logger().error('EMERGENCY STOP ACTIVATED!')
            # Immediately stop all motion
            self.current_cmd = Twist()
        else:
            self.get_logger().info('Emergency stop cleared')

    def obstacle_callback(self, msg):
        """
        Callback for obstacle detection.
        """
        if msg.data and self.safety_enabled:
            self.get_logger().warn('Obstacle detected, reducing speed')
            # Reduce commanded velocities when obstacle detected
            self.current_cmd.linear.x *= 0.5
            self.current_cmd.angular.z *= 0.5

    def control_loop(self):
        """
        Main control loop that processes commands and sends actuator commands.
        """
        if self.emergency_stop:
            # Publish zero velocities during emergency stop
            zero_twist = Twist()
            self.publish_actuator_commands(zero_twist)
            return

        # Apply safety limits
        cmd = Twist()
        cmd.linear.x = max(-1.0, min(1.0, self.current_cmd.linear.x))  # Limit linear velocity
        cmd.angular.z = max(-1.0, min(1.0, self.current_cmd.angular.z))  # Limit angular velocity

        # Publish actuator commands
        self.publish_actuator_commands(cmd)

        # Publish system status
        status_msg = Bool()
        status_msg.data = not self.emergency_stop
        self.system_status_pub.publish(status_msg)

    def publish_actuator_commands(self, cmd):
        """
        Publish commands to robot actuators.
        """
        # Convert Twist to joint commands for differential drive
        wheel_separation = 0.3  # meters
        wheel_radius = 0.05     # meters

        # Differential drive kinematics
        v_left = (cmd.linear.x - cmd.angular.z * wheel_separation / 2.0) / wheel_radius
        v_right = (cmd.linear.x + cmd.angular.z * wheel_separation / 2.0) / wheel_radius

        # Create joint state message
        joint_msg = JointState()
        joint_msg.name = ['left_wheel_joint', 'right_wheel_joint']
        joint_msg.velocity = [v_left, v_right]
        joint_msg.effort = [0.0, 0.0]  # Effort not used in simulation

        self.joint_cmd_pub.publish(joint_msg)

        # Also publish wheel velocities separately
        wheel_vel_msg = Twist()
        wheel_vel_msg.linear.x = v_left
        wheel_vel_msg.angular.z = v_right
        self.wheel_vel_pub.publish(wheel_vel_msg)


def main(args=None):
    """
    Main function for the control node.
    """
    rclpy.init(args=args)

    control_node = ControlNode()

    try:
        rclpy.spin(control_node)
    except KeyboardInterrupt:
        print('Control node interrupted by user')
    finally:
        # Ensure robot stops on shutdown
        control_node.current_cmd = Twist()
        control_node.emergency_stop = True
        control_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Step 8: Create the Monitoring Node

Create the monitoring node that tracks system health:

```bash
touch ~/ros2_labs/src/robot_control_system/robot_control_system/monitoring_node.py
```

Add the following content:

```python
#!/usr/bin/env python3
"""
File: monitoring_node.py
Purpose: Monitoring node that tracks system health and status
Lab: Lab 4 - Multi-Node Communication System
Dependencies: rclpy, std_msgs, custom messages
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String, Float32
from std_msgs.msg import Header
import time
from collections import deque


class MonitoringNode(Node):
    """
    Monitoring node that tracks system health and status.
    Monitors other nodes and reports system-wide status.
    """

    def __init__(self):
        super().__init__('monitoring_node')

        # System state tracking
        self.node_statuses = {}
        self.error_log = deque(maxlen=100)
        self.start_time = time.time()

        # Publishers
        self.system_health_pub = self.create_publisher(String, 'system_health', 10)
        self.error_report_pub = self.create_publisher(String, 'error_reports', 10)
        self.status_summary_pub = self.create_publisher(String, 'status_summary', 10)

        # Subscribers for monitoring
        self.nav_status_sub = self.create_subscription(
            String,
            'navigation_status',
            self.nav_status_callback,
            10
        )

        self.sys_status_sub = self.create_subscription(
            Bool,
            'system_active',
            self.system_status_callback,
            10
        )

        self.obstacle_sub = self.create_subscription(
            Bool,
            'obstacle_detected',
            self.obstacle_callback,
            10
        )

        # Timer for health monitoring
        self.health_timer = self.create_timer(1.0, self.health_monitoring_callback)

        # Timer for status reporting
        self.report_timer = self.create_timer(5.0, self.status_report_callback)

        self.get_logger().info('Monitoring node initialized')

    def nav_status_callback(self, msg):
        """
        Callback for navigation status updates.
        """
        self.node_statuses['navigation'] = {
            'status': msg.data,
            'timestamp': time.time()
        }
        self.get_logger().debug(f'Navigation status: {msg.data}')

    def system_status_callback(self, msg):
        """
        Callback for system status updates.
        """
        self.node_statuses['control'] = {
            'status': 'ACTIVE' if msg.data else 'INACTIVE',
            'timestamp': time.time()
        }
        self.get_logger().debug(f'Control system status: {msg.data}')

    def obstacle_callback(self, msg):
        """
        Callback for obstacle detection.
        """
        status = 'OBSTACLE_DETECTED' if msg.data else 'CLEAR'
        self.node_statuses['sensors'] = {
            'status': status,
            'timestamp': time.time()
        }

        if msg.data:
            self.log_error('Obstacle detected in path')

    def health_monitoring_callback(self):
        """
        Main health monitoring callback.
        """
        # Check for node timeouts
        current_time = time.time()
        timeout_threshold = 5.0  # seconds

        for node_name, status_info in self.node_statuses.items():
            time_since_update = current_time - status_info['timestamp']
            if time_since_update > timeout_threshold:
                self.log_error(f'Node {node_name} appears unresponsive (last update {time_since_update:.1f}s ago)')

        # Publish system health status
        health_msg = String()
        health_msg.data = self.calculate_system_health()
        self.system_health_pub.publish(health_msg)

    def calculate_system_health(self):
        """
        Calculate overall system health based on node statuses.
        """
        if not self.node_statuses:
            return "UNKNOWN"

        # Count active nodes
        active_nodes = sum(1 for status in self.node_statuses.values()
                          if time.time() - status['timestamp'] < 5.0)

        total_nodes = len(self.node_statuses)

        if active_nodes == 0:
            return "SYSTEM_DOWN"
        elif active_nodes < total_nodes:
            return f"DEGRADED ({active_nodes}/{total_nodes} nodes active)"
        else:
            return "HEALTHY"

    def status_report_callback(self):
        """
        Periodic status reporting callback.
        """
        report_msg = String()
        report_msg.data = self.generate_status_report()
        self.status_summary_pub.publish(report_msg)

        self.get_logger().info(f'System status: {self.calculate_system_health()}')

    def generate_status_report(self):
        """
        Generate a comprehensive status report.
        """
        uptime = time.time() - self.start_time
        report = f"System Report - Uptime: {uptime:.1f}s\n"
        report += f"Active Nodes: {len(self.node_statuses)}\n"
        report += f"System Health: {self.calculate_system_health()}\n"
        report += f"Recent Errors: {len(self.error_log)}\n"

        for node_name, status_info in self.node_statuses.items():
            age = time.time() - status_info['timestamp']
            report += f"  {node_name}: {status_info['status']} (age: {age:.1f}s)\n"

        return report

    def log_error(self, error_msg):
        """
        Log an error message.
        """
        timestamp = time.time()
        self.error_log.append({
            'timestamp': timestamp,
            'message': error_msg
        })

        # Publish error report
        error_report = String()
        error_report.data = f"[{timestamp}] ERROR: {error_msg}"
        self.error_report_pub.publish(error_report)

        self.get_logger().error(error_msg)


def main(args=None):
    """
    Main function for the monitoring node.
    """
    rclpy.init(args=args)

    monitoring_node = MonitoringNode()

    try:
        rclpy.spin(monitoring_node)
    except KeyboardInterrupt:
        print('Monitoring node interrupted by user')
    finally:
        monitoring_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Step 9: Create the Interface Node

Create the interface node that provides external control:

```bash
touch ~/ros2_labs/src/robot_control_system/robot_control_system/interface_node.py
```

Add the following content:

```python
#!/usr/bin/env python3
"""
File: interface_node.py
Purpose: Interface node that provides external control and monitoring
Lab: Lab 4 - Multi-Node Communication System
Dependencies: rclpy, std_msgs, geometry_msgs, custom messages
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool, String
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSHistoryPolicy, QoSReliabilityPolicy


class InterfaceNode(Node):
    """
    Interface node that provides external control and monitoring.
    Acts as a bridge between the robot system and external applications.
    """

    def __init__(self):
        super().__init__('interface_node')

        # QoS profiles for different communication needs
        cmd_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.VOLATILE
        )

        status_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_ALL,
            depth=10,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE
        )

        # Publishers
        self.external_cmd_pub = self.create_publisher(Twist, 'external_cmd_vel', cmd_qos)
        self.emergency_stop_pub = self.create_publisher(Bool, 'emergency_stop', cmd_qos)
        self.system_cmd_pub = self.create_publisher(String, 'system_command', cmd_qos)

        # Subscribers
        self.system_health_sub = self.create_subscription(
            String,
            'system_health',
            self.system_health_callback,
            status_qos
        )

        self.status_summary_sub = self.create_subscription(
            String,
            'status_summary',
            self.status_summary_callback,
            status_qos
        )

        self.error_report_sub = self.create_subscription(
            String,
            'error_reports',
            self.error_report_callback,
            status_qos
        )

        # Timer for interface updates
        self.interface_timer = self.create_timer(0.5, self.interface_callback)

        # System state
        self.last_health_status = "UNKNOWN"
        self.last_error_count = 0

        self.get_logger().info('Interface node initialized')

    def system_health_callback(self, msg):
        """
        Callback for system health updates.
        """
        self.last_health_status = msg.data
        self.get_logger().info(f'System health: {msg.data}')

    def status_summary_callback(self, msg):
        """
        Callback for status summary updates.
        """
        self.get_logger().info(f'Status summary: {msg.data}')

    def error_report_callback(self, msg):
        """
        Callback for error reports.
        """
        self.get_logger().error(f'Error report: {msg.data}')
        self.last_error_count += 1

    def interface_callback(self):
        """
        Interface update callback.
        """
        # In a real system, this might handle external commands from GUI, API, etc.
        # For this lab, we'll just log the status
        self.get_logger().debug(f'Interface active - Health: {self.last_health_status}')

    def send_emergency_stop(self):
        """
        Send emergency stop command to the system.
        """
        stop_msg = Bool()
        stop_msg.data = True
        self.emergency_stop_pub.publish(stop_msg)
        self.get_logger().warn('Emergency stop command sent!')

    def send_velocity_command(self, linear_x, angular_z):
        """
        Send velocity command to the robot.
        """
        cmd_msg = Twist()
        cmd_msg.linear.x = linear_x
        cmd_msg.angular.z = angular_z
        self.external_cmd_pub.publish(cmd_msg)
        self.get_logger().info(f'Sent velocity command: linear={linear_x}, angular={angular_z}')


def main(args=None):
    """
    Main function for the interface node.
    """
    rclpy.init(args=args)

    interface_node = InterfaceNode()

    try:
        # Allow some time for system to initialize
        interface_node.get_logger().info('Interface node running. Use ROS 2 tools to send commands.')
        rclpy.spin(interface_node)
    except KeyboardInterrupt:
        print('Interface node interrupted by user')
    finally:
        interface_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Step 10: Update setup.py

Update the setup.py file to include all our nodes:

```python
from setuptools import setup

package_name = 'robot_control_system'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include launch files
        ('share/' + package_name + '/launch', ['launch/multi_robot_system.launch.py']),
        # Include config files
        ('share/' + package_name + '/config', ['config/system_params.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='student@todo.todo',
    description='Multi-node robot control system for Lab 4',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'navigation_node = robot_control_system.navigation_node:main',
            'sensor_fusion_node = robot_control_system.sensor_fusion_node:main',
            'control_node = robot_control_system.control_node:main',
            'monitoring_node = robot_control_system.monitoring_node:main',
            'interface_node = robot_control_system.interface_node:main',
        ],
    },
)
```

### Step 11: Create a Launch File

Create a launch file to start all nodes together:

```bash
touch ~/ros2_labs/src/robot_control_system/launch/multi_robot_system.launch.py
```

Add the following content:

```python
"""
File: multi_robot_system.launch.py
Purpose: Launch file to start the complete multi-node robot system
Lab: Lab 4 - Multi-Node Communication System
Dependencies: launch, launch_ros
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """
    Generate the launch description for the multi-node robot system.
    """
    # Declare launch arguments
    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='robot1',
        description='Namespace for the robot nodes'
    )

    log_level_arg = DeclareLaunchArgument(
        'log_level',
        default_value='info',
        description='Log level for all nodes'
    )

    # Get launch configurations
    namespace = LaunchConfiguration('namespace')
    log_level = LaunchConfiguration('log_level')

    # Create nodes
    navigation_node = Node(
        package='robot_control_system',
        executable='navigation_node',
        name='navigation_node',
        namespace=namespace,
        parameters=[{'linear_speed': 0.5, 'angular_speed': 0.5}],
        remappings=[
            ('/cmd_vel', 'cmd_vel'),
            ('/robot_pose', 'robot_pose'),
        ],
        arguments=['--ros-args', '--log-level', log_level],
        output='screen'
    )

    sensor_fusion_node = Node(
        package='robot_control_system',
        executable='sensor_fusion_node',
        name='sensor_fusion_node',
        namespace=namespace,
        remappings=[
            ('/scan', 'scan'),
            ('/imu/data', 'imu/data'),
        ],
        arguments=['--ros-args', '--log-level', log_level],
        output='screen'
    )

    control_node = Node(
        package='robot_control_system',
        executable='control_node',
        name='control_node',
        namespace=namespace,
        remappings=[
            ('/cmd_vel', 'cmd_vel'),
            ('/joint_commands', 'joint_commands'),
        ],
        arguments=['--ros-args', '--log-level', log_level],
        output='screen'
    )

    monitoring_node = Node(
        package='robot_control_system',
        executable='monitoring_node',
        name='monitoring_node',
        namespace=namespace,
        arguments=['--ros-args', '--log-level', log_level],
        output='screen'
    )

    interface_node = Node(
        package='robot_control_system',
        executable='interface_node',
        name='interface_node',
        namespace=namespace,
        arguments=['--ros-args', '--log-level', log_level],
        output='screen'
    )

    return LaunchDescription([
        namespace_arg,
        log_level_arg,
        navigation_node,
        sensor_fusion_node,
        control_node,
        monitoring_node,
        interface_node
    ])
```

### Step 12: Build the Package

Build the package with all our nodes:

```bash
cd ~/ros2_labs
source /opt/ros/humble/setup.bash
colcon build --packages-select robot_control_system
```

## Testing the Multi-Node System

### 1. Source the Workspace

```bash
source ~/ros2_labs/install/setup.bash
```

### 2. Start the Complete System

```bash
ros2 launch robot_control_system multi_robot_system.launch.py
```

### 3. Test Communication Between Nodes

Open a new terminal and test communication:

```bash
# Check active nodes
ros2 node list

# Check topics and their connections
ros2 topic list
ros2 topic info /robot1/cmd_vel

# Send a test command
ros2 topic pub /robot1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.5}, angular: {z: 0.2}}' --once

# Monitor system health
ros2 topic echo /robot1/system_health

# Send emergency stop
ros2 topic pub /robot1/emergency_stop std_msgs/msg/Bool '{data: true}' --once
```

### 4. Use rqt_graph to Visualize the System

```bash
rqt_graph
```

## Advanced Exercise: Adding a Service Node

Create an additional node that provides a service for system management:

```bash
touch ~/ros2_labs/src/robot_control_system/robot_control_system/service_manager_node.py
```

Add the following content:

```python
#!/usr/bin/env python3
"""
File: service_manager_node.py
Purpose: Service manager node that provides system management services
Lab: Lab 4 - Multi-Node Communication System
Dependencies: rclpy, std_srvs, custom services
"""

import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger, SetBool
from std_msgs.msg import Bool


class ServiceManagerNode(Node):
    """
    Service manager node that provides system management services.
    Offers services for system control and diagnostics.
    """

    def __init__(self):
        super().__init__('service_manager_node')

        # Create services
        self.reset_service = self.create_service(
            Trigger,
            'system_reset',
            self.reset_callback
        )

        self.emergency_stop_service = self.create_service(
            SetBool,
            'emergency_stop_service',
            self.emergency_stop_callback
        )

        self.diagnostic_service = self.create_service(
            Trigger,
            'run_diagnostics',
            self.diagnostic_callback
        )

        # Publisher for system commands
        self.system_cmd_pub = self.create_publisher(Bool, 'system_command', 10)

        self.get_logger().info('Service manager node initialized')

    def reset_callback(self, request, response):
        """
        Handle system reset request.
        """
        self.get_logger().info('Reset service called')
        response.success = True
        response.message = 'System reset initiated'

        # Publish reset command
        cmd_msg = Bool()
        cmd_msg.data = True
        self.system_cmd_pub.publish(cmd_msg)

        return response

    def emergency_stop_callback(self, request, response):
        """
        Handle emergency stop request.
        """
        self.get_logger().warn(f'Emergency stop service called: {request.data}')
        response.success = True
        response.message = f'Emergency stop set to {request.data}'

        # Publish emergency stop command
        cmd_msg = Bool()
        cmd_msg.data = request.data
        self.system_cmd_pub.publish(cmd_msg)

        return response

    def diagnostic_callback(self, request, response):
        """
        Handle diagnostic request.
        """
        self.get_logger().info('Running diagnostics...')

        # Simulate diagnostic process
        # In a real system, this would check all nodes and connections
        diagnostic_passed = True
        diagnostic_message = "All systems nominal"

        response.success = diagnostic_passed
        response.message = diagnostic_message

        return response


def main(args=None):
    """
    Main function for the service manager node.
    """
    rclpy.init(args=args)

    service_manager_node = ServiceManagerNode()

    try:
        rclpy.spin(service_manager_node)
    except KeyboardInterrupt:
        print('Service manager node interrupted by user')
    finally:
        service_manager_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

Add this node to the setup.py entry points:

```python
'console_scripts': [
    'navigation_node = robot_control_system.navigation_node:main',
    'sensor_fusion_node = robot_control_system.sensor_fusion_node:main',
    'control_node = robot_control_system.control_node:main',
    'monitoring_node = robot_control_system.monitoring_node:main',
    'interface_node = robot_control_system.interface_node:main',
    'service_manager_node = robot_control_system.service_manager_node:main',
],
```

Then rebuild the package:

```bash
cd ~/ros2_labs
colcon build --packages-select robot_control_system
source install/setup.bash
```

Test the services:

```bash
# Call the reset service
ros2 service call /robot1/system_reset std_srvs/srv/Trigger

# Call the emergency stop service
ros2 service call /robot1/emergency_stop_service std_srvs/srv/SetBool '{data: true}'

# Call the diagnostic service
ros2 service call /robot1/run_diagnostics std_srvs/srv/Trigger
```

## Troubleshooting and Debugging

### Common Issues and Solutions

1. **Nodes not communicating**: Check topic names and namespaces
2. **Message type mismatches**: Ensure all nodes use compatible message types
3. **Timing issues**: Use appropriate QoS settings for your application
4. **Parameter configuration**: Verify parameters are declared and used correctly

### Debugging Commands

```bash
# Check all nodes and topics
ros2 node list
ros2 topic list
ros2 service list

# Monitor specific communications
ros2 topic echo /robot1/system_health
ros2 topic hz /robot1/cmd_vel

# Check service availability
ros2 service info /robot1/system_reset

# Visualize the system graph
rqt_graph

# Check parameter values
ros2 param list
ros2 param get /robot1/navigation_node linear_speed
```

## Expected Outcome

By completing this lab, you should have:

- Created a complete multi-node ROS 2 system with proper communication architecture
- Implemented nodes using different communication patterns (topics, services)
- Designed custom message types for your specific application
- Created launch files to coordinate complex multi-node systems
- Applied proper error handling and system monitoring
- Tested and validated the communication between nodes

## Exercises

### Exercise 1: Add Action Server
Implement an action server in one of your nodes that performs a complex task with feedback.

### Exercise 2: Improve Error Handling
Enhance error handling in your nodes to gracefully handle communication failures.

### Exercise 3: Add Parameters
Add more parameters to your nodes to make them more configurable.

### Exercise 4: Create a New Node
Design and implement a new node that performs a specific function in your system.

## Key Concepts Review

- **Multi-node Architecture**: Designing systems with multiple specialized nodes
- **Communication Patterns**: Using topics, services, and actions appropriately
- **Message Types**: Defining and using custom message types
- **Launch Files**: Coordinating complex multi-node systems
- **System Integration**: Connecting nodes to form a cohesive system
- **Error Handling**: Managing errors in distributed systems
- **Monitoring**: Tracking system health and status