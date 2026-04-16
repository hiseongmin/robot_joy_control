# Dual Control System: Eye Modules + Robot Head

Complete guide for controlling eye display modules and robot head simultaneously with a single joystick.

## 📋 System Overview

This system allows coordinated control of:
- **Eye Display Modules** (2x OLED displays with gaze tracking)
- **Robot Head** (NEXTAGE or similar robots with head joints)

Using a single gamepad:
- **Left Stick**: Eye gaze control
- **Right Stick**: Robot head movement
- **Buttons**: Eye expressions

## 🔧 Prerequisites

### Hardware Requirements
- 2x Eye Display Modules (ESP32-based with OLED)
- USB Gamepad/Joystick (tested with Xbox/PS4 controllers)
- Robot with ROS-compatible head control (NEXTAGE, PR2, etc.)

### Software Requirements
```bash
# ROS packages
sudo apt-get install ros-noetic-joy ros-noetic-rosserial-python

# Eye display package (from JSK)
cd ~/catkin_ws/src
git clone https://github.com/jsk-ros-pkg/jsk_3rdparty.git
```

## ⚙️ Configuration

### 1. Eye Module Serial Numbers

The system auto-detects eye modules by serial number. If your modules have different serial numbers, update them in the scripts:

```bash
# Check your module serial numbers
for dev in /dev/ttyACM*; do
    echo "Device: $dev"
    sudo udevadm info "$dev" | grep ID_SERIAL_SHORT
done
```

Update serial numbers in `2_eye_modules.sh` or `auto_detect_eyes.sh`:
```bash
SERIAL_LEFT="YOUR_LEFT_SERIAL"
SERIAL_RIGHT="YOUR_RIGHT_SERIAL"
```

### 2. Robot Network Configuration

For remote robot control, update IP addresses in `4_robot_head.sh`:
```bash
export ROS_MASTER_URI=http://YOUR_ROBOT_IP:11311
export ROS_IP=YOUR_LOCAL_IP
```

## 🚀 Running the System

### Method 1: Four Terminal Setup (Recommended for debugging)

Open 4 terminals and run in order:

**Terminal 1 - ROS Master:**
```bash
./1_roscore.sh
```

**Terminal 2 - Eye Modules:**
```bash
./2_eye_modules.sh
```
This handles serial communication with eye modules.

**Terminal 3 - Joystick + Eye Control:**
```bash
./3_eye_joystick.sh
```
This runs:
- `joy_node` (joystick driver)
- Eye gaze control nodes (left stick)
- Expression control (buttons)

**Terminal 4 - Robot Head Control:**
```bash
./4_robot_head.sh
```
This subscribes to the existing `/joy` topic for right stick control.

### Method 2: All-in-One (Simple but less flexible)
```bash
./all_in_one.sh        # Standard speed
# or
./all_in_one_fast.sh   # Optimized for minimal latency
```

## 🎮 Control Mapping

| Input | Function | Details |
|-------|----------|---------|
| **Left Stick X** | Eye gaze horizontal | Both eyes move together |
| **Left Stick Y** | Eye gaze vertical | Both eyes move together |
| **Right Stick X** | Robot head yaw | Left/right rotation |
| **Right Stick Y** | Robot head pitch | Up/down tilt |
| **Button 0 (A/X)** | Normal expression | Default eye shape |
| **Button 1 (B/○)** | Blink | Quick blink animation |
| **Button 2 (X/□)** | Surprised | Wide eyes |
| **Button 3 (Y/△)** | Sleepy | Half-closed eyes |
| **Button 4 (LB)** | Angry | Furrowed expression |
| **Button 5 (RB)** | Sad | Droopy eyes |
| **Button 6 (Back)** | Happy | Smiling eyes |

## ⚠️ Important: Avoiding Conflicts

### Joy Node Management

The system uses a **single joy_node** instance to avoid conflicts:

1. **Terminal 3** launches `joy_node` for local control (eyes)
2. **Terminal 4** only subscribes to the existing `/joy` topic
3. Never run multiple `joy_node` instances!

### Checking for Conflicts
```bash
# Check if joy_node is already running
rosnode list | grep joy

# Kill duplicate nodes if necessary
rosnode kill /duplicate_joy_node
```

### Topic Namespaces

Eye modules use namespaces to avoid conflicts:
- Left eye: `/left/eye_display/*`
- Right eye: `/right/eye_display/*`
- Robot head: `/head_controller/command`

## 🔧 Tuning Performance

### For Faster Robot Response

Edit `4_robot_head.sh` or use the tuning script:

```bash
# Interactive tuning
./tune_robot_head.sh

# Or edit parameters directly:
_move_duration:=0.05   # Faster movement (default: 0.3)
_rate:=50.0           # Higher update rate (default: 20)
_snap_threshold:=0.01  # More sensitive (default: 0.05)
```

### Network Latency Test
```bash
./test_network_latency.sh
```

## 🤖 Robot-Specific Configuration

### NEXTAGE Robot
Current configuration in `4_robot_head.sh`:
```bash
export ROS_MASTER_URI=http://133.11.216.57:11311
export ROS_IP=133.11.216.68
```

### Other Robots

Create a new script based on `4_robot_head.sh`:

```bash
cp 4_robot_head.sh 4_robot_head_YOUR_ROBOT.sh
```

Update:
1. ROS_MASTER_URI and ROS_IP
2. Topic name (if different from `/head_controller/command`)
3. Joint names (if different from HEAD_JOINT0/1)
4. Axis mapping if needed

### PR2 Example
```bash
# Change topic
/head_traj_controller/command

# Change joint names
["head_pan_joint", "head_tilt_joint"]
```

## 🐛 Troubleshooting

### Eye modules not detected
```bash
# Check connections
ls /dev/ttyACM*

# Fix permissions
sudo chmod 666 /dev/ttyACM*

# Check serial numbers
sudo udevadm info /dev/ttyACM0 | grep SERIAL
```

### Joystick not working
```bash
# Check device
ls /dev/input/js*

# Test joystick
jstest /dev/input/js0
```

### Robot not responding
```bash
# Test network
ping YOUR_ROBOT_IP

# Check ROS connection
rostopic list
rostopic echo /head_controller/command
```

### Duplicate joy_node error
```bash
# Find and kill duplicates
rosnode list | grep joy
rosnode kill /joy_node_duplicate
```

## 📚 Architecture

```
┌─────────────┐
│  Joystick   │
└──────┬──────┘
       │ /joy topic
       ▼
┌──────────────────────────────┐
│        joy_node              │
│   (Terminal 3 - Local)       │
└──────┬───────────────────────┘
       │
       ├─── Left Stick ──→ Eye Control Nodes ──→ Serial ──→ Eye Modules
       │                     (Terminal 3)                   (Terminal 2)
       │
       └─── Right Stick ──→ Robot Head Node ──→ Network ──→ Robot
                             (Terminal 4)

```

## 🔗 Integration with Eye Module Repository

This system is designed to work with the [eye_display package](https://github.com/jsk-ros-pkg/jsk_3rdparty/tree/master/eye_display).

To use with your custom eye module repository:

1. Ensure your package provides these topics:
   - `/left/eye_display/look_at` (geometry_msgs/Point)
   - `/right/eye_display/look_at` (geometry_msgs/Point)
   - `/left/eye_display/eye_status` (std_msgs/String)
   - `/right/eye_display/eye_status` (std_msgs/String)

2. Update the launch file paths in `2_eye_modules.sh` if needed

## 📄 License

BSD 3-Clause License

## 👥 Contributors

- Original eye_display package by JSK Robotics Lab
- Dual control integration by hiseongmin