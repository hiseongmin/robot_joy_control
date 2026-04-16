#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
joy_head_smooth.py
------------------
Smooth version with interpolation and velocity control
"""

import rospy
from sensor_msgs.msg import Joy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

# State
joy_msg = None
last_yaw = 0.0
last_pitch = 0.0
smoothing_factor = 0.3  # 0.0 = no smoothing, 1.0 = max smoothing

def joy_cb(msg):
    global joy_msg
    joy_msg = msg

def timer_cb(event):
    global joy_msg, last_yaw, last_pitch

    if joy_msg is None:
        return

    msg = joy_msg

    # Read axes
    if len(msg.axes) <= max(axis_yaw, axis_pitch):
        return

    raw_yaw = msg.axes[axis_yaw]
    raw_pitch = msg.axes[axis_pitch]

    # Dead-band
    if abs(raw_yaw) < snap_threshold:
        raw_yaw = 0.0
    if abs(raw_pitch) < snap_threshold:
        raw_pitch = 0.0

    # Target angles
    target_yaw = raw_yaw * max_angle * yaw_invert
    target_pitch = raw_pitch * max_angle * pitch_invert

    # SMOOTHING: Exponential moving average
    # Instead of jumping directly to target, blend with previous
    smooth_yaw = last_yaw + (target_yaw - last_yaw) * (1.0 - smoothing_factor)
    smooth_pitch = last_pitch + (target_pitch - last_pitch) * (1.0 - smoothing_factor)

    # Update last values
    last_yaw = smooth_yaw
    last_pitch = smooth_pitch

    # Build trajectory with multiple points for smoother motion
    traj = JointTrajectory()
    traj.joint_names = ["HEAD_JOINT0", "HEAD_JOINT1"]

    # Current position (assumed at last commanded position)
    point1 = JointTrajectoryPoint()
    point1.positions = [smooth_yaw, smooth_pitch]

    # Calculate velocities for smooth motion
    # Velocity = change / time
    vel_yaw = (target_yaw - smooth_yaw) / move_duration if move_duration > 0 else 0
    vel_pitch = (target_pitch - smooth_pitch) / move_duration if move_duration > 0 else 0

    point1.velocities = [vel_yaw, vel_pitch]
    point1.accelerations = [0.0, 0.0]
    point1.time_from_start = rospy.Duration(move_duration)

    traj.points = [point1]

    pub.publish(traj)

if __name__ == "__main__":
    rospy.init_node("joy_head_smooth")
    rospy.loginfo("joy_head_smooth node started (with interpolation)")

    # Parameters
    max_angle = rospy.get_param("~max_angle", 0.523)
    axis_yaw = rospy.get_param("~axis_yaw", 3)
    axis_pitch = rospy.get_param("~axis_pitch", 4)
    snap_threshold = rospy.get_param("~snap_threshold", 0.03)
    move_duration = rospy.get_param("~move_duration", 0.2)
    yaw_invert = rospy.get_param("~yaw_invert", -1.0)
    pitch_invert = rospy.get_param("~pitch_invert", -1.0)
    rate = rospy.get_param("~rate", 15.0)
    smoothing_factor = rospy.get_param("~smoothing", 0.3)

    pub = rospy.Publisher("/head_controller/command",
                          JointTrajectory, queue_size=1)
    rospy.Subscriber("/joy", Joy, joy_cb, queue_size=1)

    timer = rospy.Timer(rospy.Duration(1.0 / rate), timer_cb)
    rospy.spin()