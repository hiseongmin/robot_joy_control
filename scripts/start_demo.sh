#!/bin/bash
# ================================================================
# NEXTAGE Robot + Eye Display Demo Launcher
#
# Usage:
#   ./start_demo.sh                     # Use default IPs
#   ./start_demo.sh <ROBOT_IP>          # Custom robot IP
#   ./start_demo.sh <ROBOT_IP> <MY_IP>  # Custom both IPs
#
# Example:
#   ./start_demo.sh 192.168.1.100
#   ./start_demo.sh 192.168.1.100 192.168.1.50
# ================================================================

echo "=========================================="
echo "  NEXTAGE + Eye Display Demo"
echo "=========================================="
echo ""

# Get IPs from arguments or use defaults
ROBOT_IP=${1:-"10.0.0.1"}  # Default robot IP
MY_IP=${2:-$(hostname -I | awk '{print $1}')}  # Auto-detect local IP if not provided

# Set ROS network configuration
export ROS_MASTER_URI=http://$ROBOT_IP:11311
export ROS_IP=$MY_IP

echo "📡 Network Configuration:"
echo "   Robot IP: $ROBOT_IP"
echo "   Local IP: $MY_IP"
echo ""
echo "   ROS_MASTER_URI: $ROS_MASTER_URI"
echo "   ROS_IP: $ROS_IP"
echo ""

# Check robot connection
echo "🔍 Checking robot connection..."
timeout 2 rostopic list > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Connected to NEXTAGE robot!"
else
    echo "❌ Cannot connect to robot at $ROBOT_IP"
    echo ""
    echo "Usage:"
    echo "  $0 [ROBOT_IP] [LOCAL_IP]"
    echo ""
    echo "Example:"
    echo "  $0 192.168.1.100"
    echo "  $0 192.168.1.100 192.168.1.50"
    exit 1
fi
echo ""

# Check local hardware
echo "🔍 Checking local hardware..."

# Check eye modules
EYE_COUNT=$(ls /dev/ttyACM* 2>/dev/null | wc -l)
if [ $EYE_COUNT -gt 0 ]; then
    echo "✅ Found $EYE_COUNT eye module(s):"
    ls /dev/ttyACM* 2>/dev/null | sed 's/^/   /'
else
    echo "⚠️  No eye modules found"
    echo "   Continuing anyway..."
fi

# Check joystick
if [ -e /dev/input/js0 ]; then
    echo "✅ Joystick found: /dev/input/js0"
else
    echo "⚠️  No joystick found"
    echo "   Continuing anyway..."
fi
echo ""

# Show control mapping
echo "=========================================="
echo "  Control Mapping:"
echo "  - Left Stick:  Eye gaze"
echo "  - Right Stick: Robot head"
echo "  - Buttons:     Eye expressions"
echo "=========================================="
echo ""

# Launch
echo "🚀 Starting demo..."
echo "   Press Ctrl+C to stop"
echo ""

# Source ROS workspace and launch
source ~/catkin_ws/devel/setup.bash
roslaunch robot_joy_control remote_nextage_with_eyes.launch