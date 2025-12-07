---
sidebar_position: 4
---

# Software Installation Guide

This guide provides step-by-step instructions for installing the required software stack for the Physical AI & Humanoid Robotics course.

## Prerequisites

- Ubuntu 22.04 LTS (recommended) or Windows 11 with WSL2
- Administrative access to install software
- Stable internet connection for package downloads
- At least 20GB of free disk space

## ROS 2 Installation (Humble Hawksbill)

### On Ubuntu 22.04

1. Set locale:
```bash
locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
```

2. Add ROS 2 apt repository:
```bash
sudo apt update && sudo apt install -y curl gnupg lsb-release
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

3. Install ROS 2 packages:
```bash
sudo apt update
sudo apt install ros-humble-desktop
sudo apt install ros-humble-cv-bridge ros-humble-vision-opencv ros-humble-image-transport
sudo apt install python3-colcon-common-extensions python3-rosdep python3-vcstool
```

4. Initialize rosdep:
```bash
sudo rosdep init
rosdep update
```

5. Source ROS 2 environment:
```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## NVIDIA Isaac Sim Installation

1. Download NVIDIA Isaac Sim from [NVIDIA Developer Portal](https://developer.nvidia.com/isaac-sim)
2. Follow the installation guide for your platform
3. Ensure your GPU drivers support OpenGL 4.5 or Vulkan

### Prerequisites for Isaac Sim:
- NVIDIA GPU with CUDA support
- Updated GPU drivers (495.44 or later)
- OpenGL 4.5 or Vulkan support

## Python Environment Setup

1. Install Python 3.10+ and pip:
```bash
sudo apt install python3.10 python3.10-venv python3-pip
```

2. Create a virtual environment:
```bash
python3 -m venv ~/ros2_venv
source ~/ros2_venv/bin/activate
pip install --upgrade pip
```

3. Install required Python packages:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install tensorflow
pip install opencv-python
pip install numpy scipy matplotlib
pip install openai anthropic
```

## Docker Installation

1. Install Docker:
```bash
sudo apt install docker.io
sudo usermod -aG docker $USER
```

2. Install Docker Compose:
```bash
sudo apt install docker-compose-v2
```

## Git Configuration

1. Configure Git:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global core.editor "nano"
```

2. Set up SSH keys for GitHub:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

## Testing Your Installation

1. Test ROS 2:
```bash
source /opt/ros/humble/setup.bash
ros2 run demo_nodes_cpp talker
```

2. Test Python packages:
```bash
python3 -c "import rclpy; import cv2; import torch; print('All packages imported successfully')"
```

## Troubleshooting

### Common Issues:

1. **ROS 2 command not found**: Make sure to source the ROS 2 environment in each terminal or add it to your `.bashrc`.

2. **Permission errors**: Ensure you've added your user to the `docker` group and logged out/in.

3. **CUDA not detected**: Verify GPU drivers and install CUDA toolkit if needed.

4. **Python package conflicts**: Use virtual environments to isolate dependencies.

## Verification Checklist

- [ ] ROS 2 Humble installed and sourced
- [ ] Python virtual environment set up
- [ ] Required Python packages installed
- [ ] Docker installed and user added to docker group
- [ ] Git configured with SSH keys
- [ ] Basic ROS 2 commands working
- [ ] Python packages importing correctly

For additional help, refer to the [Learning Path Navigator](./learning-path-navigator.md) for next steps.