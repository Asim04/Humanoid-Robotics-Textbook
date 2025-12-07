#!/usr/bin/env python3
"""
File: simulation_example.py
Purpose: Demonstrates simulation concepts in Physical AI
Chapter: 1 - Introduction to Physical AI
Dependencies: numpy, matplotlib (for visualization)
Hardware: None (simulation only)
"""

import numpy as np
import time
import random
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class PhysicalState:
    """
    Represents the state of a physical system in simulation
    """
    position: np.ndarray
    velocity: np.ndarray
    timestamp: float
    safety_status: str = "safe"


class PhysicalAISimulator:
    """
    A simple simulator demonstrating Physical AI concepts:
    - Safe testing environment
    - Rapid prototyping
    - Data generation
    - Validation before deployment
    """

    def __init__(self):
        self.current_state = PhysicalState(
            position=np.array([0.0, 0.0]),  # x, y coordinates
            velocity=np.array([0.1, 0.05]),  # velocity vector
            timestamp=time.time()
        )
        self.history: List[PhysicalState] = [self.current_state]
        self.environment_bounds = (-10.0, 10.0, -10.0, 10.0)  # xmin, xmax, ymin, ymax
        self.obstacles = [(2.0, 2.0, 1.0), (-3.0, -2.0, 1.5)]  # (x, y, radius)

    def update_state(self, dt: float = 0.1):
        """
        Update the physical state based on dynamics
        """
        # Add some randomness to simulate real-world uncertainty
        noise = np.random.normal(0, 0.01, size=2)

        # Update position based on velocity
        new_position = self.current_state.position + self.current_state.velocity * dt + noise

        # Simple boundary checking
        safety_status = self._check_safety(new_position)

        # Create new state
        new_state = PhysicalState(
            position=new_position,
            velocity=self.current_state.velocity + np.random.normal(0, 0.005, size=2),  # Add velocity noise
            timestamp=time.time(),
            safety_status=safety_status
        )

        self.current_state = new_state
        self.history.append(new_state)

        return new_state

    def _check_safety(self, position: np.ndarray) -> str:
        """
        Check if the position is safe (not near obstacles or outside bounds)
        """
        x, y = position

        # Check bounds
        xmin, xmax, ymin, ymax = self.environment_bounds
        if x < xmin or x > xmax or y < ymin or y > ymax:
            return "unsafe_boundary"

        # Check obstacles
        for obs_x, obs_y, obs_radius in self.obstacles:
            distance = np.sqrt((x - obs_x)**2 + (y - obs_y)**2)
            if distance < obs_radius:
                return "unsafe_obstacle"

        return "safe"

    def simulate_step(self):
        """
        Perform one simulation step and return the new state
        """
        new_state = self.update_state()

        print(f"Time: {new_state.timestamp:.2f}")
        print(f"Position: ({new_state.position[0]:.2f}, {new_state.position[1]:.2f})")
        print(f"Velocity: ({new_state.velocity[0]:.3f}, {new_state.velocity[1]:.3f})")
        print(f"Safety: {new_state.safety_status}")
        print("-" * 40)

        return new_state

    def run_simulation(self, steps: int = 20):
        """
        Run the simulation for a specified number of steps
        """
        print("Starting Physical AI Simulation...")
        print("Demonstrating: Safe testing, Rapid prototyping, Data generation, Validation")
        print("=" * 50)

        for i in range(steps):
            print(f"Step {i+1}:")
            self.simulate_step()

            # Add a small delay to simulate real-time processing
            time.sleep(0.05)

        print("Simulation completed.")
        print(f"Total steps: {steps}")
        print(f"Final position: ({self.current_state.position[0]:.2f}, {self.current_state.position[1]:.2f})")
        print(f"Path safety: {self.current_state.safety_status}")

        # Show some statistics
        positions = np.array([state.position for state in self.history])
        avg_position = np.mean(positions, axis=0)
        max_deviation = np.max(np.sqrt(np.sum((positions - avg_position)**2, axis=1)))

        print(f"Average position: ({avg_position[0]:.2f}, {avg_position[1]:.2f})")
        print(f"Max deviation from average: {max_deviation:.2f}")


def demonstrate_digital_vs_physical_ai():
    """
    Demonstrates the difference between Digital AI and Physical AI
    """
    print("=== Digital AI vs Physical AI Simulation ===")

    print("\nDigital AI Approach:")
    print("- Discrete inputs/outputs")
    print("- Simulated environments")
    print("- No physical constraints")
    print("- Deterministic behavior")
    print("- No safety concerns")

    print("\nPhysical AI Approach (simulated):")

    # Simulate Physical AI characteristics
    print("- Continuous sensor data: Position updates at regular intervals")
    print("- Real-world environments: Boundaries and obstacles")
    print("- Physics-based constraints: Velocity and position dynamics")
    print("- Probabilistic behavior: Random noise in system")
    print("- Safety requirements: Collision detection and boundary checking")

    # Example of Physical AI system
    simulator = PhysicalAISimulator()

    print(f"\nPhysical AI System initialized:")
    print(f"- Starting position: {simulator.current_state.position}")
    print(f"- Environment bounds: {simulator.environment_bounds}")
    print(f"- Obstacles: {len(simulator.obstacles)} detected")

    return simulator


def main():
    """
    Main function demonstrating simulation concepts in Physical AI.
    """
    print("Simulation Concepts in Physical AI")
    print("Demonstrating concepts from Chapter 1\n")

    # Demonstrate Digital vs Physical AI
    simulator = demonstrate_digital_vs_physical_ai()

    print("\n" + "="*50)
    print("RUNNING PHYSICAL AI SIMULATION")
    print("="*50)

    # Run the simulation
    simulator.run_simulation(steps=10)

    print("\n" + "="*50)
    print("SIMULATION COMPLETE")
    print("="*50)
    print("\nKey takeaways:")
    print("1. Simulation provides a safe testing environment")
    print("2. Enables rapid prototyping without hardware risk")
    print("3. Generates data for algorithm training")
    print("4. Validates system behavior before real-world deployment")
    print("5. Demonstrates real-time constraints and uncertainty handling")


if __name__ == '__main__':
    main()