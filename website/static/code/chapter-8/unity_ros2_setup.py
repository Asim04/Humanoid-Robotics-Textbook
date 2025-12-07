#!/usr/bin/env python3
"""
File: unity_ros2_setup.py
Purpose: Setup and configuration script for Unity-ROS2 bridge
Chapter: 8 - Unity for Robot Visualization
Dependencies: rosbridge_suite, unity_robotics_msgs, rospy
Hardware: Unity simulation environment
"""

import rospy
import socket
import json
import threading
import time
from std_msgs.msg import String, Float32
from sensor_msgs.msg import LaserScan, Imu, JointState, PointCloud2
from geometry_msgs.msg import Twist, Pose, Vector3
from nav_msgs.msg import Odometry
from unity_robotics_demo_msgs.msg import UnityHandshake, FromUnity, ToUnity


class UnityROS2BridgeSetup:
    """
    Setup and configuration class for Unity-ROS2 bridge.
    Handles connection establishment, topic mapping, and message routing.
    """

    def __init__(self):
        rospy.init_node('unity_ros2_bridge_setup', anonymous=True)

        # Bridge configuration
        self.unity_ip = rospy.get_param('~unity_ip', '127.0.0.1')
        self.unity_port = rospy.get_param('~unity_port', 5005)
        self.ros_bridge_port = rospy.get_param('~ros_bridge_port', 9090)

        # Topic mappings
        self.topic_mappings = {
            '/cmd_vel': '/cmd_vel',
            '/odom': '/odom',
            '/scan': '/scan',
            '/imu/data': '/imu/data',
            '/joint_states': '/joint_states',
            '/pointcloud': '/pointcloud'
        }

        # Publishers and subscribers
        self.publishers = {}
        self.subscribers = {}

        # Bridge status
        self.bridge_connected = False
        self.last_heartbeat = time.time()
        self.heartbeat_interval = 5.0  # seconds

        # Setup ROS publishers and subscribers
        self.setup_ros_interfaces()

        # Setup Unity connection
        self.setup_unity_connection()

        rospy.loginfo(f'Unity-ROS2 bridge setup initialized. Unity IP: {self.unity_ip}:{self.unity_port}')

    def setup_ros_interfaces(self):
        """Setup ROS publishers and subscribers for robot communication."""

        # Publishers for sending data to ROS topics
        self.publishers['odom'] = rospy.Publisher('/odom', Odometry, queue_size=10)
        self.publishers['laser_scan'] = rospy.Publisher('/scan', LaserScan, queue_size=10)
        self.publishers['imu'] = rospy.Publisher('/imu/data', Imu, queue_size=10)
        self.publishers['joint_states'] = rospy.Publisher('/joint_states', JointState, queue_size=10)
        self.publishers['pointcloud'] = rospy.Publisher('/pointcloud', PointCloud2, queue_size=10)
        self.publishers['status'] = rospy.Publisher('/unity_bridge/status', String, queue_size=10)

        # Subscribers for receiving data from ROS topics
        self.subscribers['cmd_vel'] = rospy.Subscriber('/cmd_vel', Twist, self.cmd_vel_callback)
        self.subscribers['heartbeat'] = rospy.Subscriber('/unity_bridge/heartbeat', String, self.heartbeat_callback)

        rospy.loginfo('ROS interfaces setup completed')

    def setup_unity_connection(self):
        """Setup connection to Unity application."""
        try:
            # Create socket connection to Unity
            self.unity_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.unity_socket.connect((self.unity_ip, self.unity_port))
            self.unity_socket.settimeout(1.0)  # 1 second timeout

            # Send handshake message
            handshake_msg = {
                'type': 'handshake',
                'timestamp': time.time(),
                'version': '1.0',
                'supported_topics': list(self.topic_mappings.keys())
            }

            self.unity_socket.send(json.dumps(handshake_msg).encode('utf-8'))
            rospy.loginfo(f'Connected to Unity at {self.unity_ip}:{self.unity_port}')

            self.bridge_connected = True

            # Start message receiving thread
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()

        except Exception as e:
            rospy.logerr(f'Failed to connect to Unity: {e}')
            self.bridge_connected = False

    def cmd_vel_callback(self, msg):
        """Handle incoming velocity commands from ROS."""
        if self.bridge_connected:
            # Convert ROS Twist message to Unity format
            cmd_data = {
                'type': 'cmd_vel',
                'linear': {
                    'x': msg.linear.x,
                    'y': msg.linear.y,
                    'z': msg.linear.z
                },
                'angular': {
                    'x': msg.angular.x,
                    'y': msg.angular.y,
                    'z': msg.angular.z
                },
                'timestamp': time.time()
            }

            try:
                self.unity_socket.send(json.dumps(cmd_data).encode('utf-8'))
            except Exception as e:
                rospy.logerr(f'Failed to send cmd_vel to Unity: {e}')
                self.bridge_connected = False

    def heartbeat_callback(self, msg):
        """Handle heartbeat messages."""
        self.last_heartbeat = time.time()

    def receive_messages(self):
        """Receive messages from Unity in a separate thread."""
        buffer = ""

        while not rospy.is_shutdown() and self.bridge_connected:
            try:
                data = self.unity_socket.recv(4096).decode('utf-8')
                if not data:
                    break

                buffer += data

                # Process complete messages (assuming they're separated by newlines)
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    self.process_unity_message(json.loads(message))

            except socket.timeout:
                # Check if connection is still alive
                if time.time() - self.last_heartbeat > self.heartbeat_interval * 2:
                    rospy.logwarn('Unity connection may be lost')
                    self.bridge_connected = False
            except Exception as e:
                rospy.logerr(f'Error receiving message from Unity: {e}')
                self.bridge_connected = False
                break

    def process_unity_message(self, msg):
        """Process messages received from Unity."""
        msg_type = msg.get('type', 'unknown')

        if msg_type == 'odom':
            self.process_odom_message(msg)
        elif msg_type == 'sensor_data':
            self.process_sensor_message(msg)
        elif msg_type == 'heartbeat':
            self.last_heartbeat = time.time()
            self.publish_bridge_status('connected')
        elif msg_type == 'robot_state':
            self.process_robot_state_message(msg)
        else:
            rospy.logdebug(f'Unknown message type from Unity: {msg_type}')

    def process_odom_message(self, msg):
        """Process odometry data from Unity."""
        try:
            odom_msg = Odometry()
            odom_msg.header.stamp = rospy.Time.now()
            odom_msg.header.frame_id = 'odom'
            odom_msg.child_frame_id = 'base_link'

            # Position
            pos = msg.get('position', {})
            odom_msg.pose.pose.position.x = pos.get('x', 0.0)
            odom_msg.pose.pose.position.y = pos.get('y', 0.0)
            odom_msg.pose.pose.position.z = pos.get('z', 0.0)

            # Orientation
            rot = msg.get('orientation', {})
            odom_msg.pose.pose.orientation.x = rot.get('x', 0.0)
            odom_msg.pose.pose.orientation.y = rot.get('y', 0.0)
            odom_msg.pose.pose.orientation.z = rot.get('z', 0.0)
            odom_msg.pose.pose.orientation.w = rot.get('w', 1.0)

            # Velocity
            lin_vel = msg.get('linear_velocity', {})
            odom_msg.twist.twist.linear.x = lin_vel.get('x', 0.0)
            odom_msg.twist.twist.linear.y = lin_vel.get('y', 0.0)
            odom_msg.twist.twist.linear.z = lin_vel.get('z', 0.0)

            ang_vel = msg.get('angular_velocity', {})
            odom_msg.twist.twist.angular.x = ang_vel.get('x', 0.0)
            odom_msg.twist.twist.angular.y = ang_vel.get('y', 0.0)
            odom_msg.twist.twist.angular.z = ang_vel.get('z', 0.0)

            # Publish to ROS
            self.publishers['odom'].publish(odom_msg)

        except Exception as e:
            rospy.logerr(f'Error processing odometry message: {e}')

    def process_sensor_message(self, msg):
        """Process sensor data from Unity."""
        sensor_type = msg.get('sensor_type', 'unknown')

        if sensor_type == 'lidar':
            self.process_lidar_message(msg)
        elif sensor_type == 'imu':
            self.process_imu_message(msg)
        elif sensor_type == 'camera':
            self.process_camera_message(msg)

    def process_lidar_message(self, msg):
        """Process LiDAR data from Unity."""
        try:
            scan_msg = LaserScan()
            scan_msg.header.stamp = rospy.Time.now()
            scan_msg.header.frame_id = 'laser_link'

            # Set laser scan parameters
            scan_msg.angle_min = msg.get('angle_min', -3.14159)
            scan_msg.angle_max = msg.get('angle_max', 3.14159)
            scan_msg.angle_increment = msg.get('angle_increment', 0.01)
            scan_msg.time_increment = msg.get('time_increment', 0.0)
            scan_msg.scan_time = msg.get('scan_time', 0.0)
            scan_msg.range_min = msg.get('range_min', 0.1)
            scan_msg.range_max = msg.get('range_max', 10.0)

            # Set ranges
            scan_msg.ranges = msg.get('ranges', [])

            # Publish to ROS
            self.publishers['laser_scan'].publish(scan_msg)

        except Exception as e:
            rospy.logerr(f'Error processing lidar message: {e}')

    def process_imu_message(self, msg):
        """Process IMU data from Unity."""
        try:
            imu_msg = Imu()
            imu_msg.header.stamp = rospy.Time.now()
            imu_msg.header.frame_id = 'imu_link'

            # Orientation
            orientation = msg.get('orientation', {})
            imu_msg.orientation.x = orientation.get('x', 0.0)
            imu_msg.orientation.y = orientation.get('y', 0.0)
            imu_msg.orientation.z = orientation.get('z', 0.0)
            imu_msg.orientation.w = orientation.get('w', 1.0)

            # Angular velocity
            ang_vel = msg.get('angular_velocity', {})
            imu_msg.angular_velocity.x = ang_vel.get('x', 0.0)
            imu_msg.angular_velocity.y = ang_vel.get('y', 0.0)
            imu_msg.angular_velocity.z = ang_vel.get('z', 0.0)

            # Linear acceleration
            lin_acc = msg.get('linear_acceleration', {})
            imu_msg.linear_acceleration.x = lin_acc.get('x', 0.0)
            imu_msg.linear_acceleration.y = lin_acc.get('y', 0.0)
            imu_msg.linear_acceleration.z = lin_acc.get('z', 0.0)

            # Publish to ROS
            self.publishers['imu'].publish(imu_msg)

        except Exception as e:
            rospy.logerr(f'Error processing IMU message: {e}')

    def process_robot_state_message(self, msg):
        """Process robot state data from Unity."""
        try:
            joint_msg = JointState()
            joint_msg.header.stamp = rospy.Time.now()
            joint_msg.header.frame_id = 'base_link'

            # Process joint states
            joints = msg.get('joints', {})
            for joint_name, joint_data in joints.items():
                joint_msg.name.append(joint_name)
                joint_msg.position.append(joint_data.get('position', 0.0))
                joint_msg.velocity.append(joint_data.get('velocity', 0.0))
                joint_msg.effort.append(joint_data.get('effort', 0.0))

            # Publish to ROS
            self.publishers['joint_states'].publish(joint_msg)

        except Exception as e:
            rospy.logerr(f'Error processing robot state message: {e}')

    def publish_bridge_status(self, status):
        """Publish bridge status to ROS."""
        status_msg = String()
        status_msg.data = status
        self.publishers['status'].publish(status_msg)

    def run(self):
        """Main run loop."""
        rate = rospy.Rate(10)  # 10 Hz

        while not rospy.is_shutdown():
            # Send heartbeat to Unity periodically
            if self.bridge_connected and time.time() - self.last_heartbeat > self.heartbeat_interval:
                heartbeat_msg = {
                    'type': 'heartbeat',
                    'timestamp': time.time()
                }

                try:
                    self.unity_socket.send(json.dumps(heartbeat_msg).encode('utf-8') + b'\n')
                    self.last_heartbeat = time.time()
                except Exception as e:
                    rospy.logerr(f'Failed to send heartbeat to Unity: {e}')
                    self.bridge_connected = False

            # Publish bridge status
            status = 'connected' if self.bridge_connected else 'disconnected'
            self.publish_bridge_status(status)

            rate.sleep()


def main():
    try:
        bridge_setup = UnityROS2BridgeSetup()
        bridge_setup.run()
    except rospy.ROSInterruptException:
        rospy.loginfo('Unity-ROS2 bridge setup node terminated')
    except Exception as e:
        rospy.logerr(f'Error in Unity-ROS2 bridge setup: {e}')


if __name__ == '__main__':
    main()