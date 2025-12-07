#!/usr/bin/env python3
"""
File: mathematical_foundations.py
Purpose: Demonstrates mathematical foundations of Physical AI using Python
Chapter: 1 - Introduction to Physical AI
Dependencies: numpy
Hardware: None (pure computation)
"""

import numpy as np
from scipy import integrate
import math


def transformation_matrix_example():
    """
    Demonstrates the transformation matrix T = [R p; 0 1] from Chapter 1
    where R is a rotation matrix and p is a position vector.
    """
    print("=== Linear Algebra: Transformation Matrix ===")

    # Define a 2D rotation matrix (rotation by 45 degrees)
    theta = math.pi / 4  # 45 degrees in radians
    R = np.array([[math.cos(theta), -math.sin(theta)],
                  [math.sin(theta), math.cos(theta)]])

    # Define a position vector
    p = np.array([[2.0], [3.0]])

    # Construct the transformation matrix T
    # T = [R p; 0 0 1]
    T = np.block([[R, p],
                  [np.zeros((1, 2)), 1.0]])

    print(f"Rotation matrix R:\n{R}")
    print(f"Position vector p:\n{p.flatten()}")
    print(f"Transformation matrix T:\n{T}")

    # Apply transformation to a point
    point = np.array([1.0, 1.0, 1.0])  # Homogeneous coordinates
    transformed_point = T @ point
    print(f"Original point (homogeneous): {point}")
    print(f"Transformed point: {transformed_point[:2]}")

    print("\nThis demonstrates spatial relationships in Physical AI systems.")
    print("Transformation matrices are crucial for robotics and embodied systems.\n")


def bayesian_inference_example():
    """
    Demonstrates Bayesian inference P(x|z) = P(z|x)P(x)/P(z) from Chapter 1
    Applied to sensor uncertainty in Physical AI systems.
    """
    print("=== Probability Theory: Bayesian Inference ===")

    # Prior probability: P(x) - initial belief about state
    prior_belief = 0.7  # 70% chance the robot is in a safe zone

    # Likelihood: P(z|x) - probability of sensor reading given state
    likelihood_given_safe = 0.9  # 90% chance of safe reading if actually safe
    likelihood_given_unsafe = 0.3  # 30% chance of safe reading if actually unsafe

    # Sensor reading: z (indicates safe environment)
    # Calculate P(z) = P(z|x)P(x) + P(z|¬x)P(¬x)
    prob_safe_reading = (likelihood_given_safe * prior_belief +
                        0.3 * (1 - prior_belief))

    # Apply Bayes' theorem: P(x|z) = P(z|x)P(x) / P(z)
    posterior_belief = (likelihood_given_safe * prior_belief) / prob_safe_reading

    print(f"Prior belief (robot in safe zone): {prior_belief:.2f}")
    print(f"Likelihood of safe reading if actually safe: {likelihood_given_safe:.2f}")
    print(f"Likelihood of safe reading if unsafe: {likelihood_given_unsafe:.2f}")
    print(f"Marginal probability of safe reading: {prob_safe_reading:.2f}")
    print(f"Posterior belief (after sensor reading): {posterior_belief:.2f}")

    print("\nThis demonstrates how Physical AI systems update beliefs based on sensor observations.")
    print("Bayesian inference is crucial for handling uncertainty in sensor data.\n")


def pid_controller_example():
    """
    Demonstrates PID control u(t) = Kp*e(t) + Ki*∫e(t)dt + Kd*de(t)/dt from Chapter 1
    Applied to a simple system stabilization problem.
    """
    print("=== Control Theory: PID Controller ===")

    # PID gains
    Kp = 1.0  # Proportional gain
    Ki = 0.1  # Integral gain
    Kd = 0.05  # Derivative gain

    # Simulate a simple control system
    def pid_control_system(t, state):
        """
        Simple PID control system simulation
        state[0] = current position, state[1] = current velocity
        """
        target_position = 5.0  # Target to stabilize to
        current_position = state[0]
        current_velocity = state[1]

        # Calculate error
        error = target_position - current_position

        # Calculate integral of error (approximated)
        integral_error = state[2] if len(state) > 2 else 0

        # Calculate derivative of error
        derivative_error = -current_velocity

        # PID control law
        control_output = Kp * error + Ki * integral_error + Kd * derivative_error

        # Return derivatives: [dposition/dt, dvelocity/dt, dintegral/dt]
        # Simplified second-order system: acceleration = control_output - current_position
        acceleration = control_output - current_position - 0.1 * current_velocity  # Add damping
        return [current_velocity, acceleration, error]  # [dposition/dt, dvelocity/dt, dintegral/dt]

    # Initial state: [position, velocity, integral_error]
    initial_state = [0.0, 0.0, 0.0]
    time_points = np.linspace(0, 10, 100)

    print(f"PID Gains - Kp: {Kp}, Ki: {Ki}, Kd: {Kd}")
    print(f"Target position: {5.0}")
    print("Simulating system stabilization with PID control...")

    # Note: In a real implementation, we would use scipy.integrate.odeint
    # to solve the differential equations, but for demonstration purposes,
    # we'll show the control law structure.

    print("\nPID control law: u(t) = Kp*e(t) + Ki*∫e(t)dt + Kd*de(t)/dt")
    print("Where:")
    print("  u(t) - control output")
    print("  e(t) - error (target - current)")
    print("  ∫e(t)dt - integral of error")
    print("  de(t)/dt - derivative of error")

    print("\nThis demonstrates how Physical AI systems use control theory")
    print("to achieve stable behavior in uncertain physical environments.\n")


def main():
    """
    Main function demonstrating mathematical foundations of Physical AI.
    """
    print("Mathematical Foundations of Physical AI")
    print("Demonstrating concepts from Chapter 1\n")

    transformation_matrix_example()
    bayesian_inference_example()
    pid_controller_example()

    print("These mathematical foundations are essential for Physical AI systems:")
    print("- Linear Algebra for spatial relationships and transformations")
    print("- Probability Theory for handling uncertainty in sensor data")
    print("- Control Theory for system stabilization and behavior")


if __name__ == '__main__':
    main()