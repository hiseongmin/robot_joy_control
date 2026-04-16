#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
joy_head_asymmetric.py
----------------------
Asymmetric version with different up/down limits
- Full range for looking down
- Limited range for looking up (to protect hardware/cables)
"""

import rospy
from sensor_msgs.msg import Joy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

# State
joy_msg = None

def joy_cb(msg):
    global joy_msg
    joy_msg = msg

def timer_cb(event):
    global joy_msg
    if joy_msg is None:
        return

    msg = joy_msg

    # Read right stick axes
    if len(msg.axes) <= max(axis_yaw, axis_pitch):
        rospy.logwarn_throttle(5, "Not enough axes: got %d, need %d" % (
            len(msg.axes), max(axis_yaw, axis_pitch) + 1))
        return

    raw_yaw = msg.axes[axis_yaw]
    raw_pitch = msg.axes[axis_pitch]

    # Apply dead-band
    if abs(raw_yaw) < snap_threshold:
        raw_yaw = 0.0
    if abs(raw_pitch) < snap_threshold:
        raw_pitch = 0.0

    # YAW: Symmetric (left/right same range)
    yaw = raw_yaw * max_angle_yaw * yaw_invert

    # PITCH: Asymmetric (different up/down limits)
    # raw_pitch: +1.0 = stick up, -1.0 = stick down
    # With pitch_invert = -1.0:
    #   stick up (+1.0) → negative pitch → robot looks up
    #   stick down (-1.0) → positive pitch → robot looks down

    if raw_pitch > 0:  # Stick pushed up → robot looks up
        # Use limited range for upward motion
        pitch = raw_pitch * max_angle_pitch_up * pitch_invert
    else:  # Stick pushed down → robot looks down
        # Use full range for downward motion
        pitch = raw_pitch * max_angle_pitch_down * pitch_invert

    # Build trajectory message
    traj = JointTrajectory()
    traj.joint_names = ["HEAD_JOINT0", "HEAD_JOINT1"]

    point = JointTrajectoryPoint()
    point.positions = [yaw, pitch]
    point.velocities = [0.0, 0.0]
    point.accelerations = [0.0, 0.0]
    point.time_from_start = rospy.Duration(move_duration)

    traj.points = [point]

    # Publish
    pub.publish(traj)

    # Debug output (throttled)
    rospy.logdebug_throttle(1, "Yaw: %.2f, Pitch: %.2f (up limit: %.2f, down limit: %.2f)" %
                           (yaw, pitch, max_angle_pitch_up, max_angle_pitch_down))

if __name__ == "__main__":
    rospy.init_node("joy_head_asymmetric")
    rospy.loginfo("joy_head_asymmetric node started (different up/down limits)")

    # YAW parameters (left/right)
    max_angle_yaw = rospy.get_param("~max_angle_yaw", 0.523)  # 30 deg for left/right

    # PITCH parameters (up/down) - ASYMMETRIC
    max_angle_pitch_up = rospy.get_param("~max_angle_pitch_up", 0.262)   # 15 deg for looking up (limited)
    max_angle_pitch_down = rospy.get_param("~max_angle_pitch_down", 0.523) # 30 deg for looking down (full)

    # Joystick axes
    axis_yaw = rospy.get_param("~axis_yaw", 3)
    axis_pitch = rospy.get_param("~axis_pitch", 4)

    # Control parameters
    snap_threshold = rospy.get_param("~snap_threshold", 0.03)
    move_duration = rospy.get_param("~move_duration", 0.15)
    yaw_invert = rospy.get_param("~yaw_invert", -1.0)    # Observer perspective
    pitch_invert = rospy.get_param("~pitch_invert", -1.0) # Intuitive control
    rate = rospy.get_param("~rate", 10.0)

    # Log configuration
    rospy.loginfo("Asymmetric limits configured:")
    rospy.loginfo("  Yaw (L/R): ±%.1f deg" % (max_angle_yaw * 57.3))
    rospy.loginfo("  Pitch UP: %.1f deg (limited)" % (max_angle_pitch_up * 57.3))
    rospy.loginfo("  Pitch DOWN: %.1f deg (full)" % (max_angle_pitch_down * 57.3))

    # Setup ROS communication
    pub = rospy.Publisher("/head_controller/command",
                          JointTrajectory, queue_size=1)
    rospy.Subscriber("/joy", Joy, joy_cb, queue_size=1)

    timer = rospy.Timer(rospy.Duration(1.0 / rate), timer_cb)
    rospy.spin()