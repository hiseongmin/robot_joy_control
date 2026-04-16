# 🤖 Robot Joy Control

ROS package for controlling NEXTAGE robot head and eye display modules using a joystick controller.

## ✨ Features

- **🎮 Dual Control**: Control both robot head and eye modules with single joystick
- **👀 Eye Modules**: Real-time eye gaze and expression control
- **🤖 Robot Head**: Smooth head movement with safety limits
- **🛡️ Safe Operation**: Command overflow prevention and smooth motion
- **🔧 Easy Setup**: Simple 4-terminal operation

## 📋 Prerequisites

- ROS Noetic
- NEXTAGE Robot
- Logitech F310 Gamepad (or compatible)
- Eye Display Modules (ESP32-based OLED)

## 🚀 Quick Start

### Installation

```bash
cd ~/catkin_ws/src
git clone https://github.com/hiseongmin/robot_joy_control.git
cd ~/catkin_ws
catkin_make
```

### Running the System

Open 4 terminals and run each command:

#### Terminal 1 - ROS Master
```bash
./1_roscore.sh
```

#### Terminal 2 - Eye Modules
```bash
./2_eye_modules.sh
```

#### Terminal 3 - Joystick Control
```bash
./3_joystick_both.sh
```

#### Terminal 4 - Robot Head Control
```bash
./4_robot_head.sh
```

## 🎮 Control Mapping

| Control | Function | Description |
|---------|----------|-------------|
| **Left Stick** | Eye Gaze | Move eyes up/down/left/right |
| **Right Stick** | Head Movement | Control robot head pitch/yaw |
| **Button 0 (X)** | Normal Eyes | Default expression |
| **Button 1 (A)** | Blink | Blink animation |
| **Button 2 (B)** | Surprised | Surprised expression |
| **Button 3 (Y)** | Sleepy | Sleepy expression |
| **Button 4 (LB)** | Angry | Angry expression |
| **Button 5 (RB)** | Sad | Sad expression |
| **Button 6 (LT)** | Happy | Happy expression |

## ⚙️ Configuration

### Network Settings

Edit IP addresses in the launch scripts if needed:

```bash
# Robot IP (in 4_robot_head.sh)
export ROS_MASTER_URI=http://133.11.216.57:11311
export ROS_IP=133.11.216.68  # Your machine IP
```

### Safety Parameters

Current safe settings (10Hz update, 0.15s duration):
- **Max Angle**: 30° (0.523 rad)
- **Update Rate**: 10 Hz
- **Move Duration**: 0.15 seconds
- **Dead Zone**: 0.03

## 🔍 Troubleshooting

### Check System Status
```bash
python monitor_passive.py
```

### Common Issues

**Robot head not moving:**
- Check robot network connection
- Verify Terminal 3 shows "Robot connected"
- Ensure joystick is detected

**Eye modules not responding:**
- Check serial ports: `/dev/ttyACM0` and `/dev/ttyACM1`
- Verify Terminal 2 shows both modules connected

**"우르르" (sudden rush) motion:**
- Using safe parameters (10Hz, 0.15s)
- Check network latency with monitor tool

## 📁 Project Structure

```
robot_joy_control/
├── scripts/
│   ├── joy_head_nextage.py      # Main robot head control
│   ├── joy_head_safe.py         # Safe mode with overflow prevention
│   └── network_monitor.py       # Network diagnostics
├── launch_scripts/
│   └── 3_joystick_both.sh      # Dual network joystick
└── robots/
    └── nextage.yaml             # Robot configuration
```

## 🛠️ Advanced Usage

### Monitor Network Performance
```bash
python monitor_passive.py
```

### Adjust Control Parameters
Edit `robots/nextage.yaml` for different settings:
```yaml
head_control:
  max_angle: 0.523        # Maximum rotation (radians)
  move_duration: 0.15     # Movement time (seconds)
  rate: 10.0              # Update frequency (Hz)
```

## 📝 Notes

- The system uses dual joy_node setup to bridge localhost (eye modules) and robot network
- Observer perspective control: joystick left = robot turns left (from your view)
- Asymmetric pitch limits available for hardware protection

## 🤝 Contributing

Issues and PRs welcome! Please test thoroughly before submitting changes.

## 📄 License

MIT License

## 👥 Authors

- Seongmin Hi
- Developed with Claude Code Assistant

---

**Status**: ✅ Production Ready | **Version**: 1.0.0 | **Last Updated**: April 2024