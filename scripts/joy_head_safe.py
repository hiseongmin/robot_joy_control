#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
joy_head_safe.py
----------------
Safe version that prevents command queue buildup
Only sends new command when previous is nearly complete
"""

import rospy
from sensor_msgs.msg import Joy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

# State tracking
joy_msg = None
last_command_time = None
command_in_progress = False

def joy_cb(msg):
    global joy_msg
    joy_msg = msg

def timer_cb(event):
    global joy_msg, last_command_time, command_in_progress

    if joy_msg is None:
        return

    # Check if enough time has passed since last command
    if last_command_time is not None:
        elapsed = (rospy.Time.now() - last_command_time).to_sec()
        # Only send new command if 80% of previous duration has passed
        if elapsed < (move_duration * 0.8):
            return  # Skip this update to prevent overlap

    msg = joy_msg

    # Read axes
    if len(msg.axes) <= max(axis_yaw, axis_pitch):
        return

    raw_yaw = msg.axes[axis_yaw]
    raw_pitch = msg.axes[axis_pitch]

    # Dead-band filter
    if abs(raw_yaw) < snap_threshold:
        raw_yaw = 0.0
    if abs(raw_pitch) < snap_threshold:
        raw_pitch = 0.0

    # Calculate target angles
    yaw = raw_yaw * max_angle * yaw_invert
    pitch = raw_pitch * max_angle * pitch_invert

    # Build trajectory message
    traj = JointTrajectory()
    traj.joint_names = ["HEAD_JOINT0", "HEAD_JOINT1"]

    point = JointTrajectoryPoint()
    point.positions = [yaw, pitch]
    point.velocities = [0.0, 0.0]
    point.accelerations = [0.0, 0.0]
    point.time_from_start = rospy.Duration(move_duration)

    traj.points = [point]

    # Publish and record time
    pub.publish(traj)
    last_command_time = rospy.Time.now()

    # Log for debugging
    rospy.logdebug("Command sent: yaw=%.2f, pitch=%.2f" % (yaw, pitch))

if __name__ == "__main__":
    rospy.init_node("joy_head_safe")
    rospy.loginfo("joy_head_safe node started (queue-safe version)")

    # Parameters with safe defaults
    max_angle = rospy.get_param("~max_angle", 0.523)        # 30 degrees
    axis_yaw = rospy.get_param("~axis_yaw", 3)
    axis_pitch = rospy.get_param("~axis_pitch", 4)
    snap_threshold = rospy.get_param("~snap_threshold", 0.03)
    move_duration = rospy.get_param("~move_duration", 0.15)  # 150ms per move
    yaw_invert = rospy.get_param("~yaw_invert", -1.0)
    pitch_invert = rospy.get_param("~pitch_invert", -1.0)
    rate = rospy.get_param("~rate", 10.0)  # 10Hz to match duration

    # Validate parameters
    if (1.0 / rate) < (move_duration * 0.8):
        rospy.logwarn("Rate too high for duration! Adjusting rate...")
        rate = 1.0 / (move_duration * 1.2)  # Set safe rate

    # Publisher with queue_size=1 to prevent buildup
    pub = rospy.Publisher("/head_controller/command",
                          JointTrajectory, queue_size=1)
    rospy.Subscriber("/joy", Joy, joy_cb, queue_size=1)

    # Timer
    timer = rospy.Timer(rospy.Duration(1.0 / rate), timer_cb)

    rospy.loginfo("Safe parameters: rate=%.1fHz, duration=%.2fs" % (rate, move_duration))
    rospy.spin()