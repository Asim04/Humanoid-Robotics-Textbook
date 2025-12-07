# Lab 9: First Isaac Sim Environment

## Objective

In this lab, you will set up your first Isaac Sim environment, create a basic scene with a robot, configure sensors, and run a simple simulation. By the end of this lab, you will understand the fundamental components of Isaac Sim and be able to create and run basic robotic simulations.

## Prerequisites

- NVIDIA GPU with RTX technology (recommended: RTX 3080 or higher)
- NVIDIA Omniverse installed and running
- Isaac Sim extension installed
- Basic understanding of Python programming
- Familiarity with ROS2 concepts (optional but helpful)

## Learning Outcomes

After completing this lab, you will be able to:
1. Set up and configure Isaac Sim for basic use
2. Create a simple scene with a robot model
3. Configure and use basic sensors in Isaac Sim
4. Run a simulation and interact with the environment
5. Understand the basic architecture and workflow of Isaac Sim

## Estimated Time

- Setup: 30 minutes
- Implementation: 60 minutes
- Testing and Validation: 30 minutes
- Total: 120 minutes

## Task 1: Environment Setup and Isaac Sim Installation

### Step 1: Verify System Requirements
1. Check your GPU specifications to ensure it meets Isaac Sim requirements
2. Verify NVIDIA driver version (should be 470 or later)
3. Confirm CUDA installation and compatibility

### Step 2: Install Omniverse and Isaac Sim
1. Download and install NVIDIA Omniverse from the official website
2. Launch Omniverse Launcher
3. Install the Isaac Sim extension
4. Ensure all dependencies are properly installed

### Step 3: Verify Installation
1. Launch Isaac Sim from Omniverse Launcher
2. Confirm the application starts without errors
3. Test basic functionality by opening a sample scene

## Task 2: Create a Basic Scene

### Step 1: Initialize Isaac Sim in Python
Create a new Python script called `basic_isaac_sim.py`:

```python
import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage, get_stage_units
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.prims import create_prim
from omni.isaac.core.robots import Robot
from omni.isaac.core.objects import DynamicCuboid
import numpy as np
import carb

# Initialize Isaac Sim
def setup_isaac_sim():
    # Set up the world with 1-meter units
    world = World(stage_units_in_meters=1.0)

    # Set physics parameters
    world.scene.add_default_ground_plane()

    print("Isaac Sim environment initialized successfully!")
    return world

# Main execution
if __name__ == "__main__":
    world = setup_isaac_sim()

    # Reset the world to initialize physics
    world.reset()

    # Run the simulation for a few steps to verify
    for i in range(100):
        world.step(render=True)

    # Clean up
    world.clear()
```

### Step 2: Add a Simple Robot Model
Extend the script to include a basic robot:

```python
# Add this function to your script
def add_robot_to_scene(world):
    # Add a simple wheeled robot to the scene
    # In a real scenario, you would use a proper robot USD file
    robot = world.scene.add(
        Robot(
            prim_path="/World/Robot",
            name="simple_robot",
            usd_path="/Isaac/Robots/Carter/carter_model.usd",  # Example robot path
            position=np.array([0.0, 0.0, 0.5]),
            orientation=np.array([0.0, 0.0, 0.0, 1.0])
        )
    )
    return robot

# Update the main execution
if __name__ == "__main__":
    world = setup_isaac_sim()

    # Add robot to the scene
    robot = add_robot_to_scene(world)

    # Reset the world to initialize physics
    world.reset()

    # Run the simulation for a few steps
    for i in range(200):
        world.step(render=True)
        if i % 100 == 0:
            print(f"Simulation step: {i}")

    # Clean up
    world.clear()
```

### Step 3: Add Objects to the Environment
Add some simple objects to interact with:

```python
def add_objects_to_scene(world):
    # Add a few dynamic objects to the scene
    object1 = world.scene.add(
        DynamicCuboid(
            prim_path="/World/Object1",
            name="object1",
            position=np.array([1.0, 1.0, 0.5]),
            size=0.2,
            color=np.array([0.8, 0.1, 0.1])
        )
    )

    object2 = world.scene.add(
        DynamicCuboid(
            prim_path="/World/Object2",
            name="object2",
            position=np.array([-1.0, -1.0, 0.5]),
            size=0.2,
            color=np.array([0.1, 0.8, 0.1])
        )
    )

    return [object1, object2]

# Update the main execution
if __name__ == "__main__":
    world = setup_isaac_sim()

    # Add objects to the scene
    objects = add_objects_to_scene(world)

    # Add robot to the scene
    robot = add_robot_to_scene(world)

    # Reset the world to initialize physics
    world.reset()

    # Run the simulation for a few steps
    for i in range(300):
        world.step(render=True)
        if i % 100 == 0:
            print(f"Simulation step: {i}")

    # Clean up
    world.clear()
```

## Task 3: Configure Sensors

### Step 1: Add a Camera Sensor
Modify your script to include a camera sensor:

```python
from omni.isaac.sensor import Camera
from omni.isaac.core.utils.prims import set_targets

def add_camera_sensor(world, robot_prim_path):
    # Create camera sensor
    camera = Camera(
        prim_path=f"{robot_prim_path}/camera",
        position=np.array([0.2, 0.0, 0.1]),
        frequency=30,
        resolution=(640, 480)
    )

    # Add the camera to the world
    world.scene.add(camera)

    return camera

# Update the main execution to include the camera
if __name__ == "__main__":
    world = setup_isaac_sim()

    # Add objects to the scene
    objects = add_objects_to_scene(world)

    # Add robot to the scene
    robot = add_robot_to_scene(world)

    # Add camera to the robot
    camera = add_camera_sensor(world, "/World/Robot")

    # Reset the world to initialize physics
    world.reset()

    # Run the simulation and capture camera data
    for i in range(300):
        world.step(render=True)

        if i % 30 == 0:  # Capture image every 30 steps
            camera_data = camera.get_rgb()
            if camera_data is not None:
                print(f"Captured image at step {i}, shape: {camera_data.shape}")

    # Clean up
    world.clear()
```

### Step 2: Add a LiDAR Sensor
Add a LiDAR sensor to your robot:

```python
from omni.isaac.range_sensor import LidarRtx
from omni.isaac.range_sensor._range_sensor import acquire_lidar_sensor_interface

def add_lidar_sensor(world, robot_prim_path):
    # Create LiDAR sensor
    lidar = LidarRtx(
        prim_path=f"{robot_prim_path}/Lidar",
        name="Lidar_Sensor",
        translation=np.array([0.0, 0.0, 0.3]),
        orientation=np.array([0, 0.0, 0.0, 1.0]),
        config="Example_Rotary_Lidar",
        depth_range=20.0,
        frequency=20,
        horizontal_resolution=0.5,
        vertical_resolution=0.5,
        horizontal_fov=360,
        vertical_fov=30
    )

    # Add the LiDAR to the world
    world.scene.add(lidar)

    return lidar

# Update the main execution to include the LiDAR
if __name__ == "__main__":
    world = setup_isaac_sim()

    # Add objects to the scene
    objects = add_objects_to_scene(world)

    # Add robot to the scene
    robot = add_robot_to_scene(world)

    # Add sensors to the robot
    camera = add_camera_sensor(world, "/World/Robot")
    lidar = add_lidar_sensor(world, "/World/Robot")

    # Reset the world to initialize physics
    world.reset()

    # Run the simulation and capture sensor data
    for i in range(500):
        world.step(render=True)

        if i % 30 == 0:  # Capture camera data every 30 steps
            camera_data = camera.get_rgb()
            if camera_data is not None:
                print(f"Captured image at step {i}")

        if i % 20 == 0:  # Capture LiDAR data every 20 steps
            lidar_data = lidar.get_linear_depth_data()
            if lidar_data is not None:
                print(f"Captured LiDAR data at step {i}, points: {len(lidar_data)}")

    # Clean up
    world.clear()
```

## Task 4: Implement Basic Robot Control

### Step 1: Create a Simple Controller
Add a basic controller to move the robot:

```python
def simple_move_robot(robot, world, target_position, speed=0.1):
    """
    Simple function to move robot toward a target position
    This is a simplified approach - in real applications, use proper control interfaces
    """
    # Get current position
    current_pos = robot.get_world_pose()[0]

    # Calculate direction to target
    direction = target_position - current_pos
    distance = np.linalg.norm(direction)

    if distance > 0.1:  # If not close enough to target
        direction = direction / distance  # Normalize
        velocity = direction * speed
        # In a real implementation, you would set joint velocities here
        print(f"Moving toward {target_position}, current pos: {current_pos}")

    return distance < 0.1  # Return True if reached

# Update the main execution with control
if __name__ == "__main__":
    world = setup_isaac_sim()

    # Add objects to the scene
    objects = add_objects_to_scene(world)

    # Add robot to the scene
    robot = add_robot_to_scene(world)

    # Add sensors to the robot
    camera = add_camera_sensor(world, "/World/Robot")
    lidar = add_lidar_sensor(world, "/World/Robot")

    # Reset the world to initialize physics
    world.reset()

    # Define a target position for the robot
    target_position = np.array([2.0, 2.0, 0.0])

    # Run the simulation with control
    reached_target = False
    for i in range(1000):
        world.step(render=True)

        if not reached_target:
            reached_target = simple_move_robot(robot, world, target_position)

        if i % 30 == 0:  # Capture camera data every 30 steps
            camera_data = camera.get_rgb()
            if camera_data is not None:
                print(f"Captured image at step {i}")

        if i % 20 == 0:  # Capture LiDAR data every 20 steps
            lidar_data = lidar.get_linear_depth_data()
            if lidar_data is not None:
                print(f"Captured LiDAR data at step {i}")

        if i % 100 == 0:
            current_pos = robot.get_world_pose()[0]
            print(f"Step {i}: Robot position: {current_pos}")

    # Clean up
    world.clear()
```

## Task 5: Advanced Scene Configuration

### Step 1: Create a More Complex Environment
Create a more interesting environment with multiple objects and obstacles:

```python
def create_complex_environment(world):
    """Create a more complex environment with various objects"""

    # Add ground plane with texture
    world.scene.add_default_ground_plane()

    # Add walls to create an enclosed area
    wall_positions = [
        (0, 4, 1),   # North wall
        (0, -4, 1),  # South wall
        (4, 0, 1),   # East wall
        (-4, 0, 1)   # West wall
    ]

    wall_orientations = [
        (0, 0, 0, 1),      # North wall - no rotation
        (0, 0, 0, 1),      # South wall - no rotation
        (0, 0, 0.707, 0.707),  # East wall - 90 degree rotation around Z
        (0, 0, 0.707, 0.707)   # West wall - 90 degree rotation around Z
    ]

    walls = []
    for i, (pos, orient) in enumerate(zip(wall_positions, wall_orientations)):
        wall = world.scene.add(
            DynamicCuboid(
                prim_path=f"/World/Wall{i}",
                name=f"wall_{i}",
                position=np.array([pos[0], pos[1], pos[2]]),
                size=np.array([8.0, 0.2, 2.0]),
                color=np.array([0.5, 0.5, 0.5]),
                mass=1000.0  # Make walls heavy so they don't move
            )
        )
        walls.append(wall)

    # Add some obstacles in the environment
    obstacles = []
    obstacle_positions = [
        (1.5, 1.5, 0.3),
        (-1.5, -1.5, 0.3),
        (2.0, -2.0, 0.3),
        (-2.0, 2.0, 0.3)
    ]

    for i, pos in enumerate(obstacle_positions):
        obstacle = world.scene.add(
            DynamicCuboid(
                prim_path=f"/World/Obstacle{i}",
                name=f"obstacle_{i}",
                position=np.array([pos[0], pos[1], pos[2]]),
                size=0.4,
                color=np.array([0.8, 0.6, 0.2])
            )
        )
        obstacles.append(obstacle)

    # Add a goal marker
    goal = world.scene.add(
        DynamicCuboid(
            prim_path="/World/Goal",
            name="goal",
            position=np.array([3.0, 3.0, 0.2]),
            size=0.3,
            color=np.array([0.1, 0.8, 0.1])  # Green for goal
        )
    )

    return walls, obstacles, [goal]

# Complete implementation of the full lab
def main():
    print("Starting Isaac Sim Lab 9: First Isaac Sim Environment")

    # Initialize Isaac Sim
    world = World(stage_units_in_meters=1.0)
    world.scene.add_default_ground_plane()

    # Create complex environment
    walls, obstacles, goal = create_complex_environment(world)

    # Add robot to the scene
    robot = world.scene.add(
        Robot(
            prim_path="/World/Robot",
            name="simple_robot",
            usd_path="/Isaac/Robots/Carter/carter_model.usd",
            position=np.array([0.0, 0.0, 0.5]),
            orientation=np.array([0.0, 0.0, 0.0, 1.0])
        )
    )

    # Add sensors to the robot
    camera = Camera(
        prim_path="/World/Robot/camera",
        position=np.array([0.2, 0.0, 0.1]),
        frequency=30,
        resolution=(640, 480)
    )
    world.scene.add(camera)

    lidar = LidarRtx(
        prim_path="/World/Robot/Lidar",
        name="Lidar_Sensor",
        translation=np.array([0.0, 0.0, 0.3]),
        orientation=np.array([0, 0.0, 0.0, 1.0]),
        config="Example_Rotary_Lidar",
        depth_range=20.0,
        frequency=20,
        horizontal_resolution=0.5,
        vertical_resolution=0.5,
        horizontal_fov=360,
        vertical_fov=30
    )
    world.scene.add(lidar)

    # Reset the world to initialize physics
    world.reset()

    # Define a target position for the robot
    target_position = np.array([3.0, 3.0, 0.0])

    # Run the simulation with control
    reached_target = False
    for i in range(2000):  # Run for 2000 steps
        world.step(render=True)

        # Simple navigation - move toward target
        if not reached_target:
            current_pos = robot.get_world_pose()[0]
            direction = target_position - current_pos[:2]  # Only X,Y for 2D navigation
            distance = np.linalg.norm(direction)

            if distance > 0.5:  # If not close enough to target
                direction = direction / distance  # Normalize
                # In a real implementation, you would command the robot's motors here
                print(f"Step {i}: Moving toward target, distance: {distance:.2f}")
            else:
                reached_target = True
                print(f"Step {i}: Reached target!")

        # Capture sensor data periodically
        if i % 60 == 0:  # Every 2 seconds at 30Hz
            camera_data = camera.get_rgb()
            if camera_data is not None:
                print(f"Step {i}: Captured RGB image")

        if i % 40 == 0:  # Every 2 seconds at 20Hz
            lidar_data = lidar.get_linear_depth_data()
            if lidar_data is not None:
                print(f"Step {i}: Captured LiDAR data with {len(lidar_data)} points")

        # Print robot position periodically
        if i % 100 == 0:
            current_pos = robot.get_world_pose()[0]
            print(f"Step {i}: Robot at position ({current_pos[0]:.2f}, {current_pos[1]:.2f}, {current_pos[2]:.2f})")

    print("Lab 9 completed successfully!")

    # Clean up
    world.clear()

if __name__ == "__main__":
    main()
```

## Task 6: Testing and Validation

### Step 1: Run the Simulation
1. Execute your complete script
2. Observe the robot in the Isaac Sim viewer
3. Verify that the robot moves toward the target
4. Check that sensor data is being captured

### Step 2: Validate Sensor Data
1. Verify that camera images are being captured
2. Check that LiDAR data is being generated
3. Confirm that the data shapes match expectations

### Step 3: Performance Analysis
1. Monitor simulation performance (frames per second)
2. Check for any physics instabilities
3. Validate that objects behave as expected

## Challenge Tasks

### Challenge 1: Add More Complex Navigation
Modify the robot controller to implement a simple path planning algorithm that avoids obstacles while navigating to the target.

### Challenge 2: Sensor Fusion
Combine data from both the camera and LiDAR sensors to create a more comprehensive understanding of the environment.

### Challenge 3: ROS2 Integration
Connect your Isaac Sim environment to ROS2 and publish sensor data to ROS topics.

## Troubleshooting

### Common Issues and Solutions

1. **Isaac Sim won't start**
   - Verify GPU drivers and CUDA installation
   - Check Omniverse connection and licensing
   - Ensure sufficient system resources

2. **Physics instabilities**
   - Reduce time step size
   - Increase solver iterations
   - Check mass and inertia properties of objects

3. **Sensor data not capturing**
   - Verify sensor configuration parameters
   - Check that sensors are properly attached to the robot
   - Ensure the simulation is running when capturing data

4. **Performance issues**
   - Reduce scene complexity
   - Lower sensor resolutions
   - Adjust physics parameters

## Summary

In this lab, you have successfully:
- Set up an Isaac Sim environment
- Created a complex scene with multiple objects
- Added a robot with camera and LiDAR sensors
- Implemented basic navigation control
- Validated sensor data capture

This foundation provides the basis for more advanced robotics simulations and AI development using Isaac Sim's powerful capabilities.

## Next Steps

After completing this lab, you can:
- Explore more complex robot models and environments
- Implement advanced control algorithms
- Integrate with ROS2 for real-world robotics applications
- Use Isaac Sim for AI training and synthetic data generation