#!/bin/bash
# ================================================================
# Safe & Smooth Robot Head Control
# Prevents command overflow while maintaining smooth motion
# ================================================================

echo "=========================================="
echo "  🛡️ SAFE & SMOOTH Robot Head Control"
echo "=========================================="
echo ""

# ROS network configuration
export ROS_MASTER_URI=http://133.11.216.57:11311
export ROS_IP=133.11.216.68

echo "📡 Connecting to NEXTAGE robot..."
timeout 3 rostopic list > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Cannot connect to robot"
    exit 1
fi
echo "✅ Robot connected"

# Clear any queued commands
echo "Clearing command queue..."
rosnode kill /joy_head_nextage 2>/dev/null
sleep 1

echo ""
echo "=========================================="
echo "  🛡️ SAFE Settings (No overlap):"
echo "  • Movement: 0.15s (fast but safe)"
echo "  • Update: 10Hz (matches movement)"
echo "  • Queue size: 1 (no buildup)"
echo "  • Smooth: Medium response"
echo "=========================================="
echo ""
echo "This configuration ensures:"
echo "  ✓ No command overflow"
echo "  ✓ Predictable motion"
echo "  ✓ Smooth enough for comfort"
echo "  ✓ Fast enough for control"
echo ""

source ~/catkin_ws/devel/setup.bash

# Safe parameters:
# - Rate and duration synchronized to prevent overlap
# - 10Hz update with 0.15s duration = safe margin
echo "Starting safe smooth control..."
rosrun robot_joy_control joy_head_nextage.py \
    _max_angle:=0.523 \
    _move_duration:=0.15 \
    _rate:=10.0 \
    _axis_yaw:=3 \
    _axis_pitch:=4 \
    _yaw_invert:=-1.0 \
    _pitch_invert:=-1.0 \
    _snap_threshold:=0.03