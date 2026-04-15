#!/bin/bash
# Remote NEXTAGE + Local Eye Display Demo

echo "==================================="
echo "Remote NEXTAGE + Eye Display Demo"
echo "==================================="

# Set ROS network
export ROS_MASTER_URI=http://133.11.216.57:11311
export ROS_IP=133.11.216.68

echo "ROS_MASTER_URI: $ROS_MASTER_URI"
echo "ROS_IP: $ROS_IP"
echo ""

# Check connection
echo "Checking connection to NEXTAGE..."
rostopic list > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Connected to NEXTAGE robot"
else
    echo "✗ Cannot connect to NEXTAGE at 133.11.216.57"
    echo "Please check network and robot status"
    exit 1
fi

# Check USB devices
echo ""
echo "Checking local devices..."
if [ -e /dev/ttyACM0 ] || [ -e /dev/ttyACM1 ]; then
    echo "✓ Eye modules found:"
    ls /dev/ttyACM* 2>/dev/null
else
    echo "⚠ No eye modules found at /dev/ttyACM*"
fi

if [ -e /dev/input/js0 ]; then
    echo "✓ Joystick found: /dev/input/js0"
else
    echo "⚠ No joystick found at /dev/input/js0"
fi

echo ""
echo "Starting demo..."
echo "Use Ctrl+C to stop"
echo ""

# Source workspace and launch
source ~/catkin_ws/devel/setup.bash
roslaunch robot_joy_control remote_nextage_with_eyes.launch