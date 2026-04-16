#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
network_monitor.py
------------------
ROS network and topic monitoring for latency analysis
"""

import rospy
import time
from sensor_msgs.msg import Joy
from trajectory_msgs.msg import JointTrajectory
from collections import deque

class NetworkMonitor:
    def __init__(self):
        self.joy_times = deque(maxlen=100)
        self.cmd_times = deque(maxlen=100)
        self.latencies = deque(maxlen=100)
        self.last_joy_time = None
        self.last_cmd_time = None

        # Track message intervals
        self.joy_intervals = deque(maxlen=50)
        self.cmd_intervals = deque(maxlen=50)

    def joy_cb(self, msg):
        """Track joystick message timing"""
        current_time = rospy.Time.now()

        if self.last_joy_time:
            interval = (current_time - self.last_joy_time).to_sec()
            self.joy_intervals.append(interval)

        self.last_joy_time = current_time
        self.joy_times.append(current_time.to_sec())

    def cmd_cb(self, msg):
        """Track command message timing"""
        current_time = rospy.Time.now()

        if self.last_cmd_time:
            interval = (current_time - self.last_cmd_time).to_sec()
            self.cmd_intervals.append(interval)

        self.last_cmd_time = current_time
        self.cmd_times.append(current_time.to_sec())

    def analyze(self):
        """Analyze network performance"""
        if len(self.joy_intervals) > 10 and len(self.cmd_intervals) > 10:
            # Joy message statistics
            joy_avg = sum(self.joy_intervals) / len(self.joy_intervals)
            joy_max = max(self.joy_intervals)
            joy_min = min(self.joy_intervals)

            # Command message statistics
            cmd_avg = sum(self.cmd_intervals) / len(self.cmd_intervals)
            cmd_max = max(self.cmd_intervals)
            cmd_min = min(self.cmd_intervals)

            # Calculate jitter (variation in intervals)
            joy_jitter = joy_max - joy_min
            cmd_jitter = cmd_max - cmd_min

            print("\n" + "="*50)
            print("📊 Network Performance Analysis")
            print("="*50)

            print("\n🎮 Joystick Messages (/joy):")
            print(f"  Avg interval: {joy_avg*1000:.1f}ms")
            print(f"  Min/Max: {joy_min*1000:.1f}ms / {joy_max*1000:.1f}ms")
            print(f"  Jitter: {joy_jitter*1000:.1f}ms")

            print("\n🤖 Command Messages (/head_controller/command):")
            print(f"  Avg interval: {cmd_avg*1000:.1f}ms")
            print(f"  Min/Max: {cmd_min*1000:.1f}ms / {cmd_max*1000:.1f}ms")
            print(f"  Jitter: {cmd_jitter*1000:.1f}ms")

            # Warnings
            if joy_jitter > 0.05:  # >50ms jitter
                print("\n⚠️  High joystick jitter detected!")
            if cmd_jitter > 0.1:  # >100ms jitter
                print("\n⚠️  High command jitter detected!")

            # Estimate latency between joy and command
            if self.joy_times and self.cmd_times:
                # Simple estimation: average time between joy and next command
                estimated_latency = (self.cmd_times[-1] - self.joy_times[-1]) * 1000
                print(f"\n⏱️  Estimated processing latency: {abs(estimated_latency):.1f}ms")

            print("\n💡 Recommendations:")
            if joy_jitter > 0.05:
                print("  • Network connection unstable - check WiFi/ethernet")
            if cmd_avg > 0.15:
                print("  • Commands too infrequent - increase rate parameter")
            if cmd_jitter > 0.1:
                print("  • Inconsistent command timing - check CPU load")

if __name__ == "__main__":
    rospy.init_node("network_monitor")
    monitor = NetworkMonitor()

    # Subscribe to topics
    rospy.Subscriber("/joy", Joy, monitor.joy_cb, queue_size=1)
    rospy.Subscriber("/head_controller/command", JointTrajectory,
                     monitor.cmd_cb, queue_size=1)

    print("🔍 Monitoring network performance...")
    print("Move the joystick for 10 seconds to collect data...")

    # Analyze every 5 seconds
    rate = rospy.Rate(0.2)  # 0.2Hz = every 5 seconds
    while not rospy.is_shutdown():
        monitor.analyze()
        rate.sleep()