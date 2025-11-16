#!/usr/bin/env python
"""
Diagnostic script for COM10 (MDT693A) communication issues
Tests raw serial commands and responses to identify protocol problems
"""

from mdt_controller import MDTController
import time

def test_com10():
    print("="*60)
    print("COM10 (MDT693A) Diagnostic Test")
    print("="*60)
    
    # Connect to COM10 with MDT693A model
    controller = MDTController(port="COM10", model="MDT693A", timeout=3.0)
    
    print("\n1. Testing connection...")
    if not controller.connect():
        print("   ❌ Failed to connect to COM10")
        return
    print(f"   ✓ Connected to {controller.model}")
    print(f"   - Legacy protocol: {controller.is_legacy_protocol}")
    print(f"   - Axes: {controller.axes}")
    print(f"   - Voltage range: {controller.voltage_min}V - {controller.voltage_max}V")
    
    print("\n2. Testing device identification...")
    id_response = controller.send_command("ID?")
    print(f"   ID? response: {repr(id_response)}")
    
    print("\n3. Testing each axis individually...")
    for axis in controller.axes:
        print(f"\n   --- Testing {axis}-axis ---")
        
        # Get current voltage
        print(f"   Querying current voltage...")
        current_cmd = f"{axis}VOLTAGE?"
        current_raw = controller.send_command(current_cmd, timeout=3.0)
        print(f"   Command: {current_cmd}")
        print(f"   Raw response: {repr(current_raw)}")
        current_voltage = controller.get_voltage(axis)
        print(f"   Parsed voltage: {current_voltage}V")
        
        # Try to set a test voltage (10V)
        test_voltage = 10.0
        print(f"\n   Setting {axis} to {test_voltage}V...")
        set_cmd = f"{axis}VOLTAGE={test_voltage:.2f}"
        set_response = controller.send_command(set_cmd, timeout=3.0)
        print(f"   Command: {set_cmd}")
        print(f"   Raw response: {repr(set_response)}")
        
        # Wait for device to settle
        time.sleep(0.3)
        
        # Read back the voltage
        print(f"   Reading back voltage...")
        readback_raw = controller.send_command(current_cmd, timeout=3.0)
        print(f"   Raw response: {repr(readback_raw)}")
        readback_voltage = controller.get_voltage(axis)
        print(f"   Parsed voltage: {readback_voltage}V")
        
        # Check if readback matches
        if readback_voltage is not None:
            diff = abs(readback_voltage - test_voltage)
            print(f"   Difference: {diff:.2f}V")
            if diff <= 1.0:
                print(f"   ✓ Verification successful")
            else:
                print(f"   ⚠ Voltage mismatch (expected {test_voltage}V, got {readback_voltage}V)")
        else:
            print(f"   ❌ Failed to read back voltage")
    
    print("\n4. Testing combined XYZ command...")
    xyz_response = controller.send_command("XYZVOLTAGE?", timeout=3.0)
    print(f"   XYZVOLTAGE? response: {repr(xyz_response)}")
    all_voltages = controller.get_all_voltages()
    print(f"   Parsed voltages: {all_voltages}")
    
    print("\n5. Testing voltage limits...")
    for axis in controller.axes:
        min_v, max_v = controller.get_voltage_limits(axis)
        print(f"   {axis}-axis limits: {min_v}V - {max_v}V")
    
    print("\n6. Raw buffer test (checking for extra characters)...")
    # Send a command and look at raw bytes
    controller.connection.reset_input_buffer()
    test_cmd = "XVOLTAGE?"
    cmd_bytes = test_cmd.encode('ascii') + b'\r\n'
    controller.connection.write(cmd_bytes)
    controller.connection.flush()
    time.sleep(0.3)
    
    raw_bytes = controller.connection.read(controller.connection.in_waiting)
    print(f"   Command sent: {repr(test_cmd)}")
    print(f"   Raw bytes received: {raw_bytes}")
    print(f"   Decoded: {repr(raw_bytes.decode('ascii', errors='ignore'))}")
    print(f"   Hex: {raw_bytes.hex()}")
    
    print("\n" + "="*60)
    print("Diagnostic Complete")
    print("="*60)
    
    controller.disconnect()

if __name__ == "__main__":
    test_com10()
