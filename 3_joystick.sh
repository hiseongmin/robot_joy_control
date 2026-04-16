#!/bin/bash
# ================================================================
# Universal Joystick Node
# Connects to robot specified in config or command line
# ================================================================

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default robot
DEFAULT_ROBOT="nextage"
ROBOT=${1:-$DEFAULT_ROBOT}

# Configuration directory
CONFIG_DIR="$HOME/catkin_ws/src/robot_joy_control/robots"
CONFIG_FILE="$CONFIG_DIR/$ROBOT.yaml"

echo "=========================================="
echo "  🎮 Universal Joystick Control"
echo "=========================================="
echo ""

# Parse YAML configuration (simple parser)
get_config() {
    grep "^$1:" "$CONFIG_FILE" 2>/dev/null | sed "s/^$1: *//" | tr -d '"'
}

# If config exists, load network settings
if [ -f "$CONFIG_FILE" ]; then
    ROBOT_NAME=$(get_config "robot_name")
    ROS_MASTER_URI=$(get_config "ros_master_uri")
    LOCAL_IP=$(get_config "local_ip")

    echo -e "${GREEN}Connecting to: $ROBOT_NAME${NC}"
    echo "  ROS Master: $ROS_MASTER_URI"
    echo "  Local IP: $LOCAL_IP"
else
    # Fallback to environment variables or defaults
    echo -e "${YELLOW}No config found for '$ROBOT', using environment defaults${NC}"
    ROS_MASTER_URI=${ROS_MASTER_URI:-"http://localhost:11311"}
    LOCAL_IP=${ROS_IP:-"127.0.0.1"}

    echo "  ROS Master: $ROS_MASTER_URI"
    echo "  Local IP: $LOCAL_IP"
fi

echo ""

# Check joystick hardware
echo "Checking joystick hardware..."
if [ -e "/dev/input/js0" ]; then
    echo -e "${GREEN}✅ Joystick found: /dev/input/js0${NC}"
    ls -la /dev/input/js0
else
    echo -e "${RED}❌ No joystick found at /dev/input/js0${NC}"
    echo ""
    echo "Please connect a joystick and try again."
    echo "Check with: ls /dev/input/js*"
    exit 1
fi

# Set ROS environment
export ROS_MASTER_URI=$ROS_MASTER_URI
export ROS_IP=$LOCAL_IP

# Source ROS workspace
source ~/catkin_ws/devel/setup.bash

# Test ROS connection
echo ""
echo "Testing ROS connection..."
timeout 3 rostopic list > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Cannot connect to ROS Master${NC}"
    echo "  This is OK for local-only operation (eye modules)"
    echo "  Robot control will not work without connection"
else
    echo -e "${GREEN}✅ Connected to ROS Master${NC}"
fi

# Kill any existing joy_node
echo ""
echo "Cleaning up old joy_node instances..."
killall joy_node 2>/dev/null
sleep 1

# Start joy_node
echo ""
echo "=========================================="
echo "  Starting joy_node..."
echo "=========================================="

rosrun joy joy_node \
    _dev:=/dev/input/js0 \
    _deadzone:=0.05 \
    _autorepeat_rate:=30 &

JOY_PID=$!
sleep 2

# Verify it's working
echo ""
echo "Verifying joy messages..."
timeout 2 rostopic hz /joy 2>/dev/null | head -3

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Joystick ready!${NC}"
else
    echo -e "${YELLOW}⚠️  Could not verify joy messages${NC}"
    echo "  This is OK for local operation"
fi

echo ""
echo "=========================================="
echo "  Control Mapping:"
echo "  • Left Stick: Eye modules / Custom"
echo "  • Right Stick: Robot head movement"
echo "  • Buttons: Various functions"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  Terminal 4: ./4_robot_control.sh $ROBOT"
echo ""
echo "Press Ctrl+C to stop"

# Keep running
wait $JOY_PID