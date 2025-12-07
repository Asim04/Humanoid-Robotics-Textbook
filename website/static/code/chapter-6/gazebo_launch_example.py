#!/usr/bin/env python3
"""
File: gazebo_launch_example.py
Purpose: Example launch file for Gazebo simulation with ROS 2
Chapter: 6 - Gazebo Classic & Fortress
Dependencies: launch, launch_ros, gazebo_ros
Hardware: Simulation environment
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world = LaunchConfiguration('world', default='empty.sdf')
    model = LaunchConfiguration('model', default='my_robot')

    # Get the package share directory
    pkg_share = FindPackageShare('my_robot_gazebo').find('my_robot_gazebo')

    # Path to robot description
    robot_description_path = os.path.join(
        get_package_share_directory('my_robot_description'),
        'urdf',
        'my_robot.urdf'
    )

    # Get the URDF content
    with open(robot_description_path, 'r') as infp:
        robot_description_content = infp.read()

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
            'world': PathJoinSubstitution([pkg_share, 'worlds', world]),
            'verbose': 'false',
            'gui': 'true'
        }.items()
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'robot_description': robot_description_content}
        ]
    )

    # Joint State Publisher (for non-fixed joints)
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # Spawn robot in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', model,
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ],
        output='screen'
    )

    # Robot controller node (example)
    robot_controller = Node(
        package='my_robot_controller',
        executable='simple_controller',
        name='robot_controller',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # RViz2 (optional)
    rviz_config = PathJoinSubstitution([
        FindPackageShare('my_robot_description'),
        'rviz',
        'view_robot.rviz'
    ])

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
        condition=launch.conditions.IfCondition(
            LaunchConfiguration('rviz', default='true')
        )
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
            default_value='empty.sdf',
            description='Choose one of the world files from `/my_robot_gazebo/worlds`'
        ),
        DeclareLaunchArgument(
            'model',
            default_value='my_robot',
            description='Robot model name'
        ),
        DeclareLaunchArgument(
            'rviz',
            default_value='true',
            description='Open RViz if true'
        ),
        gazebo,
        robot_state_publisher,
        joint_state_publisher,
        spawn_entity,
        robot_controller,
        rviz
    ])

    return ld


# Alternative launch configuration with more advanced features
def generate_advanced_launch_description():
    """Advanced launch configuration with multiple robots and sensors."""

    # Define launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world = LaunchConfiguration('world', default='multi_room.world')

    # Get package share directory
    pkg_share = FindPackageShare('complex_env_sim').find('complex_env_sim')

    # Launch Gazebo with a complex world
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
            'gui': 'true'
        }.items()
    )

    # Launch multiple robots
    robot_launches = []
    robot_names = ['robot1', 'robot2', 'robot3']
    robot_positions = [
        {'x': '0.0', 'y': '0.0', 'z': '0.1'},
        {'x': '2.0', 'y': '2.0', 'z': '0.1'},
        {'x': '-2.0', 'y': '-2.0', 'z': '0.1'}
    ]

    for i, (name, pos) in enumerate(zip(robot_names, robot_positions)):
        # Robot state publisher for each robot
        robot_state_publisher = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name=f'robot_state_publisher_{name}',
            namespace=name,
            parameters=[
                {'use_sim_time': use_sim_time},
                {'robot_description':
                    # In a real implementation, this would load the robot URDF
                    # For this example, we'll use a placeholder
                    '<robot name="{}">{}</robot>'.format(name,
                    '<link name="base_link"><visual><geometry><box size="0.5 0.3 0.15"/></geometry></visual></link>')
                }
            ],
            remappings=[
                ('/tf', 'tf'),
                ('/tf_static', 'tf_static')
            ]
        )

        # Spawn entity for each robot
        spawn_entity = Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            name=f'spawn_{name}',
            arguments=[
                '-topic', f'/{name}/robot_description',
                '-entity', name,
                '-x', pos['x'],
                '-y', pos['y'],
                '-z', pos['z']
            ],
            output='screen'
        )

        robot_launches.extend([robot_state_publisher, spawn_entity])

    # Add navigation and coordination nodes
    coordinator = Node(
        package='complex_env_sim',
        executable='multi_robot_coordinator',
        name='multi_robot_coordinator',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    ld = LaunchDescription([
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
        coordinator
    ])

    # Add all robot launches
    for launch in robot_launches:
        ld.add_action(launch)

    return ld