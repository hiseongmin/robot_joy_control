#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
joy_head_nextage.py
-------------------
Control Nextage robot head joints with joystick right stick.

TOPIC INTERFACE:
  Subscribes to:
    /joy (sensor_msgs/Joy) - Joystick input from joy_node
      - axes[3]: Right stick horizontal (-1.0 left to 1.0 right)
      - axes[4]: Right stick vertical (-1.0 down to 1.0 up)

  Publishes to:
    /head_controller/command (trajectory_msgs/JointTrajectory)
      - joint_names: ["HEAD_JOINT0", "HEAD_JOINT1"]
      - points[0].positions: [yaw_angle, pitch_angle] in radians
      - points[0].time_from_start: Duration for trajectory execution

JOINT MAPPING:
  Right stick horizontal (axes[3]) -> HEAD_JOINT0 (yaw, left-right rotation)
  Right stick vertical   (axes[4]) -> HEAD_JOINT1 (pitch, up-down tilt)

KEY PARAMETERS FOR TUNING:
  max_angle: Maximum rotation angle in radians (motor speed limit)
    - 0.523 rad (30°) = 50% speed (safe, default)
    - 0.733 rad (42°) = 70% speed
    - 1.047 rad (60°) = 100% speed (max hardware limit)

  move_duration: Time for robot to execute trajectory (response latency)
    - 0.05s = Ultra fast (may cause jerky motion)
    - 0.1s = Fast response (recommended)
    - 0.3s = Smooth motion
    - 0.5s = Default (safe but slow)

  rate: How often to publish commands (Hz)
    - 10Hz = 100ms between commands (slow)
    - 20Hz = 50ms between commands (normal)
    - 30Hz = 33ms between commands (fast)
    - 50Hz = 20ms between commands (very fast)

  snap_threshold: Dead zone for joystick (0.0-1.0)
    - 0.01 = Very sensitive (1% threshold)
    - 0.02 = Sensitive (2% threshold)
    - 0.05 = Normal (5% threshold)
    - 0.1 = Less sensitive (10% threshold)

Usage:
  rosrun robot_joy_control joy_head_nextage.py
  rosrun robot_joy_control joy_head_nextage.py _max_angle:=0.5 _axis_yaw:=3 _axis_pitch:=4
"""

import math
import rospy
from sensor_msgs.msg import Joy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

# State
joy_msg = None


def joy_cb(msg):
    global joy_msg
    joy_msg = msg


def timer_cb(event):
    """
    Timer callback: Publishes head trajectory commands at fixed rate.
    Called every 1/rate seconds (e.g., 30Hz = every 33ms).
    """
    global joy_msg
    if joy_msg is None:
        return

    msg = joy_msg

    # Read right stick axes from joystick message
    if len(msg.axes) <= max(axis_yaw, axis_pitch):
        rospy.logwarn_throttle(5, "Not enough axes: got %d, need %d" % (
            len(msg.axes), max(axis_yaw, axis_pitch) + 1))
        return

    # Get raw joystick values (-1.0 to 1.0)
    raw_yaw = msg.axes[axis_yaw]      # axes[3] for right stick X
    raw_pitch = msg.axes[axis_pitch]  # axes[4] for right stick Y

    # Apply dead-band filter (ignore small movements near center)
    # This prevents drift and unintended micro-movements
    if abs(raw_yaw) < snap_threshold:
        raw_yaw = 0.0
    if abs(raw_pitch) < snap_threshold:
        raw_pitch = 0.0

    # Map joystick values to joint angles
    # Formula: joystick_value * max_angle * invert_factor
    # Example: 0.5 * 0.523 * 1.0 = 0.2615 rad (15 degrees right)
    yaw = raw_yaw * max_angle * yaw_invert
    pitch = raw_pitch * max_angle * pitch_invert

    # Build JointTrajectory message for robot controller
    traj = JointTrajectory()
    # NEXTAGE robot head joint names (must match robot's URDF)
    traj.joint_names = ["HEAD_JOINT0", "HEAD_JOINT1"]

    # Create trajectory point with target positions
    point = JointTrajectoryPoint()
    point.positions = [yaw, pitch]  # Target angles in radians
    point.velocities = [0.0, 0.0]   # Let controller compute velocities
    point.accelerations = [0.0, 0.0] # Let controller compute accelerations

    # CRITICAL PARAMETER: How long robot takes to reach target
    # Shorter = faster response but may cause overshoot
    # Longer = smoother motion but feels laggy
    point.time_from_start = rospy.Duration(move_duration)

    traj.points = [point]

    # Publish to robot's head controller
    # Topic: /head_controller/command
    # The robot's trajectory controller will execute this motion
    pub.publish(traj)


if __name__ == "__main__":
    rospy.init_node("joy_head_nextage")
    rospy.loginfo("joy_head_nextage node started")

    # ========== PARAMETER CONFIGURATION ==========
    # These parameters control robot behavior and can be adjusted for different requirements

    # MOTOR SPEED: Maximum angle the head can rotate (in radians)
    # Smaller value = slower/safer movement, Larger value = faster movement
    # To change motor speed: adjust this value (0.0 to 1.047 rad)
    max_angle = rospy.get_param("~max_angle", 1.047)        # Default: 60° (full speed)

    # JOYSTICK MAPPING: Which joystick axes control the head
    # Standard mapping: 3=right stick X, 4=right stick Y
    # Change these if using different joystick or want different stick
    axis_yaw = rospy.get_param("~axis_yaw", 3)              # Horizontal control
    axis_pitch = rospy.get_param("~axis_pitch", 4)          # Vertical control

    # SENSITIVITY: Dead zone threshold (0.0 to 1.0)
    # Smaller = more sensitive to small movements
    # Larger = ignores small movements (prevents drift)
    snap_threshold = rospy.get_param("~snap_threshold", 0.1)

    # RESPONSE TIME: How long robot takes to reach commanded position
    # THIS IS THE MAIN LATENCY PARAMETER
    # Smaller = faster response but may overshoot
    # Larger = smoother but feels laggy
    move_duration = rospy.get_param("~move_duration", 0.5)   # seconds

    # DIRECTION: Invert controls if needed (-1.0 to flip, 1.0 normal)
    yaw_invert = rospy.get_param("~yaw_invert", 1.0)
    pitch_invert = rospy.get_param("~pitch_invert", 1.0)

    # UPDATE RATE: How often to send commands to robot (Hz)
    # Higher = more responsive but uses more network bandwidth
    # Lower = less responsive but more stable on poor networks
    rate = rospy.get_param("~rate", 10.0)                    # Commands per second

    # ========== ROS COMMUNICATION SETUP ==========

    # Publisher: Sends JointTrajectory messages to robot
    # Topic: /head_controller/command
    # Message type: trajectory_msgs/JointTrajectory
    # Queue size: 1 (only keep latest command)
    pub = rospy.Publisher("/head_controller/command",
                          JointTrajectory, queue_size=1)

    # Subscriber: Receives joystick input
    # Topic: /joy (published by joy_node)
    # Message type: sensor_msgs/Joy
    # Callback: joy_cb stores latest joystick state
    rospy.Subscriber("/joy", Joy, joy_cb, queue_size=1)

    # Timer: Calls timer_cb at fixed rate to publish commands
    # This ensures consistent command rate regardless of joystick update rate
    timer = rospy.Timer(rospy.Duration(1.0 / rate), timer_cb)

    # Keep node running
    rospy.spin()
