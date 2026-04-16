#!/usr/bin/env bash
# ================================================================
# Terminal 3: Joystick control for ROBOT (Fixed version)
# Connects to robot's ROS Master, not localhost
# ================================================================

echo "=========================================="
echo "  Starting Joystick for Robot Control"
echo "=========================================="
echo ""

# CRITICAL: Connect to ROBOT's ROS Master, not localhost!
export ROS_MASTER_URI=http://133.11.216.57:11311
export ROS_IP=133.11.216.68

echo "📡 ROS Network Configuration:"
echo "   Connecting to ROBOT at: $ROS_MASTER_URI"
echo "   Local IP: $ROS_IP"
echo ""

# Source ROS workspace
source ~/catkin_ws/devel/setup.bash

# Check joystick hardware
echo "Checking joystick hardware..."
if [ -e "/dev/input/js0" ]; then
    echo "✅ Joystick found: /dev/input/js0"
    ls -la /dev/input/js0
else
    echo "❌ No joystick found at /dev/input/js0"
    echo ""
    echo "Please connect a joystick and try again."
    exit 1
fi

# Test ROS Master connection
echo ""
echo "Testing connection to robot..."
timeout 3 rostopic list > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Cannot connect to robot's ROS Master"
    echo "   Check network and robot power"
    exit 1
fi
echo "✅ Connected to robot's ROS Master"

echo ""
echo "=========================================="
echo "  Starting joy_node..."
echo "=========================================="

# Start joy_node connected to ROBOT
rosrun joy joy_node \
    _dev:=/dev/input/js0 \
    _deadzone:=0.05 \
    _autorepeat_rate:=30 &

JOY_PID=$!
sleep 2

# Verify it's working
echo ""
echo "Verifying joy messages on robot network..."
timeout 2 rostopic hz /joy | head -3

echo ""
echo "=========================================="
echo "  ✅ Joystick Ready for Robot Control"
echo "=========================================="
echo ""
echo "Control Mapping:"
echo "  • Left Stick: (Available for eye modules)"
echo "  • Right Stick: Robot head movement"
echo ""
echo "Now run in Terminal 4:"
echo "  ./4_robot_head.sh"
echo ""
echo "Press Ctrl+C to stop"

# Keep running
wait $JOY_PID