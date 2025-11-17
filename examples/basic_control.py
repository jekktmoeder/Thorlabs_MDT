#!/usr/bin/env python
# SPDX-License-Identifier: MIT
"""
Basic MDT Controller Example

This example demonstrates basic connection and voltage control
using the high-level API.
"""

import sys
import os

# Add src to path for development
root = os.path.dirname(os.path.dirname(__file__))
src = os.path.join(root, 'src')
if src not in sys.path:
    sys.path.insert(0, src)

from mdt import HighLevelMDTController


def main():
    """Basic controller usage example."""
    
    print("=== Basic MDT Controller Example ===\n")
    
    # Connect to first available device (auto-discovery)
    with HighLevelMDTController() as mdt:
        if not mdt.is_connected():
            print("✗ No MDT devices found")
            print("\nTroubleshooting:")
            print("  1. Ensure device is powered on and connected")
            print("  2. Run: python find_MDT_devices.py")
            print("  3. Check COM port in Device Manager")
            return 1
        
        # Get device status
        status = mdt.get_device_status()
        print(f"✓ Connected to: {status['model']} on {status['port']}")
        print(f"  Axes: {status['axes']}")
        print(f"  Current voltages: {status['current_voltages']}\n")
        
        # Read current voltage for first axis
        first_axis = status['axes'][0]
        current_v = mdt.controller.get_voltage(first_axis)
        print(f"📊 Current {first_axis}-axis voltage: {current_v:.2f}V\n")
        
        # Set voltage safely (respects 100V default safety limit)
        target_voltage = 15.0
        print(f"Setting {first_axis}-axis to {target_voltage}V...")
        success = mdt.set_voltage_safe(first_axis, target_voltage)
        
        if success:
            # Verify by reading back
            actual_v = mdt.controller.get_voltage(first_axis)
            print(f"✓ Voltage set successfully: {actual_v:.2f}V\n")
        else:
            print(f"✗ Failed to set voltage\n")
            return 1
        
        # Display voltage limits
        print("📋 Voltage Limits:")
        for axis in status['axes']:
            limits = status['voltage_limits'][axis]
            print(f"  {axis}: {limits['min']:.1f}V - {limits['max']:.1f}V "
                  f"(safe max: {limits['safe_max']:.1f}V)")
        
        # Return to zero (safe operation)
        print("\n🔄 Returning to zero...")
        mdt.zero_all_axes()
        print("✓ All axes zeroed")
    
    print("\n✓ Example completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
