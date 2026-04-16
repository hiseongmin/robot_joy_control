#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Passive monitoring - doesn't interfere with control
Just watches the message flow without subscribing
"""

import subprocess
import time
import os

def run_passive_diagnostics():
    """Monitor without creating ROS node"""
    print("\n" + "="*60)
    print("🔍 PASSIVE SYSTEM MONITOR (Non-intrusive)")
    print("="*60)

    # Set ROS environment
    os.environ['ROS_MASTER_URI'] = 'http://133.11.216.57:11311'
    os.environ['ROS_IP'] = '133.11.216.68'

    # Check connection
    try:
        result = subprocess.run(['rostopic', 'list'],
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print("✅ ROS Master connected")
        else:
            print("❌ Cannot connect to ROS Master")
            return
    except:
        print("❌ ROS not available")
        return

    print("\n📊 Monitoring for 3 seconds...")
    print("   (Keep using joystick normally)")

    # Monitor joy topic rate (non-intrusive)
    try:
        print("\n🎮 Checking Joystick (/joy)...")
        result = subprocess.run(['timeout', '2', 'rostopic', 'hz', '/joy'],
                              capture_output=True, text=True)

        if "average rate:" in result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if "average rate:" in line:
                    rate = line.split("average rate:")[1].strip()
                    print(f"   Rate: {rate}")
                elif "min:" in line:
                    print(f"   {line.strip()}")
        else:
            print("   ⚠️  No joystick messages")
    except Exception as e:
        print(f"   Error: {e}")

    # Monitor command topic rate
    try:
        print("\n🤖 Checking Head Commands (/head_controller/command)...")
        result = subprocess.run(['timeout', '2', 'rostopic', 'hz',
                               '/head_controller/command'],
                              capture_output=True, text=True)

        if "average rate:" in result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if "average rate:" in line:
                    rate = line.split("average rate:")[1].strip()
                    print(f"   Rate: {rate}")
                elif "min:" in line:
                    print(f"   {line.strip()}")
        else:
            print("   ⚠️  No command messages")
    except Exception as e:
        print(f"   Error: {e}")

    # Check node status
    print("\n📡 Active Nodes:")
    try:
        result = subprocess.run(['rosnode', 'list'],
                              capture_output=True, text=True, timeout=2)
        nodes = result.stdout.strip().split('\n')
        joy_nodes = [n for n in nodes if 'joy' in n.lower() or 'head' in n.lower()]
        for node in joy_nodes:
            print(f"   • {node}")
    except:
        pass

    # Simple network ping test
    print("\n🌐 Network Latency to Robot:")
    try:
        result = subprocess.run(['ping', '-c', '3', '-W', '1', '133.11.216.57'],
                              capture_output=True, text=True)
        if "avg" in result.stdout:
            for line in result.stdout.split('\n'):
                if "avg" in line:
                    print(f"   {line.strip()}")
    except:
        pass

    print("\n" + "-"*60)
    print("💡 ANALYSIS:")
    print("-"*60)
    print("This monitor runs PASSIVELY - doesn't interfere with control")
    print("If rates look good but control is delayed, check:")
    print("  1. Network stability (ping times)")
    print("  2. CPU load on robot")
    print("  3. WiFi signal strength")

if __name__ == "__main__":
    run_passive_diagnostics()