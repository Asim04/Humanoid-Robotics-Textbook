---
sidebar_position: 4
---

# Chapter 4: ROS 2 Package Development

ROS 2 packages form the fundamental building blocks of robotic applications, organizing code, data, and configuration into reusable and distributable units. This chapter covers the principles and practices of ROS 2 package development, including project structure, build systems, message definitions, and best practices for creating maintainable and efficient packages.

## Learning Objectives

After completing this chapter, students will be able to:

- Create and structure ROS 2 packages using standard conventions
- Use CMake and colcon for building ROS 2 packages
- Define custom messages, services, and actions
- Organize code using launch files and parameter files
- Implement proper package dependencies and interfaces
- Apply testing and documentation practices for ROS 2 packages

## Package Structure and Organization

A ROS 2 package follows a standardized structure that promotes consistency and maintainability:

```
my_robot_package/
├── CMakeLists.txt          # Build configuration for C++
├── package.xml             # Package metadata and dependencies
├── README.md               # Package documentation
├── CHANGELOG.rst           # Version history
├── include/                # Header files (C++)
│   └── my_robot_package/
├── src/                    # Source files (C++)
├── scripts/                # Executable scripts (Python, etc.)
├── launch/                 # Launch files
├── config/                 # Configuration files
├── msg/                    # Custom message definitions
├── srv/                    # Custom service definitions
├── action/                 # Custom action definitions
├── test/                   # Test files
└── setup.py                # Python package configuration
```

### package.xml

The `package.xml` file contains metadata about the package including name, version, maintainers, licenses, dependencies, and export information:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>my_robot_package</name>
  <version>0.0.0</version>
  <description>Package for my robot functionality</description>
  <maintainer email="maintainer@todo.todo">maintainer</maintainer>
  <license>Apache License 2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <depend>rclcpp</depend>
  <depend>rclpy</depend>
  <depend>std_msgs</depend>
  <depend>sensor_msgs</depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

### CMakeLists.txt

For C++ packages, the CMakeLists.txt file defines how to build the package:

```cmake
cmake_minimum_required(VERSION 3.8)
project(my_robot_package)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)

# Include directories
include_directories(include)

# Add executable
add_executable(my_robot_node src/my_robot_node.cpp)
ament_target_dependencies(my_robot_node
  rclcpp
  std_msgs
  sensor_msgs
)

# Install targets
install(TARGETS
  my_robot_node
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

## Build Systems: CMake and colcon

ROS 2 uses CMake as the build system with colcon as the meta-build tool for building multiple packages efficiently.

### CMake for C++ Packages

CMakeLists.txt files define how to build C++ code, handle dependencies, and create executables or libraries:

```cmake
# Minimal CMakeLists.txt for a C++ node
cmake_minimum_required(VERSION 3.8)
project(example_package)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# Add executable
add_executable(example_node src/example_node.cpp)
ament_target_dependencies(example_node rclcpp std_msgs)

# Install executable
install(TARGETS example_node DESTINATION lib/${PROJECT_NAME})

ament_package()
```

### setup.py for Python Packages

For Python packages, setup.py defines how to build and install the package:

```python
from setuptools import setup
from glob import glob
import os

package_name = 'my_robot_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include all launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        # Include all config files
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='maintainer',
    maintainer_email='maintainer@todo.todo',
    description='Package for my robot functionality',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'my_robot_node = my_robot_package.my_robot_node:main',
        ],
    },
)
```

## Creating Custom Messages, Services, and Actions

### Custom Messages

Custom messages are defined in `.msg` files in the `msg/` directory:

```
# File: msg/RobotState.msg
float64 x
float64 y
float64 theta
float64 velocity
float64 angular_velocity
bool is_moving
```

### Custom Services

Custom services are defined in `.srv` files in the `srv/` directory:

```
# File: srv/MoveToPosition.srv
float64 x
float64 y
float64 theta
---
bool success
string message
```

### Custom Actions

Custom actions are defined in `.action` files in the `action/` directory:

```
# File: action/MoveToGoal.action
float64 x
float64 y
---
float64 distance_to_goal
---
float64 remaining_distance
```

## Python Package Development

Python packages in ROS 2 follow standard Python conventions with additional ROS 2 integration:

```python
#!/usr/bin/env python3
"""
File: my_robot_node.py
Purpose: Example ROS 2 Python node demonstrating package structure
Chapter: 4 - ROS 2 Package Development
Dependencies: rclpy, std_msgs
Hardware: None (simulation)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan
import sys
import os

# Add custom message import if needed
# from my_robot_package.msg import RobotState


class MyRobotNode(Node):
    """
    Example robot node demonstrating proper ROS 2 Python package structure.
    This node publishes status information and subscribes to sensor data.
    """

    def __init__(self):
        super().__init__('my_robot_node')

        # Create publishers
        self.status_publisher = self.create_publisher(String, 'robot_status', 10)
        self.heartbeat_publisher = self.create_publisher(String, 'heartbeat', 1)

        # Create subscribers
        self.laser_subscription = self.create_subscription(
            LaserScan,
            'scan',
            self.laser_callback,
            10
        )

        # Create timers
        self.status_timer = self.create_timer(1.0, self.status_callback)
        self.heartbeat_timer = self.create_timer(0.1, self.heartbeat_callback)

        # Initialize node state
        self.robot_state = {
            'position': (0.0, 0.0),
            'velocity': 0.0,
            'status': 'idle',
            'battery_level': 100.0
        }

        self.get_logger().info('MyRobotNode initialized')

    def laser_callback(self, msg):
        """
        Process incoming laser scan data.
        """
        min_distance = min(msg.ranges) if msg.ranges else float('inf')

        if min_distance < 1.0:  # Obstacle within 1 meter
            self.robot_state['status'] = 'obstacle_detected'
            self.get_logger().warn(f'Obstacle detected at {min_distance:.2f}m')
        else:
            self.robot_state['status'] = 'navigating'

    def status_callback(self):
        """
        Publish robot status information.
        """
        status_msg = String()
        status_msg.data = (
            f"Position: ({self.robot_state['position'][0]:.2f}, {self.robot_state['position'][1]:.2f}), "
            f"Status: {self.robot_state['status']}, "
            f"Velocity: {self.robot_state['velocity']:.2f} m/s"
        )
        self.status_publisher.publish(status_msg)

    def heartbeat_callback(self):
        """
        Publish heartbeat message to indicate node is alive.
        """
        heartbeat_msg = String()
        heartbeat_msg.data = f"Heartbeat from {self.get_name()}"
        self.heartbeat_publisher.publish(heartbeat_msg)


def main(args=None):
    """
    Main entry point for the node.
    """
    rclpy.init(args=args)
    node = MyRobotNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

For the complete implementation, see [my_robot_node.py](/static/code/chapter-4/my_robot_node.py).

## Launch Files

Launch files provide a way to start multiple nodes with specific configurations:

```python
#!/usr/bin/env python3
"""
File: my_robot_launch.py
Purpose: Launch file for my robot package
Chapter: 4 - ROS 2 Package Development
Dependencies: launch, launch_ros
Hardware: None (simulation)
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """
    Generate the launch description for the robot system.
    """
    # Declare launch arguments
    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='my_robot',
        description='Namespace for the robot nodes'
    )

    # Get launch configurations
    namespace = LaunchConfiguration('namespace')

    # Create nodes
    robot_node = Node(
        package='my_robot_package',
        executable='my_robot_node',
        name='robot_controller',
        namespace=namespace,
        parameters=[
            {'robot_name': 'my_robot'},
            {'max_velocity': 1.0},
            {'use_sim_time': False}
        ],
        remappings=[
            ('/scan', 'laser_scan'),
            ('/cmd_vel', 'cmd_velocity')
        ]
    )

    diagnostics_node = Node(
        package='my_robot_package',
        executable='diagnostics_node',
        name='diagnostics',
        namespace=namespace
    )

    return LaunchDescription([
        namespace_arg,
        robot_node,
        diagnostics_node
    ])
```

For the complete implementation, see [my_robot_launch.py](/static/code/chapter-4/my_robot_launch.py).

## Parameter Management

Parameters in ROS 2 can be organized in YAML files for easy configuration:

```yaml
# File: config/robot_params.yaml
my_robot:
  ros__parameters:
    robot_name: "my_robot"
    max_velocity: 1.0
    max_angular_velocity: 1.5
    wheel_diameter: 0.1
    wheel_separation: 0.3
    use_sim_time: false
    controller:
      kp: 1.0
      ki: 0.1
      kd: 0.05
    sensors:
      laser_range: [0.1, 30.0]
      imu_enabled: true
      camera_enabled: true
```

## C++ Package Development

C++ packages in ROS 2 use rclcpp and follow modern C++ practices:

```cpp
// File: include/my_robot_package/my_robot_controller.hpp
#ifndef MY_ROBOT_CONTROLLER_HPP_
#define MY_ROBOT_CONTROLLER_HPP_

#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include "nav_msgs/msg/odometry.hpp"

namespace my_robot_package {

class MyRobotController : public rclcpp::Node
{
public:
    explicit MyRobotController(const std::string & node_name);
    virtual ~MyRobotController();

private:
    // Publishers
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_pub_;

    // Subscribers
    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr laser_sub_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;

    // Timers
    rclcpp::TimerBase::SharedPtr control_timer_;

    // Callbacks
    void laser_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg);
    void odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg);
    void control_loop();

    // Robot state
    double current_x_, current_y_, current_theta_;
    double target_x_, target_y_;
    std::string robot_status_;

    // Parameters
    double max_velocity_;
    double max_angular_velocity_;
};

}  // namespace my_robot_package

#endif  // MY_ROBOT_CONTROLLER_HPP_
```

```cpp
// File: src/my_robot_controller.cpp
#include "my_robot_package/my_robot_controller.hpp"

#include <chrono>
#include <cmath>
#include <memory>
#include <string>

using namespace std::chrono_literals;

namespace my_robot_package {

MyRobotController::MyRobotController(const std::string & node_name)
: Node(node_name)
{
    // Declare parameters with default values
    this->declare_parameter<std::string>("robot_name", "my_robot");
    this->declare_parameter<double>("max_velocity", 1.0);
    this->declare_parameter<double>("max_angular_velocity", 1.5);

    // Get parameter values
    max_velocity_ = this->get_parameter("max_velocity").as_double();
    max_angular_velocity_ = this->get_parameter("max_angular_velocity").as_double();

    // Create publishers
    cmd_vel_pub_ = this->create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);

    // Create subscribers
    laser_sub_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
        "scan", 10,
        std::bind(&MyRobotController::laser_callback, this, std::placeholders::_1));

    odom_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
        "odom", 10,
        std::bind(&MyRobotController::odom_callback, this, std::placeholders::_1));

    // Create timer for control loop
    control_timer_ = this->create_wall_timer(
        50ms, std::bind(&MyRobotController::control_loop, this));

    RCLCPP_INFO(this->get_logger(), "MyRobotController initialized");
}

MyRobotController::~MyRobotController()
{
    RCLCPP_INFO(this->get_logger(), "MyRobotController destroyed");
}

void MyRobotController::laser_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg)
{
    // Find minimum distance in laser scan
    float min_distance = std::numeric_limits<float>::max();
    for (const auto& range : msg->ranges) {
        if (std::isfinite(range) && range < min_distance) {
            min_distance = range;
        }
    }

    if (min_distance < 1.0) {  // Obstacle within 1 meter
        RCLCPP_WARN(this->get_logger(), "Obstacle detected at %.2f m", min_distance);
        robot_status_ = "obstacle_detected";
    } else {
        robot_status_ = "navigating";
    }
}

void MyRobotController::odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
{
    current_x_ = msg->pose.pose.position.x;
    current_y_ = msg->pose.pose.position.y;

    // Extract orientation (simplified - should use proper quaternion conversion)
    current_theta_ = 2.0 * std::atan2(msg->pose.pose.orientation.z,
                                     msg->pose.pose.orientation.w);
}

void MyRobotController::control_loop()
{
    // Simple control logic
    auto cmd_msg = geometry_msgs::msg::Twist();

    if (robot_status_ == "obstacle_detected") {
        // Stop if obstacle detected
        cmd_msg.linear.x = 0.0;
        cmd_msg.angular.z = 0.0;
    } else {
        // Move forward
        cmd_msg.linear.x = 0.5;  // 0.5 m/s
        cmd_msg.angular.z = 0.0;
    }

    cmd_vel_pub_->publish(cmd_msg);
}

}  // namespace my_robot_package

// Main function
int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<my_robot_package::MyRobotController>("my_robot_controller");

    rclcpp::spin(node);
    rclcpp::shutdown();

    return 0;
}
```

For the complete implementation, see [my_robot_controller.hpp](/static/code/chapter-4/my_robot_controller.hpp) and [my_robot_controller.cpp](/static/code/chapter-4/my_robot_controller.cpp).

## Testing and Documentation

### Unit Testing

ROS 2 packages should include comprehensive tests:

```python
#!/usr/bin/env python3
"""
File: test_my_robot_node.py
Purpose: Unit tests for my robot node
Chapter: 4 - ROS 2 Package Development
Dependencies: rclpy, pytest, unittest
Hardware: None (simulation)
"""

import unittest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from my_robot_package.my_robot_node import MyRobotNode


class TestMyRobotNode(unittest.TestCase):
    """
    Unit tests for MyRobotNode.
    """

    def setUp(self):
        """
        Set up test environment.
        """
        if not rclpy.ok():
            rclpy.init()
        self.node = MyRobotNode()
        self.executor = SingleThreadedExecutor()
        self.executor.add_node(self.node)

    def tearDown(self):
        """
        Clean up test environment.
        """
        self.executor.remove_node(self.node)
        self.node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

    def test_node_initialization(self):
        """
        Test that the node initializes correctly.
        """
        self.assertIsNotNone(self.node)
        self.assertEqual(self.node.get_name(), 'my_robot_node')

    def test_heartbeat_timer(self):
        """
        Test that heartbeat timer is active.
        """
        # Check that timers exist
        timers = [timer for timer in self.node.timers if timer is not None]
        self.assertGreater(len(timers), 0)


def main():
    """
    Main function to run tests.
    """
    unittest.main()


if __name__ == '__main__':
    main()
```

For the complete implementation, see [test_my_robot_node.py](/static/code/chapter-4/test_my_robot_node.py).

### Documentation

Package documentation should include:

- README.md with usage instructions
- API documentation for classes and functions
- Configuration guides
- Troubleshooting guides

## Best Practices

### Code Organization

- Use consistent naming conventions
- Separate concerns into different modules
- Follow ROS 2 style guides
- Use proper error handling

### Performance Considerations

- Minimize memory allocations in loops
- Use appropriate QoS settings
- Consider real-time constraints
- Profile and optimize critical paths

### Security Considerations

- Validate all inputs
- Use secure communication when needed
- Follow principle of least privilege
- Regular security updates

## Build and Deployment

### Building Packages

```bash
# Build a single package
colcon build --packages-select my_robot_package

# Build with specific build type
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release

# Build and run tests
colcon build --packages-select my_robot_package
colcon test --packages-select my_robot_package
```

### Installing and Running

```bash
# Source the workspace
source install/setup.bash

# Run a node
ros2 run my_robot_package my_robot_node

# Launch with launch file
ros2 launch my_robot_package my_robot_launch.py
```

## Exercises and Review Questions

### Conceptual Questions
1. Explain the standard structure of a ROS 2 package and the purpose of each directory.
2. Describe the difference between CMake-based and Python-based ROS 2 packages.
3. What are the advantages of using launch files over running nodes separately?
4. Explain how custom messages, services, and actions are defined and used.

### Application Questions
5. Design a package structure for a mobile robot with navigation, perception, and control capabilities.
6. Create appropriate launch files for different robot configurations (simulation vs. real robot).
7. Explain how you would organize parameters for a complex robot system with multiple subsystems.

### Technical Problems
8. Create a ROS 2 package with both C++ and Python nodes that communicate with each other.
9. Implement a custom message type and use it in a publisher-subscriber pair.
10. Write a launch file that starts multiple nodes with different parameter configurations.

## Key Terms
- **Package**: Fundamental unit of code organization in ROS 2
- **ament**: ROS 2 build system and package management framework
- **colcon**: Multi-package build tool for ROS
- **CMake**: Cross-platform build system generator
- **Launch file**: Configuration file for starting multiple nodes
- **Custom message**: User-defined data structure for ROS communication
- **Dependency**: Package required by another package
- **Entry point**: Python console script definition
- **QoS**: Quality of Service policies for communication
- **Build type**: Compilation settings (Debug, Release, etc.)