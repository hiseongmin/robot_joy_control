#!/bin/bash
# ================================================================
# Universal Robot Control Script
# Loads robot-specific configuration from YAML files
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
echo "  🤖 Universal Robot Control"
echo "=========================================="
echo ""

# Check if configuration exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}❌ Configuration not found: $CONFIG_FILE${NC}"
    echo ""
    echo "Available robots:"
    for config in $CONFIG_DIR/*.yaml; do
        if [ -f "$config" ]; then
            basename "$config" .yaml | sed 's/^/  • /'
        fi
    done
    echo ""
    echo "Usage: $0 [robot_name]"
    echo "Example: $0 nextage"
    exit 1
fi

# Parse YAML configuration (simple parser)
get_config() {
    grep "^$1:" "$CONFIG_FILE" | sed "s/^$1: *//" | tr -d '"'
}

get_nested_config() {
    sed -n "/^$1:/,/^[^ ]/p" "$CONFIG_FILE" | grep "  $2:" | sed "s/.*$2: *//" | tr -d '"'
}

# Load configuration
ROBOT_NAME=$(get_config "robot_name")
ROBOT_TYPE=$(get_config "robot_type")
ROS_MASTER_URI=$(get_config "ros_master_uri")
LOCAL_IP=$(get_config "local_ip")

# Head control parameters
HEAD_ENABLED=$(get_nested_config "head_control" "enabled")
CONTROL_SCRIPT=$(get_nested_config "head_control" "control_script")
MAX_ANGLE=$(get_nested_config "head_control" "max_angle")
MOVE_DURATION=$(get_nested_config "head_control" "move_duration")
RATE=$(get_nested_config "head_control" "rate")
AXIS_YAW=$(get_nested_config "head_control" "axis_yaw")
AXIS_PITCH=$(get_nested_config "head_control" "axis_pitch")
YAW_INVERT=$(get_nested_config "head_control" "yaw_invert")
PITCH_INVERT=$(get_nested_config "head_control" "pitch_invert")
SNAP_THRESHOLD=$(get_nested_config "head_control" "snap_threshold")

# Display configuration
echo -e "${GREEN}Robot: $ROBOT_NAME ($ROBOT_TYPE)${NC}"
echo "Configuration loaded from: $CONFIG_FILE"
echo ""
echo "Network Settings:"
echo "  ROS Master: $ROS_MASTER_URI"
echo "  Local IP: $LOCAL_IP"
echo ""

if [ "$HEAD_ENABLED" != "true" ]; then
    echo -e "${YELLOW}⚠️  Head control disabled for this robot${NC}"
    exit 0
fi

echo "Control Parameters:"
echo "  Max angle: $MAX_ANGLE rad"
echo "  Move duration: $MOVE_DURATION s"
echo "  Update rate: $RATE Hz"
echo "  Deadzone: $SNAP_THRESHOLD"
echo ""

# Set ROS environment
export ROS_MASTER_URI=$ROS_MASTER_URI
export ROS_IP=$LOCAL_IP

# Test connection
echo "Testing connection to robot..."
timeout 3 rostopic list > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Cannot connect to robot${NC}"
    echo "Check network and robot power"
    exit 1
fi
echo -e "${GREEN}✅ Connected to robot${NC}"
echo ""

# Source ROS workspace
source ~/catkin_ws/devel/setup.bash

# Check if control script exists
SCRIPT_PATH="$HOME/catkin_ws/src/robot_joy_control/scripts/$CONTROL_SCRIPT"
if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${YELLOW}⚠️  Using default control script${NC}"
    CONTROL_SCRIPT="joy_head_nextage.py"
fi

# Launch robot control
echo "=========================================="
echo "  Starting $ROBOT_NAME Control"
echo "=========================================="

rosrun robot_joy_control $CONTROL_SCRIPT \
    _max_angle:=$MAX_ANGLE \
    _move_duration:=$MOVE_DURATION \
    _rate:=$RATE \
    _axis_yaw:=$AXIS_YAW \
    _axis_pitch:=$AXIS_PITCH \
    _yaw_invert:=$YAW_INVERT \
    _pitch_invert:=$PITCH_INVERT \
    _snap_threshold:=$SNAP_THRESHOLD