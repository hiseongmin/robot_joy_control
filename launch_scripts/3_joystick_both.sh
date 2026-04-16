#!/bin/bash
# ================================================================
# Joystick for BOTH localhost (eyes) AND robot (head)
# Runs two joy_nodes on different ROS masters
# ================================================================

echo "=========================================="
echo "  🎮 Dual Network Joystick"
echo "=========================================="
echo ""

# Kill any existing joy_node
killall joy_node 2>/dev/null
sleep 1

# PART 1: Start joy_node for ROBOT
echo "📡 Starting joy_node for ROBOT..."
export ROS_MASTER_URI=http://133.11.216.57:11311
export ROS_IP=133.11.216.68
source ~/catkin_ws/devel/setup.bash

# Test robot connection
timeout 2 rostopic list > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Robot connected"
    rosrun joy joy_node _dev:=/dev/input/js0 _deadzone:=0.05 _autorepeat_rate:=30 &
    ROBOT_JOY_PID=$!
    echo "   joy_node started for robot (PID: $ROBOT_JOY_PID)"
else
    echo "⚠️  Robot not connected (head control won't work)"
    ROBOT_JOY_PID=""
fi

sleep 2

# PART 2: Start joy_node and eye control for LOCALHOST
echo ""
echo "📡 Starting joy_node for LOCALHOST (eyes)..."
export ROS_MASTER_URI=http://localhost:11311
export ROS_HOSTNAME=localhost
source ~/catkin_ws/devel/setup.bash

# Start local joy_node
rosrun joy joy_node _dev:=/dev/input/js0 _deadzone:=0.05 _autorepeat_rate:=30 &
LOCAL_JOY_PID=$!
echo "   joy_node started for localhost (PID: $LOCAL_JOY_PID)"

sleep 2

# Start eye control
echo ""
echo "Starting eye control nodes..."

# Right eye
rosrun eye_display joy_eye_status_ye.py __ns:=right \
    _left_edge:=30.0 _right_edge:=30.0 \
    _upper_edge:=30.0 _bottom_edge:=30.0 \
    _duration:=0.02 _snap_threshold:=0.05 \
    _offset_x:=10.0 _offset_y:=5.0 &
RIGHT_PID=$!

# Left eye
rosrun eye_display joy_eye_status_ye.py __ns:=left \
    _left_edge:=30.0 _right_edge:=30.0 \
    _upper_edge:=30.0 _bottom_edge:=30.0 \
    _duration:=0.02 _snap_threshold:=0.05 \
    _offset_x:=-10.0 _offset_y:=5.0 &
LEFT_PID=$!

# Expression control
rosrun eye_display joy_eye_expression_ye.py &
EXP_PID=$!

echo ""
echo "=========================================="
echo "  ✅ Both Networks Ready!"
echo "=========================================="
echo "  • Left Stick: Eye gaze (localhost)"
echo "  • Right Stick: Robot head (robot network)"
echo "  • Buttons: Eye expressions"
echo ""
echo "Terminal 4: Run ./4_robot_head.sh"
echo ""
echo "Press Ctrl+C to stop all"

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping all nodes..."
    [ ! -z "$ROBOT_JOY_PID" ] && kill $ROBOT_JOY_PID 2>/dev/null
    kill $LOCAL_JOY_PID $RIGHT_PID $LEFT_PID $EXP_PID 2>/dev/null
    exit 0
}

trap cleanup INT

# Wait
wait