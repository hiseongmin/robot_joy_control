# Technical Details - Robot Head Control System

## ROS Topic Communication

### Input Topic
**`/joy` (sensor_msgs/Joy)**
- Published by: `joy_node`
- Subscribe rate: As fast as available
- Key fields:
  ```
  axes[3]: Right stick horizontal (-1.0 left, 0.0 center, 1.0 right)
  axes[4]: Right stick vertical (-1.0 down, 0.0 center, 1.0 up)
  ```

### Output Topic
**`/head_controller/command` (trajectory_msgs/JointTrajectory)**
- Published to: Robot's trajectory controller
- Publish rate: Configurable (10-50 Hz)
- Message structure:
  ```yaml
  joint_names: ["HEAD_JOINT0", "HEAD_JOINT1"]
  points:
    - positions: [yaw_radians, pitch_radians]
      velocities: [0.0, 0.0]
      accelerations: [0.0, 0.0]
      time_from_start: {secs: 0, nsecs: 100000000}  # 0.1 seconds
  ```

## Parameter Reference

### 1. `max_angle` (Motor Speed Control)
**Purpose:** Controls how far the robot head can rotate

**Range:** 0.0 to 1.047 radians (0° to 60°)

**How to adjust motor speed:**
```bash
# Slow (30% speed)
_max_angle:=0.314   # 18 degrees

# Safe (50% speed) - RECOMMENDED
_max_angle:=0.523   # 30 degrees

# Normal (70% speed)
_max_angle:=0.733   # 42 degrees

# Fast (90% speed)
_max_angle:=0.942   # 54 degrees

# Maximum (100% speed)
_max_angle:=1.047   # 60 degrees
```

**Effect:**
- Smaller value = Robot head moves slower but safer
- Larger value = Robot head moves faster but may overshoot

### 2. `move_duration` (Response Latency)
**Purpose:** Time for robot to execute trajectory

**Range:** 0.05 to 1.0 seconds

**Settings:**
```bash
# Ultra Fast (may be unstable)
_move_duration:=0.05

# Fast (recommended for good networks)
_move_duration:=0.1

# Balanced
_move_duration:=0.2

# Smooth (default)
_move_duration:=0.3

# Very Smooth (for poor networks)
_move_duration:=0.5
```

**Network Impact:**
- Local network: Can use 0.05-0.1s
- Remote LAN: Use 0.1-0.2s
- Internet: Use 0.3s or higher

### 3. `rate` (Update Frequency)
**Purpose:** How often to send commands to robot

**Range:** 5 to 50 Hz

**Settings:**
```bash
# Conservative
_rate:=10.0   # 100ms between commands

# Normal
_rate:=20.0   # 50ms between commands

# Fast (recommended)
_rate:=30.0   # 33ms between commands

# Very Fast
_rate:=50.0   # 20ms between commands
```

**Trade-offs:**
- Higher rate = More responsive but more network traffic
- Lower rate = Less responsive but more stable

### 4. `snap_threshold` (Sensitivity)
**Purpose:** Dead zone to prevent drift

**Range:** 0.0 to 0.2

**Settings:**
```bash
# Ultra Sensitive (may drift)
_snap_threshold:=0.01

# Sensitive (recommended)
_snap_threshold:=0.02

# Normal
_snap_threshold:=0.05

# Less Sensitive (prevents accidental movement)
_snap_threshold:=0.1
```

## Common Tuning Scenarios

### Scenario 1: "Robot moves too fast/dangerous"
```bash
# Reduce max_angle to slow down motor speed
rosrun robot_joy_control joy_head_nextage.py \
    _max_angle:=0.3 \     # Slower motor
    _move_duration:=0.2 \ # Smoother motion
    _rate:=20.0
```

### Scenario 2: "Response is too laggy"
```bash
# Reduce move_duration and increase rate
rosrun robot_joy_control joy_head_nextage.py \
    _max_angle:=0.523 \   # Keep safe speed
    _move_duration:=0.05 \ # Very fast response
    _rate:=50.0 \         # High update rate
    _snap_threshold:=0.01 # Very sensitive
```

### Scenario 3: "Robot drifts when joystick centered"
```bash
# Increase snap_threshold
rosrun robot_joy_control joy_head_nextage.py \
    _snap_threshold:=0.15 # Larger dead zone
```

### Scenario 4: "Jerky/unstable movement"
```bash
# Increase move_duration for smoother motion
rosrun robot_joy_control joy_head_nextage.py \
    _move_duration:=0.3 \ # Smoother
    _rate:=15.0          # Lower update rate
```

## Message Flow Diagram

```
Joystick → joy_node → /joy topic → joy_head_nextage.py
                                           ↓
                                    Process at rate Hz
                                           ↓
                              Calculate target angles:
                              yaw = axes[3] * max_angle
                              pitch = axes[4] * max_angle
                                           ↓
                                Build JointTrajectory:
                                - positions: [yaw, pitch]
                                - time_from_start: move_duration
                                           ↓
                    /head_controller/command topic → Robot Controller
                                                            ↓
                                                     Execute motion
```

## Robot-Specific Configuration

### NEXTAGE Robot
```yaml
Joint names: ["HEAD_JOINT0", "HEAD_JOINT1"]
Joint limits: ±60 degrees (1.047 rad)
Safe operating range: ±30 degrees (0.523 rad)
Topic: /head_controller/command
```

### PR2 Robot
```yaml
Joint names: ["head_pan_joint", "head_tilt_joint"]
Joint limits: ±90 degrees (1.57 rad)
Topic: /head_traj_controller/command
```

### Custom Robot
1. Find joint names from URDF:
   ```bash
   rostopic echo /joint_states -n 1
   ```

2. Find controller topic:
   ```bash
   rostopic list | grep head
   ```

3. Update in code:
   ```python
   traj.joint_names = ["YOUR_YAW_JOINT", "YOUR_PITCH_JOINT"]
   pub = rospy.Publisher("/your_controller/command", ...)
   ```

## Debugging Commands

### Monitor actual commands being sent:
```bash
rostopic echo /head_controller/command
```

### Check command frequency:
```bash
rostopic hz /head_controller/command
```

### View joystick input:
```bash
rostopic echo /joy
```

### Test manual command:
```bash
rostopic pub -1 /head_controller/command trajectory_msgs/JointTrajectory \
  '{joint_names: ["HEAD_JOINT0", "HEAD_JOINT1"],
    points: [{positions: [0.5, 0.3], time_from_start: {secs: 1}}]}'
```

## Performance Optimization Guide

### For Minimum Latency (<100ms total):
```yaml
max_angle: 0.523      # Safe speed
move_duration: 0.05   # Ultra fast
rate: 50              # Maximum update
snap_threshold: 0.01  # Very sensitive
```

### For Smooth Operation (Recommended):
```yaml
max_angle: 0.523      # Safe speed
move_duration: 0.1    # Fast
rate: 30              # High update
snap_threshold: 0.02  # Sensitive
```

### For Stability on Poor Networks:
```yaml
max_angle: 0.523      # Safe speed
move_duration: 0.3    # Smooth
rate: 15              # Moderate update
snap_threshold: 0.05  # Normal
```