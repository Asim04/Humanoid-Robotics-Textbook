---
sidebar_position: 3
---

# Chapter 3: ROS 2 Architecture & Core Concepts

The Robot Operating System 2 (ROS 2) represents a fundamental shift from ROS 1 to a more robust, scalable, and production-ready framework for robotics development. Built on the Data Distribution Service (DDS) middleware, ROS 2 provides improved real-time capabilities, enhanced security, and better support for distributed systems. This chapter introduces the core architectural concepts that underpin ROS 2 and form the foundation for all subsequent robotics development.

## Learning Objectives

After completing this chapter, students will be able to:

- Explain the evolution from ROS 1 to ROS 2 and the key architectural improvements
- Describe the DDS middleware and its role in ROS 2 communication
- Identify and explain the core concepts: nodes, topics, services, actions, and parameters
- Understand Quality of Service (QoS) policies and their impact on communication
- Apply ROS 2 client libraries (rclpy, rclcpp) for node development
- Recognize the security and real-time capabilities of ROS 2

## From ROS 1 to ROS 2: The Evolution

ROS 1, while revolutionary in its time, had several limitations that became apparent as robotics applications matured:

- **Single Master Architecture**: The central master created a single point of failure
- **Real-time Limitations**: No real-time capabilities for safety-critical applications
- **Security Concerns**: No built-in security mechanisms
- **Scalability Issues**: Challenging to deploy in distributed systems
- **Middleware Dependencies**: Tightly coupled to custom communication protocols

ROS 2 addresses these limitations through:

- **DDS-based Communication**: Provides reliable, real-time communication
- **Distributed Architecture**: No single point of failure
- **Enhanced Security**: Built-in authentication, encryption, and access control
- **Real-time Support**: Improved timing guarantees for critical applications
- **Language and Platform Independence**: Better cross-platform support

### Key Differences

| ROS 1 | ROS 2 |
|-------|-------|
| Single master | Distributed architecture |
| Custom communication | DDS-based middleware |
| No security | Built-in security features |
| Master-slave discovery | Peer-to-peer discovery |
| No real-time support | Real-time capabilities |
| roscore-based | No central master |

## DDS Middleware Foundation

The Data Distribution Service (DDS) is an OMG (Object Management Group) standard for real-time, distributed, and reliable data exchange. In ROS 2, DDS serves as the communication layer that enables:

- **Discovery**: Automatic discovery of nodes and topics
- **Communication**: Reliable data exchange between nodes
- **Quality of Service**: Configurable policies for different communication needs
- **Security**: Built-in authentication and encryption

### DDS Concepts

- **Domain**: A communication space where participants can discover each other
- **Participant**: An entity that can create publishers, subscribers, readers, and writers
- **Publisher**: Entity that sends data
- **Subscriber**: Entity that receives data
- **DataWriter**: Interface for publishing data
- **DataReader**: Interface for subscribing to data

## Core ROS 2 Concepts

### Nodes

A node is the fundamental unit of computation in ROS 2. It encapsulates the functionality of a specific component of your robot application. Nodes can:

- Create publishers, subscribers, clients, and services
- Manage parameters
- Execute callbacks
- Log messages

```python
#!/usr/bin/env python3
"""
File: minimal_publisher.py
Purpose: Demonstrates a minimal ROS 2 publisher node
Chapter: 3 - ROS 2 Architecture & Core Concepts
Dependencies: rclpy
Hardware: None (simulation)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

For the complete implementation, see [minimal_publisher.py](/static/code/chapter-3/minimal_publisher.py).

### Topics and Messages

Topics provide asynchronous, many-to-many communication using a publish-subscribe pattern. Messages are the data structures exchanged between nodes.

```python
#!/usr/bin/env python3
"""
File: minimal_subscriber.py
Purpose: Demonstrates a minimal ROS 2 subscriber node
Chapter: 3 - ROS 2 Architecture & Core Concepts
Dependencies: rclpy
Hardware: None (simulation)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

For the complete implementation, see [minimal_subscriber.py](/static/code/chapter-3/minimal_subscriber.py).

### Services

Services provide synchronous, request-response communication. They are useful for operations that need to return a result immediately.

```python
#!/usr/bin/env python3
"""
File: add_two_ints_server.py
Purpose: Demonstrates a ROS 2 service server
Chapter: 3 - ROS 2 Architecture & Core Concepts
Dependencies: rclpy, example_interfaces
Hardware: None (simulation)
"""

from example_interfaces.srv import AddTwoInts
import rclpy
from rclpy.node import Node


class MinimalService(Node):

    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Incoming request\na={request.a}, b={request.b}')
        return response


def main(args=None):
    rclpy.init(args=args)

    minimal_service = MinimalService()

    rclpy.spin(minimal_service)

    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

For the complete implementation, see [add_two_ints_server.py](/static/code/chapter-3/add_two_ints_server.py).

### Actions

Actions provide goal-oriented communication with feedback and status updates. They are ideal for long-running tasks.

```python
#!/usr/bin/env python3
"""
File: fibonacci_action_server.py
Purpose: Demonstrates a ROS 2 action server
Chapter: 3 - ROS 2 Architecture & Core Concepts
Dependencies: rclpy, action_msgs, builtin_interfaces
Hardware: None (simulation)
"""

import time
from action_msgs.msg import GoalStatus
from builtin_interfaces.msg import Duration
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
import rclpy


class FibonacciActionServer(Node):

    def __init__(self):
        super().__init__('fibonacci_action_server')
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            execute_callback=self.execute_callback,
            callback_group=ReentrantCallbackGroup(),
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback)

    def destroy_node(self):
        self._action_server.destroy()
        super().destroy_node()

    def goal_callback(self, goal_request):
        self.get_logger().info('Received goal request')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.sequence = [0, 1]

        for i in range(1, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                return Fibonacci.Result()

            feedback_msg.sequence.append(
                feedback_msg.sequence[i] + feedback_msg.sequence[i-1])

            self.get_logger().info(f'Publishing feedback: {feedback_msg.sequence}')
            goal_handle.publish_feedback(feedback_msg)

            time.sleep(1)

        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence
        self.get_logger().info(f'Returning result: {result.sequence}')

        return result


def main(args=None):
    rclpy.init(args=args)

    fibonacci_action_server = FibonacciActionServer()

    executor = MultiThreadedExecutor()
    rclpy.spin(fibonacci_action_server, executor=executor)

    fibonacci_action_server.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

For the complete implementation, see [fibonacci_action_server.py](/static/code/chapter-3/fibonacci_action_server.py).

### Parameters

Parameters provide a way to configure nodes at runtime. They can be set at launch time or dynamically changed.

```python
#!/usr/bin/env python3
"""
File: parameter_node.py
Purpose: Demonstrates ROS 2 parameter usage
Chapter: 3 - ROS 2 Architecture & Core Concepts
Dependencies: rclpy
Hardware: None (simulation)
"""

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterType


class ParameterNode(Node):

    def __init__(self):
        super().__init__('parameter_node')

        # Declare parameters with default values
        self.declare_parameter('robot_name', 'my_robot')
        self.declare_parameter('max_velocity', 1.0)
        self.declare_parameter('use_sim_time', False)

        # Get parameter values
        robot_name = self.get_parameter('robot_name').value
        max_velocity = self.get_parameter('max_velocity').value
        use_sim_time = self.get_parameter('use_sim_time').value

        self.get_logger().info(f'Robot name: {robot_name}')
        self.get_logger().info(f'Max velocity: {max_velocity}')
        self.get_logger().info(f'Use sim time: {use_sim_time}')

        # Set up parameter callback
        self.add_on_set_parameters_callback(self.parameter_callback)

    def parameter_callback(self, params):
        for param in params:
            self.get_logger().info(f'Parameter {param.name} changed to {param.value}')
        return SetParametersResult(successful=True)


def main(args=None):
    rclpy.init(args=args)

    parameter_node = ParameterNode()

    rclpy.spin(parameter_node)

    parameter_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

For the complete implementation, see [parameter_node.py](/static/code/chapter-3/parameter_node.py).

## Quality of Service (QoS) Policies

QoS policies allow fine-tuning of communication behavior between nodes. They are crucial for meeting real-time requirements and handling network conditions.

### QoS Profiles

- **Reliability**: Best effort vs. Reliable delivery
- **Durability**: Volatile vs. Transient local
- **History**: Keep all vs. Keep last N samples
- **Deadline**: Maximum time between samples
- **Liveliness**: How to detect if publisher is alive

```python
#!/usr/bin/env python3
"""
File: qos_examples.py
Purpose: Demonstrates ROS 2 QoS policies
Chapter: 3 - ROS 2 Architecture & Core Concepts
Dependencies: rclpy
Hardware: None (simulation)
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSHistoryPolicy, QoSReliabilityPolicy
from std_msgs.msg import String


class QoSPublisher(Node):

    def __init__(self):
        super().__init__('qos_publisher')

        # Create different QoS profiles for different use cases

        # Sensor data: Best effort, keep last 10, volatile
        sensor_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE)

        # Critical commands: Reliable, keep last 1, transient local
        command_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL)

        # Log data: Reliable, keep all, volatile
        log_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_ALL,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.VOLATILE)

        self.sensor_publisher = self.create_publisher(String, 'sensor_data', sensor_qos)
        self.command_publisher = self.create_publisher(String, 'commands', command_qos)
        self.log_publisher = self.create_publisher(String, 'log_data', log_qos)


def main(args=None):
    rclpy.init(args=args)

    qos_publisher = QoSPublisher()

    rclpy.spin(qos_publisher)

    qos_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

For the complete implementation, see [qos_examples.py](/static/code/chapter-3/qos_examples.py).

## Client Libraries

ROS 2 provides client libraries for multiple programming languages:

- **rclpy**: Python client library
- **rclcpp**: C++ client library
- **rcl**: Base C library
- **rclc**: C client library
- **Others**: Rust, Java, C#, etc.

## Security in ROS 2

ROS 2 includes built-in security features:

- **Authentication**: Verify identity of nodes
- **Encryption**: Protect data in transit
- **Access Control**: Control what nodes can access

## Real-time Capabilities

ROS 2 supports real-time systems through:

- **DDS Real-time Profiles**: Configurable real-time behavior
- **Schedulability**: Support for real-time schedulers
- **Memory Management**: Predictable memory allocation

## Architecture Summary

The ROS 2 architecture provides:

- **Distributed**: No single point of failure
- **Scalable**: Supports large, distributed systems
- **Secure**: Built-in security features
- **Real-time**: Support for time-critical applications
- **Flexible**: Configurable communication patterns

## Exercises and Review Questions

### Conceptual Questions
1. Explain the key differences between ROS 1 and ROS 2 architectures.
2. Describe the role of DDS middleware in ROS 2 communication.
3. What are the four main communication patterns in ROS 2 and when would you use each?
4. Explain Quality of Service (QoS) policies and their importance in ROS 2.

### Application Questions
5. Design a ROS 2 system architecture for a mobile robot with sensors, actuators, and a navigation system.
6. Identify which QoS policies you would use for different types of robot data (sensor streams, commands, logs).
7. Explain how you would secure a ROS 2 system deployed in a production environment.

### Technical Problems
8. Create a ROS 2 node that publishes sensor data with appropriate QoS settings for real-time applications.
9. Implement a service that calculates the distance between two points in 3D space.
10. Design an action server that moves a robot to a specified goal with feedback on progress.

## Key Terms
- **DDS**: Data Distribution Service - middleware standard for real-time systems
- **Node**: Fundamental computational unit in ROS 2
- **Topic**: Asynchronous publish-subscribe communication channel
- **Service**: Synchronous request-response communication
- **Action**: Goal-oriented communication with feedback
- **QoS**: Quality of Service - policies that define communication behavior
- **Parameter**: Runtime configuration value for nodes
- **Domain**: Communication space in DDS
- **Participant**: Entity in DDS communication
- **Publisher/Subscriber**: DDS communication entities