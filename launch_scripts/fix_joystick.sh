#!/bin/bash
# ================================================================
# Fix joystick connection to ROS Master
# ================================================================

echo "=========================================="
echo "  🔧 Fixing Joystick Connection"
echo "=========================================="
echo ""

# CRITICAL: Set ROS network BEFORE running joy_node
export ROS_MASTER_URI=http://133.11.216.57:11311
export ROS_IP=133.11.216.68

echo "📡 ROS Network Configuration:"
echo "   Master: $ROS_MASTER_URI"
echo "   Local IP: $ROS_IP"
echo ""

# Kill any existing joy_node
echo "Cleaning up old joy_node..."
killall joy_node 2>/dev/null
sleep 1

# Check connection
echo "Testing ROS Master connection..."
timeout 2 rostopic list > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Cannot connect to ROS Master"
    exit 1
fi
echo "✅ ROS Master connected"
echo ""

# Start joy_node with correct network settings
echo "Starting joy_node with proper network..."
rosrun joy joy_node \
    _dev:=/dev/input/js0 \
    _deadzone:=0.05 \
    _autorepeat_rate:=30 &

sleep 2

# Verify it's working
echo ""
echo "Verifying joy messages..."
timeout 2 rostopic hz /joy > /tmp/joy_test.txt 2>&1

if grep -q "average rate" /tmp/joy_test.txt; then
    echo "✅ Joy messages confirmed!"
    cat /tmp/joy_test.txt | head -3
else
    echo "❌ No joy messages detected"
    echo "Check joystick connection"
fi

echo ""
echo "=========================================="
echo "  Now run robot head control in another terminal:"
echo "  ./4_robot_head.sh"
echo "=========================================="

# Keep running
wait