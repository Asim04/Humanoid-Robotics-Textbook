---
sidebar_position: 3
---

# Hardware Requirements & Setup

This document outlines the hardware requirements for the Physical AI & Humanoid Robotics course, including options for simulation and physical platforms.

## Minimum System Requirements

### For Simulation Only
- **CPU**: Intel i7-10700K or AMD Ryzen 7 3700X (8 cores/16 threads)
- **RAM**: 32GB DDR4
- **GPU**: NVIDIA RTX 4070 Ti (12GB VRAM) or better
- **Storage**: 500GB SSD
- **OS**: Ubuntu 22.04 LTS or Windows 11 with WSL2

### For Physical Robot Development
- **Minimum as above** for simulation and development
- **Robot Platform**: NVIDIA Jetson Orin Nano Developer Kit
- **Sensors**: Intel RealSense D435i depth camera
- **Additional**: IMU sensors, motor controllers as specified in lab exercises

## Recommended Development Platforms

### NVIDIA Jetson Orin Nano
- 1024 CUDA cores
- 8GB or 16GB LPDDR5 memory
- 2.5 TFLOPS AI performance
- Perfect for edge AI and robotics applications

### Alternative Platforms
- **UP2 Board**: Intel Celeron J4105 with Movidius Neural Compute Stick
- **Raspberry Pi 5**: For lightweight applications
- **Custom PC**: For simulation-heavy development

## Sensor Requirements

### Essential Sensors
- **Depth Camera**: Intel RealSense D435i or equivalent
- **IMU**: 9-axis sensor for orientation
- **LiDAR**: RPLIDAR A2 or similar for navigation (optional for basic setup)

### Additional Sensors (Advanced Labs)
- Thermal camera
- Force/torque sensors
- GPS module (for outdoor applications)

## Setup Checklist

- [ ] System meets minimum requirements
- [ ] GPU drivers installed (NVIDIA drivers for CUDA)
- [ ] Docker installed and configured
- [ ] ROS 2 Humble Hawksbill installed
- [ ] Simulation environment tested
- [ ] Physical hardware (if applicable) connected and tested

## Troubleshooting Common Issues

### GPU Performance
- Ensure latest NVIDIA drivers are installed
- Verify CUDA compatibility with ROS 2 packages
- Monitor thermal performance during intensive simulations

### Sensor Integration
- Check USB permissions for sensor devices
- Verify sensor calibration files
- Test sensor streams independently before integration

For detailed setup instructions, refer to the [Software Installation Guide](./software-installation.md).