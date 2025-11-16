#!/usr/bin/env python
"""
test_mdt_sdk.py - Systematically test MDT SDK functions across different device models
to discover actual API behavior and command differences.

This script will:
1. Connect to each discovered MDT device
2. Test all SDK functions safely 
3. Document which functions work with which models
4. Map out voltage ranges, limits, and capabilities
5. Generate a compatibility matrix
"""

import sys
import os
import json
import time
import struct
import shutil
from typing import Dict, List, Optional, Any

def setup_mdt_sdk():
    """Setup MDT SDK with correct architecture DLLs"""
    sdk_path = r"C:\Program Files (x86)\Thorlabs\MDT69XB\Sample\Thorlabs_MDT69XB_PythonSDK"
    
    if not os.path.exists(sdk_path):
        raise RuntimeError(f"SDK path not found: {sdk_path}")
    
    # Determine Python architecture
    is_64bit = struct.calcsize('P') == 8
    dll_suffix = "x64" if is_64bit else "win32"
    
    print(f"Python architecture: {'64-bit' if is_64bit else '32-bit'}")
    print(f"Using DLL: MDT_COMMAND_LIB_{dll_suffix}.dll")
    
    # Create local DLL directory
    local_dll_dir = ".mdt_dlls"
    os.makedirs(local_dll_dir, exist_ok=True)
    
    # Copy appropriate DLL
    src_dll = os.path.join(sdk_path, f"MDT_COMMAND_LIB_{dll_suffix}.dll")
    dst_dll = os.path.join(local_dll_dir, "MDT_COMMAND_LIB.dll")
    
    if not os.path.exists(src_dll):
        raise RuntimeError(f"DLL not found: {src_dll}")
    
    if not os.path.exists(dst_dll) or os.path.getmtime(src_dll) > os.path.getmtime(dst_dll):
        shutil.copy2(src_dll, dst_dll)
        print(f"✓ Copied {dll_suffix} DLL to local directory")
    
    return local_dll_dir

# Setup SDK and import our local wrapper
try:
    dll_dir = setup_mdt_sdk()
    
    # Change to our directory for DLL loading
    original_cwd = os.getcwd()
    
    # Import our local SDK wrapper
    from MDT_COMMAND_LIB_LOCAL import *
    print("✓ MDT SDK imported successfully")
    
except Exception as e:
    print(f"✗ Failed to setup/import MDT SDK: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Load device list
def load_devices():
    try:
        with open("mdt_devices.json", "r") as f:
            devices = json.load(f)
        return [d for d in devices if d.get("Model") and "MDT" in d.get("Model", "")]
    except Exception as e:
        print(f"Failed to load mdt_devices.json: {e}")
        return []

class MDTTester:
    def __init__(self):
        self.results = {}
        self.devices = load_devices()
        
    def safe_call(self, func_name, *args, **kwargs):
        """Safely call an MDT function and return result or error"""
        try:
            func = globals().get(func_name)
            if not func:
                return {"error": f"Function {func_name} not found"}
            
            result = func(*args, **kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}
    
    def test_device_discovery(self):
        """Test device enumeration"""
        print("\n=== Testing Device Discovery ===")
        
        result = self.safe_call("mdtListDevices")
        if "error" in result:
            print(f"✗ mdtListDevices failed: {result['error']}")
            return []
        
        sdk_devices = result["result"]
        print(f"✓ SDK found {len(sdk_devices)} devices")
        
        for i, dev in enumerate(sdk_devices):
            serial_no, model = dev
            print(f"  Device {i+1}: Serial={serial_no}, Model={model}")
        
        return sdk_devices
    
    def test_device_connection(self, serial_no, model):
        """Test opening/closing device connection"""
        print(f"\n=== Testing Connection: {model} (SN: {serial_no}) ===")
        
        # Test mdtOpen with different baud rates
        baud_rates = [115200, 9600, 57600, 38400]
        handle = None
        
        for baud in baud_rates:
            print(f"Trying baud rate: {baud}")
            result = self.safe_call("mdtOpen", serial_no, baud, 1000)
            
            if "error" not in result:
                handle = result["result"]
                print(f"✓ Connected at {baud} baud, handle: {handle}")
                break
            else:
                print(f"✗ Failed at {baud}: {result['error']}")
        
        if handle is None:
            print("✗ Could not connect to device")
            return None
        
        # Test connection status
        is_open = self.safe_call("mdtIsOpen", serial_no)
        print(f"mdtIsOpen result: {is_open}")
        
        return handle
    
    def test_device_info(self, handle, serial_no, model):
        """Test device identification functions"""
        print(f"\n=== Testing Device Info ===")
        
        # Test ID retrieval
        id_result = self.safe_call("mdtGetId", handle, "")  # May need different params
        print(f"mdtGetId: {id_result}")
        
        return id_result
    
    def test_voltage_functions(self, handle, model):
        """Test voltage control functions"""
        print(f"\n=== Testing Voltage Functions ({model}) ===")
        
        results = {}
        channels = 3 if "693" in model else 1
        
        # Test limit voltage first (safety)
        limit_test = self.safe_call("mdtGetLimtVoltage", handle, 0.0)
        print(f"mdtGetLimtVoltage: {limit_test}")
        results["limit_voltage"] = limit_test
        
        # Test each axis based on device capabilities
        axes = ["X"]
        if channels == 3:
            axes.extend(["Y", "Z"])
        
        for axis in axes:
            print(f"\n--- Testing {axis}-Axis ---")
            axis_results = {}
            
            # Get current voltage
            get_func = f"mdtGet{axis}AxisVoltage"
            voltage_result = self.safe_call(get_func, handle, 0.0)
            print(f"{get_func}: {voltage_result}")
            axis_results["get_voltage"] = voltage_result
            
            # Get min voltage
            min_func = f"mdtGet{axis}AxisMinVoltage"
            min_result = self.safe_call(min_func, handle, 0.0)
            print(f"{min_func}: {min_result}")
            axis_results["get_min"] = min_result
            
            # Get max voltage  
            max_func = f"mdtGet{axis}AxisMaxVoltage"
            max_result = self.safe_call(max_func, handle, 0.0)
            print(f"{max_func}: {max_result}")
            axis_results["get_max"] = max_result
            
            results[f"{axis.lower()}_axis"] = axis_results
        
        # Test multi-axis functions (if 3-channel)
        if channels == 3:
            print(f"\n--- Testing Multi-Axis ---")
            xyz_get = self.safe_call("mdtGetXYZAxisVoltage", handle, [0.0, 0.0, 0.0])
            print(f"mdtGetXYZAxisVoltage: {xyz_get}")
            results["xyz_get"] = xyz_get
        
        # Test adjustment resolution
        res_result = self.safe_call("mdtGetVoltageAdjustmentResolution", handle, 0.0)
        print(f"mdtGetVoltageAdjustmentResolution: {res_result}")
        results["resolution"] = res_result
        
        return results
    
    def test_scan_functions(self, handle, model):
        """Test scanning functions"""
        print(f"\n=== Testing Scan Functions ({model}) ===")
        
        results = {}
        
        # Master scan enable
        scan_enable = self.safe_call("mdtGetMasterScanEnable", handle, False)
        print(f"mdtGetMasterScanEnable: {scan_enable}")
        results["scan_enable"] = scan_enable
        
        # Master scan voltage
        scan_voltage = self.safe_call("mdtGetMasterScanVoltage", handle, 0.0)
        print(f"mdtGetMasterScanVoltage: {scan_voltage}")
        results["scan_voltage"] = scan_voltage
        
        return results
    
    def test_device_fully(self, serial_no, model):
        """Complete test of a single device"""
        print(f"\n{'='*60}")
        print(f"TESTING DEVICE: {model} (Serial: {serial_no})")
        print(f"{'='*60}")
        
        device_results = {
            "serial_no": serial_no,
            "model": model,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 1. Connect
        handle = self.test_device_connection(serial_no, model)
        if handle is None:
            device_results["status"] = "connection_failed"
            return device_results
        
        device_results["handle"] = handle
        device_results["status"] = "connected"
        
        try:
            # 2. Device info
            device_results["device_info"] = self.test_device_info(handle, serial_no, model)
            
            # 3. Voltage functions
            device_results["voltage_functions"] = self.test_voltage_functions(handle, model)
            
            # 4. Scan functions  
            device_results["scan_functions"] = self.test_scan_functions(handle, model)
            
            device_results["status"] = "test_complete"
            
        except Exception as e:
            device_results["status"] = f"test_error: {e}"
            print(f"✗ Error during testing: {e}")
        
        finally:
            # 5. Disconnect
            print(f"\n=== Disconnecting ===")
            close_result = self.safe_call("mdtClose", handle)
            print(f"mdtClose: {close_result}")
            device_results["close_result"] = close_result
        
        return device_results
    
    def run_full_test(self):
        """Test all discovered devices"""
        print("MDT SDK Command Testing")
        print("======================")
        
        # Discover devices via SDK
        sdk_devices = self.test_device_discovery()
        
        if not sdk_devices:
            print("No devices found via SDK. Exiting.")
            return
        
        # Test each device
        all_results = []
        for serial_no, model in sdk_devices:
            device_result = self.test_device_fully(serial_no, model)
            all_results.append(device_result)
            
            # Brief pause between devices
            time.sleep(1)
        
        # Save results
        output_file = "mdt_sdk_test_results.json"
        try:
            with open(output_file, "w") as f:
                json.dump(all_results, f, indent=2)
            print(f"\n✓ Results saved to {output_file}")
        except Exception as e:
            print(f"✗ Failed to save results: {e}")
        
        # Print summary
        self.print_summary(all_results)
        
        return all_results
    
    def print_summary(self, results):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        
        for result in results:
            model = result.get("model", "Unknown")
            serial = result.get("serial_no", "Unknown")
            status = result.get("status", "Unknown")
            
            print(f"\nDevice: {model} (SN: {serial})")
            print(f"Status: {status}")
            
            if "voltage_functions" in result:
                volt_funcs = result["voltage_functions"]
                working_axes = []
                for key in volt_funcs:
                    if "axis" in key and "error" not in str(volt_funcs[key]):
                        working_axes.append(key.upper())
                
                print(f"Working axes: {', '.join(working_axes) if working_axes else 'None detected'}")
            
            print("-" * 40)

def main():
    """Main test execution"""
    try:
        tester = MDTTester()
        tester.run_full_test()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()