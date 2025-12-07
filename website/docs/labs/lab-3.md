---
sidebar_position: 3
---

# Lab 3: Building Your First ROS 2 Node

## Objective

In this lab, you will create your first ROS 2 node from scratch, learning the fundamental concepts of ROS 2 development including package creation, node structure, publishers, subscribers, and basic communication patterns.

## Learning Outcomes

After completing this lab, you will be able to:

- Create a new ROS 2 package using colcon
- Implement a basic ROS 2 node in Python
- Create publishers and subscribers for message passing
- Use ROS 2 command-line tools for debugging
- Launch nodes and visualize communication

## Prerequisites

- ROS 2 Humble Hawksbill installed
- Python 3.8+ environment
- Basic Python programming knowledge
- Understanding of ROS 2 concepts from Chapter 3

## Setup and Environment

### 1. Create a Workspace

First, create a new ROS 2 workspace for this lab:

```bash
# Create workspace directory
mkdir -p ~/ros2_labs/src
cd ~/ros2_labs

# Source ROS 2 environment
source /opt/ros/humble/setup.bash
```

### 2. Create a Package

Create a new package for our lab:

```bash
cd ~/ros2_labs/src
ros2 pkg create --build-type ament_python beginner_tutorials
```

This creates a new Python package named `beginner_tutorials` with the basic structure needed for a ROS 2 package.

## Implementation Steps

### Step 1: Examine the Package Structure

Navigate to the newly created package and examine its structure:

```bash
cd ~/ros2_labs/src/beginner_tutorials
ls -la
```

You should see the following structure:
- `package.xml`: Package metadata and dependencies
- `setup.py`: Python package configuration
- `setup.cfg`: Installation configuration
- `test/`: Test directory
- `beginner_tutorials/`: Main Python package directory

### Step 2: Create a Simple Publisher Node

Create a simple publisher node that publishes messages to a topic. Edit the main Python file:

```bash
# Create the Python file
touch ~/ros2_labs/src/beginner_tutorials/beginner_tutorials/simple_publisher.py
```

Add the following content to `simple_publisher.py`:

```python
#!/usr/bin/env python3
"""
File: simple_publisher.py
Purpose: Basic ROS 2 publisher node that publishes messages to a topic
Lab: Lab 3 - Building Your First ROS 2 Node
Dependencies: rclpy, std_msgs
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimplePublisher(Node):
    """
    A simple publisher node that publishes messages to a topic.
    """

    def __init__(self):
        super().__init__('simple_publisher')

        # Create a publisher
        self.publisher_ = self.create_publisher(String, 'chatter', 10)

        # Create a timer to publish messages at regular intervals
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Counter to keep track of messages
        self.i = 0

        self.get_logger().info('SimplePublisher node initialized')

    def timer_callback(self):
        """
        Callback function that publishes messages at regular intervals.
        """
        msg = String()
        msg.data = f'Hello ROS 2 World: {self.i}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1


def main(args=None):
    """
    Main function to initialize and run the node.
    """
    rclpy.init(args=args)

    simple_publisher = SimplePublisher()

    try:
        rclpy.spin(simple_publisher)
    except KeyboardInterrupt:
        print('Node interrupted by user')
    finally:
        # Clean up
        simple_publisher.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Step 3: Create a Simple Subscriber Node

Now create a subscriber node that listens to the messages:

```bash
# Create the subscriber file
touch ~/ros2_labs/src/beginner_tutorials/beginner_tutorials/simple_subscriber.py
```

Add the following content to `simple_subscriber.py`:

```python
#!/usr/bin/env python3
"""
File: simple_subscriber.py
Purpose: Basic ROS 2 subscriber node that subscribes to messages from a topic
Lab: Lab 3 - Building Your First ROS 2 Node
Dependencies: rclpy, std_msgs
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimpleSubscriber(Node):
    """
    A simple subscriber node that subscribes to messages from a topic.
    """

    def __init__(self):
        super().__init__('simple_subscriber')

        # Create a subscription
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        self.get_logger().info('SimpleSubscriber node initialized')

    def listener_callback(self, msg):
        """
        Callback function that processes incoming messages.
        """
        self.get_logger().info(f'I heard: "{msg.data}"')


def main(args=None):
    """
    Main function to initialize and run the node.
    """
    rclpy.init(args=args)

    simple_subscriber = SimpleSubscriber()

    try:
        rclpy.spin(simple_subscriber)
    except KeyboardInterrupt:
        print('Node interrupted by user')
    finally:
        # Clean up
        simple_subscriber.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Step 4: Update Package Configuration

We need to update the `setup.py` file to make our nodes executable:

Edit `~/ros2_labs/src/beginner_tutorials/setup.py`:

```python
from setuptools import setup

package_name = 'beginner_tutorials'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email@example.com',
    description='Beginner tutorials for ROS 2',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simple_publisher = beginner_tutorials.simple_publisher:main',
            'simple_subscriber = beginner_tutorials.simple_subscriber:main',
        ],
    },
)
```

### Step 5: Make Python Files Executable

Make sure the Python files are executable:

```bash
chmod +x ~/ros2_labs/src/beginner_tutorials/beginner_tutorials/simple_publisher.py
chmod +x ~/ros2_labs/src/beginner_tutorials/beginner_tutorials/simple_subscriber.py
```

### Step 6: Build the Package

Build the package using colcon:

```bash
cd ~/ros2_labs
source /opt/ros/humble/setup.bash
colcon build --packages-select beginner_tutorials
```

### Step 7: Source the Workspace

Source the built workspace:

```bash
source ~/ros2_labs/install/setup.bash
```

## Testing Your Nodes

### 1. Run the Publisher Node

Open a new terminal and run the publisher:

```bash
source ~/ros2_labs/install/setup.bash
ros2 run beginner_tutorials simple_publisher
```

You should see output like:
```
[INFO] [1699123456.789012]: Publishing: "Hello ROS 2 World: 0"
[INFO] [1699123457.289012]: Publishing: "Hello ROS 2 World: 1"
[INFO] [1699123457.789012]: Publishing: "Hello ROS 2 World: 2"
```

### 2. Run the Subscriber Node

Open another terminal and run the subscriber:

```bash
source ~/ros2_labs/install/setup.bash
ros2 run beginner_tutorials simple_subscriber
```

You should see output like:
```
[INFO] [1699123456.890123]: I heard: "Hello ROS 2 World: 0"
[INFO] [1699123457.390123]: I heard: "Hello ROS 2 World: 1"
[INFO] [1699123457.890123]: I heard: "Hello ROS 2 World: 2"
```

## Using ROS 2 Command-Line Tools

### 1. Check Active Nodes

```bash
ros2 node list
```

### 2. Check Topics

```bash
ros2 topic list
ros2 topic info /chatter
```

### 3. Echo Messages

```bash
ros2 topic echo /chatter std_msgs/msg/String
```

### 4. Check Node Graph

```bash
rqt_graph
```

## Advanced Exercise: Adding Parameters

### Step 1: Create a Parameterized Node

Create a new node that uses parameters:

```bash
touch ~/ros2_labs/src/beginner_tutorials/beginner_tutorials/parameterized_node.py
```

Add the following content:

```python
#!/usr/bin/env python3
"""
File: parameterized_node.py
Purpose: ROS 2 node that demonstrates parameter usage
Lab: Lab 3 - Building Your First ROS 2 Node
Dependencies: rclpy, std_msgs
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ParameterizedNode(Node):
    """
    A node that demonstrates parameter usage in ROS 2.
    """

    def __init__(self):
        super().__init__('parameterized_node')

        # Declare parameters with default values
        self.declare_parameter('message_prefix', 'Custom Message')
        self.declare_parameter('publish_rate', 1.0)
        self.declare_parameter('message_count', 0)

        # Get parameter values
        self.message_prefix = self.get_parameter('message_prefix').value
        self.publish_rate = self.get_parameter('publish_rate').value
        self.message_count = self.get_parameter('message_count').value

        # Create publisher
        self.publisher_ = self.create_publisher(String, 'parameterized_chatter', 10)

        # Create timer based on parameter
        timer_period = 1.0 / self.publish_rate
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.get_logger().info(f'ParameterizedNode initialized with prefix: {self.message_prefix}, rate: {self.publish_rate}Hz')

    def timer_callback(self):
        """
        Callback function that publishes parameterized messages.
        """
        msg = String()
        msg.data = f'{self.message_prefix}: {self.message_count}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.message_count += 1

        # Update the parameter value
        self.set_parameter(rclpy.parameter.Parameter('message_count', rclpy.Parameter.Type.INTEGER, self.message_count))


def main(args=None):
    """
    Main function to initialize and run the parameterized node.
    """
    rclpy.init(args=args)

    parameterized_node = ParameterizedNode()

    try:
        rclpy.spin(parameterized_node)
    except KeyboardInterrupt:
        print('Node interrupted by user')
    finally:
        parameterized_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Step 2: Update Setup File

Add the new node to the entry points in `setup.py`:

```python
entry_points={
    'console_scripts': [
        'simple_publisher = beginner_tutorials.simple_publisher:main',
        'simple_subscriber = beginner_tutorials.simple_subscriber:main',
        'parameterized_node = beginner_tutorials.parameterized_node:main',
    ],
},
```

### Step 3: Rebuild and Test

```bash
cd ~/ros2_labs
colcon build --packages-select beginner_tutorials
source install/setup.bash
```

Run with custom parameters:

```bash
ros2 run beginner_tutorials parameterized_node --ros-args -p message_prefix:="My Custom Message" -p publish_rate:=2.0
```

## Launch Files

Create a launch file to run both nodes together:

```bash
mkdir -p ~/ros2_labs/src/beginner_tutorials/launch
touch ~/ros2_labs/src/beginner_tutorials/launch/two_nodes_launch.py
```

Add the following content:

```python
"""
File: two_nodes_launch.py
Purpose: Launch file to start publisher and subscriber nodes together
Lab: Lab 3 - Building Your First ROS 2 Node
Dependencies: launch, launch_ros
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """
    Generate the launch description for the two nodes.
    """
    return LaunchDescription([
        Node(
            package='beginner_tutorials',
            executable='simple_publisher',
            name='publisher_node',
            output='screen'
        ),
        Node(
            package='beginner_tutorials',
            executable='simple_subscriber',
            name='subscriber_node',
            output='screen'
        )
    ])
```

Run the launch file:

```bash
cd ~/ros2_labs
source install/setup.bash
ros2 launch beginner_tutorials two_nodes_launch.py
```

## Troubleshooting

### Common Issues and Solutions

1. **Node not found**: Make sure you've built the package and sourced the workspace
2. **Import errors**: Check that all dependencies are declared in `package.xml`
3. **Permission errors**: Make sure Python files are executable
4. **Topic not connecting**: Check that both nodes are on the same ROS domain

### Debugging Commands

```bash
# Check if nodes are running
ros2 node list

# Check topic connections
ros2 topic list
ros2 topic info /chatter

# Echo messages to verify communication
ros2 topic echo /chatter std_msgs/msg/String

# Check parameters
ros2 param list
ros2 param get <node_name> <param_name>
```

## Expected Outcome

By completing this lab, you should have:

- Created a complete ROS 2 package with proper structure
- Implemented publisher and subscriber nodes that communicate with each other
- Used ROS 2 command-line tools to inspect and debug your system
- Created a launch file to run multiple nodes together
- Added parameters to make your node configurable

## Exercises

### Exercise 1: Modify the Publisher
Modify the publisher to publish different types of messages (e.g., publish numbers instead of strings).

### Exercise 2: Add a Service
Create a service server and client that can request the current message count from the publisher.

### Exercise 3: Multiple Topics
Create a node that publishes to multiple topics simultaneously.

### Exercise 4: Quality of Service
Modify your nodes to use different QoS profiles and observe the differences in communication behavior.

## Key Concepts Review

- **Node**: The basic execution unit in ROS 2
- **Publisher**: Sends messages to a topic
- **Subscriber**: Receives messages from a topic
- **Topic**: Named bus for message passing
- **Package**: Organized collection of ROS 2 code
- **Launch file**: Configuration file to start multiple nodes
- **Parameters**: Runtime configuration values for nodes
- **QoS**: Quality of Service policies for communication