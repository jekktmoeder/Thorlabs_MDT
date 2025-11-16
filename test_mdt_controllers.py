#!/usr/bin/env python
"""
Test script for MDT controller functionality

This script demonstrates and tests the MDT controller classes with your actual devices.
"""

from mdt_controller import MDTController, HighLevelMDTController, discover_mdt_devices

def test_device_discovery():
    """Test device discovery"""
    print("=== Device Discovery Test ===")
    devices = discover_mdt_devices()
    print(f"Found {len(devices)} MDT devices:")
    for device in devices:
        model = device.get("Model", "Unknown")
        port = device.get("Device", "Unknown") 
        serial = device.get("SerialNumber", "N/A")
        print(f"  {model} on {port} (SN: {serial})")
    return devices

def test_low_level_controller():
    """Test low-level controller"""
    print("\n=== Low-Level Controller Test ===")
    
    devices = discover_mdt_devices()
    if not devices:
        print("No devices found")
        return
        
    device = devices[0]  # Use first device
    port = device["Device"]
    model = device.get("Model", "Unknown")
    
    print(f"Testing {model} on {port}")
    
    with MDTController(port=port, model=model) as controller:
        if controller.is_connected:
            # Test device info
            info = controller.get_device_info()
            print(f"Device info: {info}")
            
            # Test voltage reading
            for axis in controller.axes:
                voltage = controller.get_voltage(axis)
                limits = controller.get_voltage_limits(axis)
                print(f"{axis}-axis: {voltage}V (range: {limits[0]}-{limits[1]}V)")
            
            # Test all voltages
            all_voltages = controller.get_all_voltages()
            print(f"All voltages: {all_voltages}")
        else:
            print("Failed to connect")

def test_high_level_controller():
    """Test high-level controller with safety features"""
    print("\n=== High-Level Controller Test ===")
    
    with HighLevelMDTController() as mdt:
        if mdt.is_connected():
            # Get status
            status = mdt.get_device_status()
            print(f"Status: {status['status']}")
            print(f"Device: {status['model']} on {status['port']}")
            print(f"Axes: {status['axes']}")
            print(f"Current voltages: {status['current_voltages']}")
            
            # Test safety limits
            print(f"Safety limits: {status['voltage_limits']}")
            
            # Test safe voltage setting (small value)
            print("\nTesting safe voltage setting...")
            if mdt.set_voltage_safe("X", 2.0):
                print("✓ Safe voltage set successful")
            else:
                print("✗ Safe voltage set failed")
            
            # Wait a moment then read back
            import time
            time.sleep(0.5)
            current_x = mdt.controller.get_voltage("X")
            print(f"Current X voltage: {current_x}V")
            
            # Test relative movement
            print("\nTesting relative movement...")
            if mdt.move_relative("X", 1.0):  # +1V
                print("✓ Relative move successful")
                time.sleep(0.5)
                new_x = mdt.controller.get_voltage("X")
                print(f"New X voltage: {new_x}V")
            
            # Return to zero
            print("\nZeroing all axes...")
            if mdt.zero_all_axes():
                print("✓ All axes zeroed")
                time.sleep(0.5)
                final_voltages = mdt.controller.get_all_voltages()
                print(f"Final voltages: {final_voltages}")
            
        else:
            print("No device connected")

def test_multi_axis_device():
    """Test 3-axis device if available"""
    print("\n=== Multi-Axis Device Test ===")
    
    devices = discover_mdt_devices()
    multi_axis_device = None
    
    # Find a 693 device (3-axis)
    for device in devices:
        if "693" in device.get("Model", ""):
            multi_axis_device = device
            break
    
    if not multi_axis_device:
        print("No 3-axis device found")
        return
    
    port = multi_axis_device["Device"]
    model = multi_axis_device["Model"]
    
    print(f"Testing {model} on {port}")
    
    with HighLevelMDTController(port=port, model=model) as mdt:
        if mdt.is_connected():
            # Test setting multiple voltages
            test_voltages = {"X": 1.0, "Y": 1.5, "Z": 2.0}
            print(f"Setting voltages: {test_voltages}")
            
            if mdt.set_all_voltages_safe(test_voltages):
                print("✓ Multi-axis voltage set successful")
                
                import time
                time.sleep(0.5)
                
                actual = mdt.controller.get_all_voltages()
                print(f"Actual voltages: {actual}")
                
                # Verify values
                tolerance = 0.5
                for axis, target in test_voltages.items():
                    if axis in actual:
                        diff = abs(actual[axis] - target)
                        if diff <= tolerance:
                            print(f"  ✓ {axis}: {actual[axis]:.2f}V (target: {target}V)")
                        else:
                            print(f"  ⚠ {axis}: {actual[axis]:.2f}V (target: {target}V, diff: {diff:.2f}V)")
            
            # Zero all
            print("\nZeroing all axes...")
            mdt.zero_all_axes()
        else:
            print("Failed to connect to multi-axis device")

def test_safety_features():
    """Test safety and limit features"""
    print("\n=== Safety Features Test ===")
    
    with HighLevelMDTController() as mdt:
        if mdt.is_connected():
            print("Testing safety limits...")
            
            # Try to set voltage beyond safe limit (should fail)
            print("Attempting to set 120V (should be blocked by safety)...")
            success = mdt.set_voltage_safe("X", 120.0)
            if not success:
                print("✓ Safety limit correctly blocked high voltage")
            else:
                print("⚠ Safety limit did not block high voltage")
                
            # Disable safety and try again
            print("Disabling safety limits...")
            mdt.enable_safety(False)
            
            print("Attempting 5V with safety disabled...")
            success = mdt.set_voltage_safe("X", 5.0)
            if success:
                print("✓ Voltage set with safety disabled")
                
                # Return to zero
                mdt.zero_all_axes()
            
            # Re-enable safety
            mdt.enable_safety(True)
            print("Safety limits re-enabled")
        else:
            print("No device connected")

def main():
    """Run all tests"""
    print("MDT Controller Comprehensive Test")
    print("=" * 35)
    
    try:
        # Test device discovery
        devices = test_device_discovery()
        
        if not devices:
            print("No MDT devices found. Please check connections.")
            return
        
        # Test low-level controller
        test_low_level_controller()
        
        # Test high-level controller
        test_high_level_controller()
        
        # Test multi-axis if available
        test_multi_axis_device()
        
        # Test safety features
        test_safety_features()
        
        print(f"\n{'='*35}")
        print("All tests completed!")
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()