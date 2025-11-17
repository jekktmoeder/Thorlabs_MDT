#!/usr/bin/env python
# SPDX-License-Identifier: MIT
"""
Voltage Scanning Example

This example demonstrates how to perform a voltage scan for experimental measurements.
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
    """Voltage scanning example."""
    
    print("=== Voltage Scanning Example ===\n")
    
    with HighLevelMDTController() as mdt:
        if not mdt.is_connected():
            print("✗ No MDT devices found")
            return 1
        
        status = mdt.get_device_status()
        print(f"✓ Connected to: {status['model']} on {status['port']}")
        first_axis = status['axes'][0]
        print(f"  Scanning {first_axis}-axis\n")
        
        # Method 1: Using built-in scan_axis
        print("Method 1: Built-in Scan Function")
        print("-" * 50)
        
        start_v = 0.0
        end_v = 50.0
        num_steps = 11
        step_time = 0.2  # seconds
        
        print(f"Scanning {first_axis} from {start_v}V to {end_v}V "
              f"in {num_steps} steps...")
        
        scan_data = mdt.scan_axis(
            first_axis, 
            start_v=start_v,
            end_v=end_v,
            steps=num_steps,
            step_time=step_time
        )
        
        print(f"\nScan Results:")
        print(f"{'Step':<6} {'Target (V)':<12} {'Actual (V)':<12} {'Error (V)':<12}")
        print("-" * 50)
        for i, (target, actual) in enumerate(scan_data):
            error = actual - target
            print(f"{i+1:<6} {target:<12.2f} {actual:<12.2f} {error:<12.3f}")
        
        # Method 2: Manual scan with custom logic
        print("\n\nMethod 2: Manual Scan (with custom processing)")
        print("-" * 50)
        
        print(f"Scanning {first_axis} with custom step logic...")
        
        voltages = [0, 10, 20, 30, 40, 50, 40, 30, 20, 10, 0]  # Up and down
        measurements = []
        
        for i, voltage in enumerate(voltages):
            # Set voltage
            mdt.set_voltage_safe(first_axis, float(voltage))
            time.sleep(0.15)  # Settling time
            
            # Read back actual voltage
            actual = mdt.controller.get_voltage(first_axis)
            
            # Simulate measurement (replace with your measurement code)
            # measurement_value = measure_something()
            measurement_value = actual * 2.5  # Placeholder
            
            measurements.append({
                'step': i + 1,
                'target': voltage,
                'actual': actual,
                'measurement': measurement_value
            })
            
            print(f"Step {i+1:2d}: {voltage:5.1f}V → {actual:6.2f}V "
                  f"(Measurement: {measurement_value:.3f})")
        
        # Method 3: Fine scan around a feature
        print("\n\nMethod 3: Fine Scan (high resolution)")
        print("-" * 50)
        
        center_v = 25.0
        scan_range = 2.0  # ±2V around center
        fine_steps = 21  # 0.2V resolution
        
        print(f"Fine scanning around {center_v}V...")
        
        fine_scan = []
        for i in range(fine_steps):
            voltage = center_v - scan_range + (2 * scan_range * i / (fine_steps - 1))
            mdt.set_voltage_safe(first_axis, voltage)
            time.sleep(0.1)
            actual = mdt.controller.get_voltage(first_axis)
            fine_scan.append((voltage, actual))
            
            if i % 5 == 0:  # Print every 5th point
                print(f"  {voltage:.2f}V → {actual:.2f}V")
        
        print(f"\nFine scan completed: {len(fine_scan)} points")
        
        # Return to safe state
        print("\n🔄 Returning to zero...")
        mdt.zero_all_axes()
        print("✓ Scan completed and zeroed")
    
    print("\n✓ Example completed successfully")
    print("\nNext Steps:")
    print("  - Replace measurement placeholders with actual data acquisition")
    print("  - Save scan data to CSV/JSON for analysis")
    print("  - Integrate with plotting libraries (matplotlib)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
