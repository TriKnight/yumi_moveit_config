# 🤖 ABB YuMi ROS 2 + MoveIt 2 Integration  

This repository provides a complete ROS 2 + MoveIt 2 configuration for the ABB YuMi dual-arm collaborative robot.  

It includes:  
- **URDF / SRDF** robot description  
- **ROS 2 Control** setup (`yumi_control.launch.py`)  
- **MoveIt 2** setup (`yumi_moveit.launch.py`)  
- **Unified launch** (`yumi.launch.py`) to start both control & planning  

With this, you can simulate YuMi in RViz **or** connect to the real hardware.  

---

## 📦 Features  

- Dual-arm support (`left_arm`, `right_arm`, and `both_arms`)  
- Gripper control (ROS 2 position controllers)  
- MoveIt 2 motion planning with OMPL  
- Works in simulation (`use_fake_hardware:=true`)  
- Real robot support (`use_fake_hardware:=false`)  

---

## 🚀 Installation  

### 1. Clone into your workspace  

```bash
cd ~/colcon_ws/src
git clone https://github.com/TriKnight/yumi_moveit_config.git
```
### 2. Install dependencies and build
```bash
sudo apt update
rosdep install --from-paths src --ignore-src -r -y
colcon build
```

## 🚀 Launch files
### 1. Control only – yumi_control.launch.py
```bash
ros2 launch yumi_moveit_config yumi_control.launch.py use_fake_hardware:=true
```

### 2. MoveIt only – yumi_moveit.launch.py
```bash
ros2 launch yumi_moveit_config yumi_moveit.launch.py launch_rviz:=true

```
### 3. Combined launch – yumi.launch.py
```bash
ros2 launch yumi_moveit_config yumi.launch.py

```
