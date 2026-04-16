#!/usr/bin/env bash
# ================================================================
# Terminal 4: Robot head control (Right stick)
# ================================================================

echo "=========================================="
echo "  Robot Head Control"
echo "=========================================="
echo ""

# ROS network configuration for NEXTAGE robot
export ROS_MASTER_URI=http://133.11.216.57:11311
export ROS_IP=133.11.216.68

echo "📡 Connecting to NEXTAGE robot..."
echo "   Robot IP: 133.11.216.57"
echo "   Local IP: 133.11.216.68"
echo ""

# Check robot connection with retry
echo "Testing connection (timeout 3s)..."
timeout 3 rostopic list > /dev/null 2>&1
CONNECTION_RESULT=$?

if [ $CONNECTION_RESULT -ne 0 ]; then
    echo "❌ Cannot connect to robot"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check robot is powered on"
    echo "  2. Ping test: ping 133.11.216.57"
    echo "  3. Check network cable"
    echo ""
    echo "To monitor connection:"
    echo "  ./monitor_robot.sh"
    exit 1
fi
echo "✅ Robot connected"

# Check for stuck commands
echo "Checking command queue..."
EXISTING_COMMANDS=$(timeout 1 rostopic hz /head_controller/command 2>&1 | grep -c "average rate")
if [ $EXISTING_COMMANDS -gt 0 ]; then
    echo "⚠️  Warning: Commands may be queued"
    echo "   Clearing old commands..."
    rosnode kill /joy_head_nextage 2>/dev/null
    sleep 1
fi
echo "✅ Command queue clear"

# Check if joy topic already exists
echo ""
echo "Checking joy topic..."
if rostopic list | grep -q "^/joy$"; then
    echo "✅ /joy topic exists (from eye control)"
    echo "   Will subscribe to existing joystick data"
    LAUNCH_JOY=false
else
    echo "⚠️  /joy topic not found"
    echo "   Will launch joy_node"
    LAUNCH_JOY=true
fi

echo ""
echo "=========================================="
echo "  ⚡ OPTIMIZED Control Settings:"
echo "  • Right Stick: Robot head movement"
echo "  • Speed: 50% (smooth & safe)"
echo "  • Update rate: 30Hz (fast response)"
echo "  • Movement duration: 0.1s (quick)"
echo "  • Response: <200ms latency"
echo "=========================================="
echo ""

source ~/catkin_ws/devel/setup.bash

if [ "$LAUNCH_JOY" = true ]; then
    # Launch with joy_node
    echo "Starting optimized robot head control with joy_node..."
    roslaunch robot_joy_control nextage_head_only.launch \
        max_angle:=0.523 \
        move_duration:=0.1 \
        rate:=30.0
else
    # Launch without joy_node (just the control script)
    echo "Starting SAFE SMOOTH robot head control (joy_node already running)..."
    echo "  • Rate: 10Hz (prevents command overflow)"
    echo "  • Duration: 0.15s (smooth movement)"
    echo "  • Safe threshold: 0.03"
    # IMPORTANT: yaw_invert=-1.0 for observer perspective control
    # When observer pushes stick LEFT, robot head turns to observer's LEFT
    rosrun robot_joy_control joy_head_nextage.py \
        _max_angle:=0.523 \
        _move_duration:=0.15 \
        _rate:=10.0 \
        _axis_yaw:=3 \
        _axis_pitch:=4 \
        _yaw_invert:=-1.0 \
        _pitch_invert:=-1.0 \
        _snap_threshold:=0.03
fi