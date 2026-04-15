# Robot Joy Control

ROS package for controlling NEXTAGE robot head and dual eye display modules with a single joystick.

## 🎮 Overview

This package enables simultaneous control of:
- **NEXTAGE robot head movement** (2 DOF: yaw/pitch)
- **Dual eye display modules** (gaze direction + expressions)

Using a single gamepad/joystick with intuitive mapping:
- **Left stick**: Eye gaze control
- **Right stick**: Robot head control
- **Buttons**: Eye expressions

## 📦 Dependencies

```bash
# ROS packages
sudo apt-get install ros-noetic-joy ros-noetic-rosserial-python

# Eye display module (from JSK 3rdparty)
cd ~/catkin_ws/src
git clone https://github.com/jsk-ros-pkg/jsk_3rdparty.git
```

## 🚀 Installation

```bash
cd ~/catkin_ws/src
git clone https://github.com/hiseongmin/robot_joy_control.git
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

## ⚙️ Network Configuration

### Option 1: Using script with arguments
```bash
# Auto-detect local IP
./scripts/start_demo.sh <ROBOT_IP>

# Specify both IPs
./scripts/start_demo.sh <ROBOT_IP> <LOCAL_IP>

# Example
./scripts/start_demo.sh 192.168.1.100
./scripts/start_demo.sh 192.168.1.100 192.168.1.50
```

### Option 2: Using config file
```bash
# Copy and edit config
cd ~/catkin_ws/src/robot_joy_control
cp config/network_config.yaml.example config/network_config.yaml
# Edit network_config.yaml with your robot's IP
```

### Option 3: Manual setup
```bash
export ROS_MASTER_URI=http://<ROBOT_IP>:11311
export ROS_IP=<YOUR_LOCAL_IP>
roslaunch robot_joy_control remote_nextage_with_eyes.launch
```

## 🔧 Hardware Setup

1. **Connect devices:**
   - Joystick/Gamepad → USB port (usually `/dev/input/js0`)
   - Left eye module → USB serial (usually `/dev/ttyACM0`)
   - Right eye module → USB serial (usually `/dev/ttyACM1`)

2. **Check connections:**
```bash
# List joystick devices
ls /dev/input/js*

# List serial ports
ls /dev/ttyACM* /dev/ttyUSB*
```

3. **Set permissions (if needed):**
```bash
sudo chmod 666 /dev/ttyACM*
```

## 📝 Usage

### Basic Launch (NEXTAGE + Dual Eyes)

```bash
roslaunch robot_joy_control nextage_with_eyes_dual.launch
```

### Custom Ports

```bash
roslaunch robot_joy_control nextage_with_eyes_dual.launch \
    port_left:=/dev/ttyUSB0 \
    port_right:=/dev/ttyUSB1 \
    joy_dev:=/dev/input/js1
```

### Test Individual Components

```bash
# Test only NEXTAGE head control
roslaunch robot_joy_control nextage_head.launch

# Test only eye displays
roslaunch eye_display demo_dual.launch
```

## 🎮 Control Mapping

| Control | Function |
|---------|----------|
| **Left Stick** | |
| Horizontal (axis 0) | Eye gaze left/right |
| Vertical (axis 1) | Eye gaze up/down |
| **Right Stick** | |
| Horizontal (axis 3) | Robot head yaw (left/right) |
| Vertical (axis 4) | Robot head pitch (up/down) |
| **Buttons** | |
| Button 0 | Normal expression |
| Button 1 | Blink |
| Button 2 | Surprised |
| Button 3 | Sleepy |
| Button 4 | Angry |
| Button 5 | Sad |
| Button 6 | Happy |

## 📊 ROS Topics

### Published Topics
- `/head_controller/command` (trajectory_msgs/JointTrajectory)
  - NEXTAGE head joint commands

### Subscribed Topics
- `/joy` (sensor_msgs/Joy)
  - Joystick input

### Eye Display Topics (via eye_display package)
- `/left/eye_display/look_at` (geometry_msgs/Point)
- `/left/eye_display/eye_status` (std_msgs/String)
- `/right/eye_display/look_at` (geometry_msgs/Point)
- `/right/eye_display/eye_status` (std_msgs/String)

## 🔍 Debugging

Monitor topics:
```bash
# Check joystick input
rostopic echo /joy

# Monitor head commands
rostopic echo /head_controller/command

# Watch eye status
rostopic echo /left/eye_display/eye_status
rostopic echo /right/eye_display/look_at
```

Test individual controls:
```bash
# Test head movement
rostopic pub -1 /head_controller/command trajectory_msgs/JointTrajectory \
  '{joint_names: ["HEAD_JOINT0", "HEAD_JOINT1"], points: [{positions: [0.5, 0.3], time_from_start: {secs: 1}}]}'

# Test eye expression
rostopic pub -1 /left/eye_display/eye_status std_msgs/String "data: 'happy'"
```

## 📹 Demo Video Recording

To record a demo showing coordinated eye and head movements:

1. Start all nodes:
```bash
roslaunch robot_joy_control nextage_with_eyes_dual.launch
```

2. Demonstration sequence:
   - Move head while keeping eyes centered
   - Track objects with eyes while head is stationary
   - Coordinate head and eye movements together
   - Show various expressions during movements

## 🏗️ Architecture

This package integrates:
- **robot_joy_control**: NEXTAGE head control
- **eye_display** (jsk_3rdparty): Dual eye module control
- **joy**: ROS joystick driver

The launch file coordinates these components to enable simultaneous control through a single joystick interface.

## 📄 License

BSD 3-Clause License

## 👥 Contributors

- hiseongmin (ye)
- Based on eye_display from JSK Robotics Lab

## 🔗 Related Packages

- [jsk_3rdparty/eye_display](https://github.com/jsk-ros-pkg/jsk_3rdparty/tree/master/eye_display)
- [nextage_ros](http://wiki.ros.org/nextage_ros)