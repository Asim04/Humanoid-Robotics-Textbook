# Physical AI & Humanoid Robotics Textbook

Welcome to the Physical AI & Humanoid Robotics textbook project! This comprehensive educational resource covers modern robotics concepts, from foundational principles to advanced simulation and AI integration.

## Project Overview

This textbook project provides a complete curriculum for learning robotics with a focus on:
- Physical AI principles and applications
- Robot simulation environments (Gazebo, Unity, Isaac Sim)
- ROS2 integration and development
- Advanced robotics concepts and humanoid robotics

## Table of Contents

### Part I: Foundations
- Chapter 1: Introduction to Physical AI
- Chapter 2: Mathematical Foundations for Robotics

### Part II: ROS Fundamentals
- Chapter 3: ROS2 Architecture and Concepts
- Chapter 4: Nodes, Topics, and Services
- Chapter 5: Robot Control and Navigation

### Part III: Simulation
- Chapter 6: Gazebo Classic & Fortress
- Chapter 7: Advanced Simulation Techniques
- Chapter 8: Unity for Robot Visualization

### Part IV: Isaac Sim
- Chapter 9: NVIDIA Isaac Sim

### Part V: Humanoid Robotics
- (Coming soon)

### Part VI: Vision-Language-Action Models
- (Coming soon)

## Labs

Practical hands-on labs accompany each major section:
- Lab 3: ROS2 Basics
- Lab 4: Robot Control with ROS2
- Lab 5: Navigation and Path Planning
- Lab 6: Simulating a Robot in Gazebo
- Lab 7: Complex Environment Simulation
- Lab 8: Unity Visualization Pipeline
- Lab 9: First Isaac Sim Environment

## Getting Started

### Prerequisites

- **System Requirements:**
  - Modern CPU with multi-core support
  - 16GB+ RAM (32GB recommended)
  - NVIDIA GPU with RTX technology for Isaac Sim (RTX 3080 or higher recommended)
  - 100GB+ free disk space

- **Software Requirements:**
  - Ubuntu 22.04 LTS or Windows 10/11
  - ROS2 Humble Hawksbill
  - NVIDIA Omniverse (for Isaac Sim)
  - Unity 2021.3 LTS or later (for Unity integration)
  - Git and Git LFS
  - Node.js and npm/yarn

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd physical-ai-robotics-textbook
   git lfs pull
   ```

2. **Install project dependencies:**
   ```bash
   cd website
   npm install
   ```

3. **For ROS2 integration:**
   ```bash
   # Follow the ROS2 installation guide for your platform
   # Install required ROS2 packages
   sudo apt install ros-humble-desktop ros-humble-gazebo-ros-pkgs
   ```

4. **For Isaac Sim:**
   - Download and install NVIDIA Omniverse
   - Install Isaac Sim extension
   - Install Isaac ROS packages

5. **For Unity integration:**
   - Install Unity Hub and Unity 2021.3 LTS
   - Import Unity Robotics Hub package
   - Set up Unity-ROS2 bridge

### Running the Documentation Site

The textbook is built with Docusaurus and can be run locally:

```bash
cd website
npm start
```

This will start a local development server at `http://localhost:3000`.

### Project Structure

```
website/
├── blog/                    # Blog posts and updates
├── docs/                    # Main textbook content
│   ├── part-i-foundations/  # Foundational concepts
│   ├── part-ii-ros-fundamentals/ # ROS2 fundamentals
│   ├── part-iii-simulation/ # Simulation environments
│   ├── part-iv-isaac/      # Isaac Sim content
│   ├── part-v-humanoid/    # Humanoid robotics
│   ├── part-vi-vla/        # Vision-Language-Action models
│   └── labs/               # Hands-on lab exercises
├── static/                 # Static assets (images, code examples)
│   ├── code/               # Code examples by chapter
│   └── img/                # Diagrams and illustrations
└── src/                    # Custom Docusaurus components
```

## Code Examples

Each chapter includes practical code examples organized by chapter:

- `website/static/code/chapter-6/` - Gazebo examples
- `website/static/code/chapter-7/` - Advanced simulation examples
- `website/static/code/chapter-8/` - Unity integration examples
- `website/static/code/chapter-9/` - Isaac Sim examples

## Contributing

We welcome contributions to improve the textbook! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please follow the existing style and structure of the content.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:

- Check the [Troubleshooting Guide](website/docs/appendices/troubleshooting-ros2.md)
- Open an issue in the repository
- Consult the ROS2 and Isaac Sim documentation

## Acknowledgments

- The Docusaurus team for the excellent documentation framework
- The ROS2 community for their extensive documentation and tools
- NVIDIA for Isaac Sim and the robotics ecosystem
- The open-source community for countless tools and libraries

---

Happy learning and building with Physical AI & Robotics!