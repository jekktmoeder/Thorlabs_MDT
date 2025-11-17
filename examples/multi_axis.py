#!/usr/bin/env python
# SPDX-License-Identifier: MIT
"""
Multi-Axis Control Example

This example demonstrates controlling all three axes of an MDT693A/B device.
"""

import sys
import os
import time

# Add src to path for development
root = os.path.dirname(os.path.dirname(__file__))
src = os.path.join(root, 'src')
if src not in sys.path:
    sys.path.insert(0, src)

from mdt import HighLevelMDTController


def main():
    """Multi-axis control example."""
    
    print("=== Multi-Axis Control Example ===\n")
    
    # Connect to specific 3-axis device (or auto-discover)
    # Change port to match your device (check find_MDT_devices.py output)
    with HighLevelMDTController(port="COM9") as mdt:  # Replace with your port
        if not mdt.is_connected():
            print("✗ Failed to connect")
            print("  Tip: Run 'python find_MDT_devices.py' to see available devices")
            return 1
        
        status = mdt.get_device_status()
        print(f"✓ Connected to: {status['model']} on {status['port']}")
        
        # Verify device is 3-axis
        if len(status['axes']) < 3:
            print(f"⚠ This example requires a 3-axis device (MDT693A/B)")
            print(f"  Your device has axes: {status['axes']}")
            return 1
        
        print(f"  Axes: {status['axes']}\n")
        
        # Example 1: Set each axis individually
        print("Example 1: Individual Axis Control")
        print("-" * 40)
        
        voltages_individual = {"X": 10.0, "Y": 15.0, "Z": 20.0}
        for axis, voltage in voltages_individual.items():
            print(f"Setting {axis} = {voltage}V...")
            mdt.set_voltage_safe(axis, voltage)
            time.sleep(0.1)  # Brief settling time
        
        # Read back
        actual = mdt.controller.get_all_voltages()
        print(f"Actual voltages: {actual}\n")
        
        # Example 2: Set all axes simultaneously
        print("Example 2: Simultaneous Multi-Axis Control")
        print("-" * 40)
        
        voltages_batch = {"X": 25.0, "Y": 30.0, "Z": 35.0}
        print(f"Setting all axes: {voltages_batch}")
        mdt.set_all_voltages_safe(voltages_batch)
        time.sleep(0.2)
        
        actual = mdt.controller.get_all_voltages()
        print(f"Actual voltages: {actual}\n")
        
        # Example 3: Relative movements
        print("Example 3: Relative Movements")
        print("-" * 40)
        
        print("Adding +5V to each axis...")
        for axis in ["X", "Y", "Z"]:
            mdt.move_relative(axis, +5.0)
            time.sleep(0.1)
        
        actual = mdt.controller.get_all_voltages()
        print(f"New voltages: {actual}\n")
        
        # Example 4: Create a voltage pattern
        print("Example 4: Voltage Pattern (Diagonal Sweep)")
        print("-" * 40)
        
        print("Sweeping all axes from 0V to 20V...")
        for v in range(0, 25, 5):
            voltages = {"X": float(v), "Y": float(v), "Z": float(v)}
            mdt.set_all_voltages_safe(voltages)
            actual = mdt.controller.get_all_voltages()
            print(f"  Set: {v}V → Actual: X={actual['X']:.1f}, "
                  f"Y={actual['Y']:.1f}, Z={actual['Z']:.1f}")
            time.sleep(0.3)
        
        # Return to zero
        print("\n🔄 Returning to safe state...")
        mdt.zero_all_axes()
        print("✓ All axes zeroed")
    
    print("\n✓ Example completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
