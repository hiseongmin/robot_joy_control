#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
joy_head_adaptive.py
--------------------
Adaptive control that adjusts to network conditions
- Monitors latency and adjusts parameters dynamically
- Implements smoothing for consistent motion
"""

import rospy
from sensor_msgs.msg import Joy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from collections import deque
import numpy as np

class AdaptiveHeadControl:
    def __init__(self):
        # State
        self.joy_msg = None
        self.last_command_time = None

        # Position tracking for smoothing
        self.current_yaw = 0.0
        self.current_pitch = 0.0
        self.target_yaw = 0.0
        self.target_pitch = 0.0

        # Performance tracking
        self.latencies = deque(maxlen=20)
        self.last_joy_time = None

        # Adaptive parameters
        self.adaptive_duration = 0.15  # Will adjust based on network
        self.adaptive_rate = 10.0       # Will adjust based on performance

        # Fixed parameters
        self.max_angle = rospy.get_param("~max_angle", 0.523)
        self.axis_yaw = rospy.get_param("~axis_yaw", 3)
        self.axis_pitch = rospy.get_param("~axis_pitch", 4)
        self.snap_threshold = rospy.get_param("~snap_threshold", 0.03)
        self.yaw_invert = rospy.get_param("~yaw_invert", -1.0)
        self.pitch_invert = rospy.get_param("~pitch_invert", -1.0)

        # Smoothing factor (0.0 = no smoothing, 1.0 = max smoothing)
        self.smoothing_factor = rospy.get_param("~smoothing_factor", 0.3)

        # Publisher
        self.pub = rospy.Publisher("/head_controller/command",
                                   JointTrajectory, queue_size=1)

        rospy.loginfo("Adaptive head control started")

    def joy_cb(self, msg):
        """Handle joystick input with timing"""
        self.joy_msg = msg
        self.last_joy_time = rospy.Time.now()

    def smooth_position(self, target, current, factor):
        """Apply exponential smoothing to position"""
        return current + (target - current) * (1.0 - factor)

    def calculate_adaptive_params(self):
        """Adjust parameters based on network conditions"""
        if len(self.latencies) < 5:
            return  # Not enough data yet

        # Calculate average and max latency
        avg_latency = np.mean(self.latencies)
        max_latency = np.max(self.latencies)
        jitter = np.std(self.latencies)

        # Adapt duration based on latency
        if max_latency > 0.2:  # >200ms latency
            # Increase duration for stability
            self.adaptive_duration = min(0.25, self.adaptive_duration * 1.1)
            self.smoothing_factor = min(0.5, self.smoothing_factor * 1.1)
            rospy.logdebug("High latency detected, increasing smoothing")
        elif max_latency < 0.1 and jitter < 0.03:  # Good conditions
            # Decrease duration for responsiveness
            self.adaptive_duration = max(0.1, self.adaptive_duration * 0.95)
            self.smoothing_factor = max(0.2, self.smoothing_factor * 0.95)
            rospy.logdebug("Good network, decreasing smoothing")

        # Adjust rate to match duration
        self.adaptive_rate = min(15.0, 1.0 / (self.adaptive_duration * 0.8))

    def timer_cb(self, event):
        """Control loop with adaptive parameters"""
        if self.joy_msg is None:
            return

        # Check timing since last command
        if self.last_command_time is not None:
            elapsed = (rospy.Time.now() - self.last_command_time).to_sec()
            if elapsed < (self.adaptive_duration * 0.8):
                return  # Prevent overlap

        # Track latency if possible
        if self.last_joy_time:
            latency = (rospy.Time.now() - self.last_joy_time).to_sec()
            self.latencies.append(latency)

        # Update adaptive parameters periodically
        if len(self.latencies) > 0 and len(self.latencies) % 10 == 0:
            self.calculate_adaptive_params()

        # Read joystick
        msg = self.joy_msg
        if len(msg.axes) <= max(self.axis_yaw, self.axis_pitch):
            return

        raw_yaw = msg.axes[self.axis_yaw]
        raw_pitch = msg.axes[self.axis_pitch]

        # Apply dead-band
        if abs(raw_yaw) < self.snap_threshold:
            raw_yaw = 0.0
        if abs(raw_pitch) < self.snap_threshold:
            raw_pitch = 0.0

        # Calculate target angles
        self.target_yaw = raw_yaw * self.max_angle * self.yaw_invert
        self.target_pitch = raw_pitch * self.max_angle * self.pitch_invert

        # Apply smoothing for smoother motion
        self.current_yaw = self.smooth_position(
            self.target_yaw, self.current_yaw, self.smoothing_factor)
        self.current_pitch = self.smooth_position(
            self.target_pitch, self.current_pitch, self.smoothing_factor)

        # Build trajectory
        traj = JointTrajectory()
        traj.joint_names = ["HEAD_JOINT0", "HEAD_JOINT1"]

        point = JointTrajectoryPoint()
        point.positions = [self.current_yaw, self.current_pitch]
        point.velocities = [0.0, 0.0]
        point.accelerations = [0.0, 0.0]
        point.time_from_start = rospy.Duration(self.adaptive_duration)

        traj.points = [point]

        # Publish
        self.pub.publish(traj)
        self.last_command_time = rospy.Time.now()

        # Debug output
        rospy.logdebug_throttle(2,
            "Adaptive: duration=%.2fs, rate=%.1fHz, smooth=%.2f, latency=%.0fms" %
            (self.adaptive_duration, self.adaptive_rate, self.smoothing_factor,
             np.mean(self.latencies) * 1000 if self.latencies else 0))

    def run(self):
        """Main control loop"""
        rospy.Subscriber("/joy", Joy, self.joy_cb, queue_size=1)

        # Dynamic timer that can adjust its rate
        while not rospy.is_shutdown():
            self.timer_cb(None)
            rospy.sleep(1.0 / self.adaptive_rate)

if __name__ == "__main__":
    rospy.init_node("joy_head_adaptive")
    controller = AdaptiveHeadControl()
    controller.run()