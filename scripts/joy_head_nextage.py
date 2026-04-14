#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
joy_head_nextage.py
-------------------
Control Nextage robot head joints with joystick right stick.

  Right stick horizontal (axes[3]) -> HEAD_JOINT0 (yaw, left-right)
  Right stick vertical   (axes[4]) -> HEAD_JOINT1 (pitch, up-down)

Publishes trajectory_msgs/JointTrajectory to /head_controller/command.

Compatible with Python 2.7 / ROS Indigo (Ubuntu 14.04).

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

    # Dead-band
    if abs(raw_yaw) < snap_threshold:
        raw_yaw = 0.0
    if abs(raw_pitch) < snap_threshold:
        raw_pitch = 0.0

    # Map joystick (-1..1) to joint angle (-max_angle..max_angle)
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

    pub.publish(traj)


if __name__ == "__main__":
    rospy.init_node("joy_head_nextage")
    rospy.loginfo("joy_head_nextage node started")

    # Parameters
    max_angle = rospy.get_param("~max_angle", 1.047)        # 60 deg in rad
    axis_yaw = rospy.get_param("~axis_yaw", 3)              # right stick horizontal
    axis_pitch = rospy.get_param("~axis_pitch", 4)           # right stick vertical
    snap_threshold = rospy.get_param("~snap_threshold", 0.1)
    move_duration = rospy.get_param("~move_duration", 0.5)   # seconds for trajectory
    yaw_invert = rospy.get_param("~yaw_invert", 1.0)        # set -1.0 to flip
    pitch_invert = rospy.get_param("~pitch_invert", 1.0)    # set -1.0 to flip
    rate = rospy.get_param("~rate", 10.0)                    # publish rate (Hz)

    pub = rospy.Publisher("/head_controller/command",
                          JointTrajectory, queue_size=1)
    rospy.Subscriber("/joy", Joy, joy_cb, queue_size=1)

    timer = rospy.Timer(rospy.Duration(1.0 / rate), timer_cb)
    rospy.spin()
