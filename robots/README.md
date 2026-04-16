# Robot Configuration Files

This directory contains YAML configuration files for different robots.

## 📁 Structure

Each robot has its own YAML file with standardized configuration:
- Network settings (ROS Master URI, IPs)
- Control parameters (joints, speeds, limits)
- Hardware mappings (joystick axes, buttons)
- Feature flags

## 🤖 Available Robots

- `nextage.yaml` - NEXTAGE humanoid robot

## 🚀 Usage

### Quick Start
```bash
# Default robot (nextage)
./4_robot_control.sh

# Specific robot
./4_robot_control.sh pr2
./4_robot_control.sh turtlebot
```

### With Joystick
```bash
# Terminal 3: Start joystick for specific robot
./3_joystick.sh nextage

# Terminal 4: Start robot control
./4_robot_control.sh nextage
```

## ➕ Adding New Robot

1. Create new YAML file: `robots/my_robot.yaml`
2. Copy template from existing file
3. Modify parameters:
   - Network settings
   - Joint names
   - Speed limits
   - Control mappings

### Template Structure
```yaml
robot_name: "My Robot"
robot_type: "my_robot_type"

# Network
ros_master_uri: "http://ROBOT_IP:11311"
local_ip: "YOUR_MACHINE_IP"

# Head control (if applicable)
head_control:
  enabled: true/false
  control_script: "joy_head_myrobot.py"
  topic: "/joint_controller/command"
  # ... parameters ...

# Custom features
features:
  - "feature1"
  - "feature2"
```

## 🔧 Parameters

### Common Parameters
- `max_angle`: Maximum joint angle (radians)
- `move_duration`: Time for each movement (seconds)
- `rate`: Control loop frequency (Hz)
- `snap_threshold`: Joystick dead zone

### Safety Guidelines
- Start with small `max_angle` values
- Use longer `move_duration` for safety
- Keep `rate` ≤ 1/move_duration to prevent overflow

## 📝 Notes

- Configuration is loaded at runtime
- No need to recompile after changes
- Falls back to defaults if parameter missing
- Network settings override environment variables