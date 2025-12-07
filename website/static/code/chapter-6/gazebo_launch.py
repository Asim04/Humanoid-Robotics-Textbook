#!/usr/bin/env python3
"""
File: gazebo_launch.py
Purpose: Launch file for Gazebo simulation with custom world and robot
Chapter: 6 - Gazebo Classic & Fortress
Dependencies: launch, launch_ros, gazebo_ros
Hardware: Simulation environment
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world = LaunchConfiguration('world', default='basic_world.world')
    robot_name = LaunchConfiguration('robot_name', default='differential_drive_robot')

    # Get package share directory
    pkg_share = FindPackageShare('my_robot_gazebo').find('my_robot_gazebo')

    # Path to world file
    world_path = PathJoinSubstitution([
        get_package_share_directory('my_robot_gazebo'),
        'worlds',
        world
    ])

    # Launch Gazebo with custom world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            get_package_share_directory('gazebo_ros'),
            '/launch',
            '/gazebo.launch.py'
        ]),
        launch_arguments={
            'world': world_path,
            'verbose': 'false',
            'gui': 'true'
        }.items()
    )

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': get_robot_description()
        }]
    )

    # Spawn robot in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', robot_name,
            '-file', PathJoinSubstitution([
                get_package_share_directory('my_robot_description'),
                'models',
                'differential_drive_robot',
                'robot_model.sdf'
            ]),
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.2'
        ],
        output='screen'
    )

    # Robot controller node
    robot_controller = Node(
        package='my_robot_controller',
        executable='diff_drive_controller',
        name='robot_controller',
        parameters=[{
            'use_sim_time': use_sim_time,
            'cmd_topic': 'diff_drive/cmd_vel',
            'odom_topic': 'diff_drive/odom'
        }],
        output='screen'
    )

    # Create launch description
    ld = LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            'world',
            default_value='basic_world.world',
            description='Choose one of the world files from `/my_robot_gazebo/worlds`'
        ),
        DeclareLaunchArgument(
            'robot_name',
            default_value='differential_drive_robot',
            description='Name of the robot to spawn'
        ),
        gazebo,
        robot_state_publisher,
        spawn_entity,
        robot_controller
    ])

    return ld


def get_robot_description():
    """
    Get robot description from SDF file.
    In a real implementation, this would read the SDF file and return its content.
    """
    # This is a placeholder - in a real implementation, you would read the actual SDF file
    robot_description = """
    <?xml version="1.0" ?>
    <robot name="differential_drive_robot">
      <link name="base_link">
        <inertial>
          <mass value="10.0"/>
          <origin xyz="0 0 0" rpy="0 0 0"/>
          <inertia ixx="0.4" ixy="0.0" ixz="0.0" iyy="0.4" iyz="0.0" izz="0.4"/>
        </inertial>
        <visual>
          <origin xyz="0 0 0" rpy="0 0 0"/>
          <geometry>
            <box size="0.5 0.3 0.15"/>
          </geometry>
          <material name="blue">
            <color rgba="0.1 0.1 0.8 1.0"/>
          </material>
        </visual>
        <collision>
          <origin xyz="0 0 0" rpy="0 0 0"/>
          <geometry>
            <box size="0.5 0.3 0.15"/>
          </geometry>
        </collision>
      </link>
    </robot>
    """
    return robot_description