#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick diagnostics tool - run once to get system status
"""

import rospy
import time
import subprocess
import os
from sensor_msgs.msg import Joy
from trajectory_msgs.msg import JointTrajectory

class QuickDiagnostics:
    def __init__(self):
        self.joy_count = 0
        self.cmd_count = 0
        self.joy_times = []
        self.cmd_times = []
        self.start_time = time.time()

    def joy_cb(self, msg):
        self.joy_count += 1
        self.joy_times.append(time.time() - self.start_time)

    def cmd_cb(self, msg):
        self.cmd_count += 1
        self.cmd_times.append(time.time() - self.start_time)

    def run_diagnostics(self, duration=3):
        """Collect data for specified duration"""
        print("\n" + "="*60)
        print("🔍 ROBOT CONTROL SYSTEM DIAGNOSTICS")
        print("="*60)

        # Set ROS environment
        os.environ['ROS_MASTER_URI'] = 'http://133.11.216.57:11311'
        os.environ['ROS_IP'] = '133.11.216.68'

        # Initialize ROS
        rospy.init_node("quick_diagnostics", anonymous=True)

        # Check connection
        try:
            rospy.wait_for_service('/rosout/get_loggers', timeout=2)
            print("✅ ROS Master connected")
        except:
            print("❌ Cannot connect to ROS Master")
            return

        # Subscribe
        rospy.Subscriber("/joy", Joy, self.joy_cb, queue_size=1)
        rospy.Subscriber("/head_controller/command", JointTrajectory,
                        self.cmd_cb, queue_size=1)

        print(f"📊 Collecting data for {duration} seconds...")
        print("   (Move the joystick to generate data)")

        # Collect data
        time.sleep(duration)

        # Analyze
        print("\n" + "-"*60)
        print("RESULTS:")
        print("-"*60)

        # Joystick analysis
        if self.joy_count > 0:
            joy_rate = self.joy_count / duration
            print(f"\n🎮 Joystick (/joy):")
            print(f"   Messages received: {self.joy_count}")
            print(f"   Average rate: {joy_rate:.1f} Hz")

            if len(self.joy_times) > 1:
                intervals = [self.joy_times[i+1] - self.joy_times[i]
                           for i in range(len(self.joy_times)-1)]
                avg_interval = sum(intervals) / len(intervals) * 1000
                max_interval = max(intervals) * 1000
                min_interval = min(intervals) * 1000
                jitter = max_interval - min_interval

                print(f"   Avg interval: {avg_interval:.1f}ms")
                print(f"   Jitter: {jitter:.1f}ms")

                if jitter > 20:
                    print("   ⚠️  High jitter detected!")
        else:
            print("\n⚠️  No joystick messages received")
            print("   Check: Is joy_node running?")

        # Command analysis
        if self.cmd_count > 0:
            cmd_rate = self.cmd_count / duration
            print(f"\n🤖 Head Commands (/head_controller/command):")
            print(f"   Messages sent: {self.cmd_count}")
            print(f"   Average rate: {cmd_rate:.1f} Hz")

            if len(self.cmd_times) > 1:
                intervals = [self.cmd_times[i+1] - self.cmd_times[i]
                           for i in range(len(self.cmd_times)-1)]
                avg_interval = sum(intervals) / len(intervals) * 1000
                jitter = (max(intervals) - min(intervals)) * 1000

                print(f"   Avg interval: {avg_interval:.1f}ms")
                print(f"   Jitter: {jitter:.1f}ms")
        else:
            print("\n⚠️  No command messages sent")
            print("   Check: Is joy_head control running?")

        # Network latency estimate
        if self.joy_count > 0 and self.cmd_count > 0:
            # Simple check - are rates similar?
            rate_diff = abs(self.joy_count - self.cmd_count)
            if rate_diff > 5:
                print("\n⚠️  Message rate mismatch!")
                print(f"   Joy: {self.joy_count} vs Cmd: {self.cmd_count}")
                print("   Possible command dropping or queuing")

        # Recommendations
        print("\n" + "-"*60)
        print("💡 RECOMMENDATIONS:")
        print("-"*60)

        if self.joy_count == 0:
            print("1. Start joystick node: ./2_joystick.sh")
        elif self.cmd_count == 0:
            print("1. Start head control: ./4_robot_head.sh")
        elif self.joy_count > 0 and self.cmd_count > 0:
            joy_rate = self.joy_count / duration
            cmd_rate = self.cmd_count / duration

            if cmd_rate > 20:
                print("1. ⚠️  Command rate too high (>20Hz)")
                print("   Try: ./safe_smooth_control.sh")
            elif cmd_rate < 5:
                print("1. ⚠️  Command rate too low (<5Hz)")
                print("   Response might feel sluggish")

            if abs(joy_rate - 30) > 5:
                print("2. Joystick rate not optimal (should be ~30Hz)")

            print("\n✅ For best results, try:")
            print("   ./adaptive_control.sh (auto-adjusts to network)")

if __name__ == "__main__":
    diag = QuickDiagnostics()
    diag.run_diagnostics(3)