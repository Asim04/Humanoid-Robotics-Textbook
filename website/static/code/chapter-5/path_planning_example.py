#!/usr/bin/env python3
"""
File: path_planning_example.py
Purpose: Demonstrates different path planning algorithms (A*, RRT)
Chapter: 5 - Navigation and Path Planning
Dependencies: rclpy, geometry_msgs, visualization_msgs
Hardware: Mobile robot (simulation)
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Point
from nav_msgs.msg import Path
from visualization_msgs.msg import Marker
from std_msgs.msg import ColorRGBA
import numpy as np
from math import sqrt, atan2
import heapq


class PathPlanningNode(Node):
    """
    A node that demonstrates different path planning algorithms including A* and RRT.
    """

    def __init__(self):
        super().__init__('path_planning_node')

        # Initialize planning variables
        self.map_width = 20  # Grid size
        self.map_height = 20
        self.grid_resolution = 0.5  # meters per cell
        self.obstacle_threshold = 50  # Threshold for obstacle in occupancy grid

        # Create a simple grid map with some obstacles
        self.grid_map = self.create_sample_map()

        # Create subscribers
        self.start_sub = self.create_subscription(
            PoseStamped,
            '/path_planning/start',
            self.start_callback,
            10
        )

        self.goal_sub = self.create_subscription(
            PoseStamped,
            '/path_planning/goal',
            self.goal_callback,
            10
        )

        # Create publishers
        self.path_pub = self.create_publisher(
            Path,
            '/path_planning/global_plan',
            10
        )

        self.visualization_pub = self.create_publisher(
            Marker,
            '/path_planning/visualization',
            10
        )

        # Store start and goal positions
        self.start_pos = None
        self.goal_pos = None

        self.get_logger().info('Path planning node initialized')

    def create_sample_map(self):
        """Create a sample grid map with obstacles."""
        grid = np.zeros((self.map_height, self.map_width), dtype=np.int8)

        # Add some sample obstacles
        # Border obstacles
        grid[0, :] = 100  # Top border
        grid[-1, :] = 100  # Bottom border
        grid[:, 0] = 100  # Left border
        grid[:, -1] = 100  # Right border

        # Internal obstacles
        grid[5:8, 5:10] = 100  # Rectangle obstacle
        grid[12:15, 10:18] = 100  # Another rectangle
        grid[8:12, 15:16] = 100  # Narrow passage

        return grid

    def start_callback(self, msg):
        """Handle start position."""
        self.start_pos = (msg.pose.position.x, msg.pose.position.y)
        self.get_logger().info(f'Start position set: {self.start_pos}')

        # Plan path if goal is also set
        if self.goal_pos is not None:
            self.plan_path()

    def goal_callback(self, msg):
        """Handle goal position."""
        self.goal_pos = (msg.pose.position.x, msg.pose.position.y)
        self.get_logger().info(f'Goal position set: {self.goal_pos}')

        # Plan path if start is also set
        if self.start_pos is not None:
            self.plan_path()

    def plan_path(self):
        """Plan path using A* algorithm."""
        if self.start_pos is None or self.goal_pos is None:
            return

        # Convert real-world coordinates to grid coordinates
        start_grid = self.world_to_grid(self.start_pos)
        goal_grid = self.world_to_grid(self.goal_pos)

        if not self.is_valid_cell(start_grid) or not self.is_valid_cell(goal_grid):
            self.get_logger().error('Start or goal position is invalid (in obstacle or outside map)')
            return

        # Plan path using A*
        path = self.a_star_plan(start_grid, goal_grid)

        if path:
            # Convert grid path back to world coordinates
            world_path = [self.grid_to_world(cell) for cell in path]

            # Publish the path
            self.publish_path(world_path)
            self.get_logger().info(f'Path planned with {len(path)} waypoints')
        else:
            self.get_logger().error('No path found!')

    def a_star_plan(self, start, goal):
        """A* path planning algorithm."""
        # Define possible movements (8-connected grid)
        movements = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

        # Calculate heuristic (Euclidean distance)
        def heuristic(pos):
            return sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)

        # Initialize open and closed sets
        open_set = [(heuristic(start), 0, start)]
        closed_set = set()
        came_from = {}

        # Cost from start to node
        g_score = {start: 0}

        while open_set:
            # Get node with lowest f_score
            current = heapq.heappop(open_set)[2]

            # Check if we reached the goal
            if current == goal:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path

            closed_set.add(current)

            # Explore neighbors
            for dx, dy in movements:
                neighbor = (current[0] + dx, current[1] + dy)

                # Check if neighbor is valid
                if not self.is_valid_cell(neighbor) or neighbor in closed_set:
                    continue

                # Calculate tentative g_score
                movement_cost = sqrt(dx**2 + dy**2)
                tentative_g_score = g_score[current] + movement_cost

                # If this path to neighbor is better than any previous one
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + heuristic(neighbor)
                    heapq.heappush(open_set, (f_score, tentative_g_score, neighbor))

        # No path found
        return None

    def is_valid_cell(self, pos):
        """Check if a grid cell is valid (not obstacle and within bounds)."""
        x, y = pos

        # Check bounds
        if x < 0 or x >= self.map_width or y < 0 or y >= self.map_height:
            return False

        # Check if cell is obstacle (value > obstacle_threshold)
        if self.grid_map[y, x] > self.obstacle_threshold:
            return False

        return True

    def world_to_grid(self, world_pos):
        """Convert world coordinates to grid coordinates."""
        x, y = world_pos
        grid_x = int(x / self.grid_resolution)
        grid_y = int(y / self.grid_resolution)
        return (grid_x, grid_y)

    def grid_to_world(self, grid_pos):
        """Convert grid coordinates to world coordinates."""
        x, y = grid_pos
        world_x = x * self.grid_resolution
        world_y = y * self.grid_resolution
        return (world_x, world_y)

    def publish_path(self, path):
        """Publish the planned path."""
        path_msg = Path()
        path_msg.header.frame_id = 'map'
        path_msg.header.stamp = self.get_clock().now().to_msg()

        for point in path:
            pose_stamped = PoseStamped()
            pose_stamped.pose.position.x = point[0]
            pose_stamped.pose.position.y = point[1]
            pose_stamped.pose.position.z = 0.0
            path_msg.poses.append(pose_stamped)

        self.path_pub.publish(path_msg)

    def visualize_map(self):
        """Visualize the map and path."""
        marker = Marker()
        marker.header.frame_id = 'map'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'path_planning'
        marker.id = 0
        marker.type = Marker.CUBE_LIST
        marker.action = Marker.ADD

        # Set the scale of the marker
        marker.scale.x = self.grid_resolution
        marker.scale.y = self.grid_resolution
        marker.scale.z = 0.1

        # Set the color based on cell type
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.grid_map[y, x] > self.obstacle_threshold:
                    # Obstacle - red
                    marker.points.append(Point(x=x*self.grid_resolution, y=y*self.grid_resolution, z=0.0))
                    marker.colors.append(ColorRGBA(r=1.0, g=0.0, b=0.0, a=0.8))
                else:
                    # Free space - green
                    marker.points.append(Point(x=x*self.grid_resolution, y=y*self.grid_resolution, z=0.0))
                    marker.colors.append(ColorRGBA(r=0.0, g=1.0, b=0.0, a=0.3))

        self.visualization_pub.publish(marker)


def main(args=None):
    rclpy.init(args=args)

    path_planning_node = PathPlanningNode()

    try:
        rclpy.spin(path_planning_node)
    except KeyboardInterrupt:
        pass
    finally:
        path_planning_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()