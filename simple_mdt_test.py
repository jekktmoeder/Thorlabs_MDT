#!/usr/bin/env python
"""
Simple working MDT SDK test - using discovered function names
"""

import os
import sys
import struct
import shutil
from ctypes import *

def setup_dll():
    """Copy and setup the appropriate DLL"""
    sdk_path = r"C:\Program Files (x86)\Thorlabs\MDT69XB\Sample\Thorlabs_MDT69XB_PythonSDK"
    is_64bit = struct.calcsize('P') == 8
    dll_suffix = "x64" if is_64bit else "win32"
    
    # Create local DLL directory
    local_dll_dir = ".mdt_dlls"
    os.makedirs(local_dll_dir, exist_ok=True)
    
    # Copy appropriate DLL
    src_dll = os.path.join(sdk_path, f"MDT_COMMAND_LIB_{dll_suffix}.dll")
    dst_dll = os.path.join(local_dll_dir, "MDT_COMMAND_LIB.dll")
    
    if not os.path.exists(dst_dll) or os.path.getmtime(src_dll) > os.path.getmtime(dst_dll):
        shutil.copy2(src_dll, dst_dll)
        print(f"✓ Copied {dll_suffix} DLL")
    
    return dst_dll

def test_device_discovery():
    """Test device enumeration using the correct function names"""
    dll_path = setup_dll()
    
    try:
        dll = cdll.LoadLibrary(dll_path)
        print(f"✓ DLL loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load DLL: {e}")
        return []
    
    # Setup List function (this is what the original SDK uses)
    cmdList = dll.List
    cmdList.restype = c_int
    cmdList.argtypes = [c_char_p, c_int]
    
    try:
        # Call device enumeration
        buf = (c_char * 4096)()
        result = cmdList(buf, c_int(4096))
        
        print(f"cmdList returned: {result}")
        
        if result == 0:
            device_string = buf.value.decode('utf-8')
            print(f"Device string: '{device_string}'")
            
            if device_string:
                # Parse device list (format: serial1,model1,serial2,model2,...)
                parts = device_string.split(',')
                devices = []
                
                if len(parts) >= 2:
                    for i in range(0, len(parts), 2):
                        if i+1 < len(parts):
                            serial = parts[i].strip()
                            model = parts[i+1].strip()
                            devices.append((serial, model))
                            print(f"  Found device: Serial={serial}, Model={model}")
                
                return devices, dll
            else:
                print("No devices found (empty string)")
                return [], dll
        else:
            print(f"cmdList failed with code: {result}")
            return [], dll
            
    except Exception as e:
        print(f"Error during device enumeration: {e}")
        import traceback
        traceback.print_exc()
        return [], dll

def test_device_connection(dll, serial_no, model):
    """Test device connection"""
    print(f"\n--- Testing connection to {model} (SN: {serial_no}) ---")
    
    # Setup Open function
    cmdOpen = dll.Open
    cmdOpen.restype = c_int
    cmdOpen.argtypes = [c_char_p, c_int, c_int]
    
    # Setup Close function  
    cmdClose = dll.Close
    cmdClose.restype = c_int
    cmdClose.argtypes = [c_int]
    
    # Setup IsOpen function
    cmdIsOpen = dll.IsOpen
    cmdIsOpen.restype = c_bool
    cmdIsOpen.argtypes = [c_char_p]
    
    try:
        # Try different baud rates
        baud_rates = [115200, 9600, 57600, 38400]
        handle = None
        
        for baud in baud_rates:
            print(f"  Trying baud rate: {baud}")
            
            serial_c = c_char_p(serial_no.encode('utf-8'))
            result = cmdOpen(serial_c, c_int(baud), c_int(3000))
            
            if result >= 0:  # Positive values often indicate success/handle
                handle = result
                print(f"  ✓ Connected! Handle: {handle}")
                
                # Test IsOpen
                is_open = cmdIsOpen(serial_c)
                print(f"  IsOpen result: {is_open}")
                break
            else:
                print(f"  ✗ Failed with code: {result}")
        
        if handle is not None:
            # Test some basic voltage functions
            test_voltage_functions(dll, handle, model)
            
            # Close connection
            close_result = cmdClose(c_int(handle))
            print(f"  Close result: {close_result}")
        
        return handle
        
    except Exception as e:
        print(f"  Connection error: {e}")
        return None

def test_voltage_functions(dll, handle, model):
    """Test voltage control functions"""
    print(f"  Testing voltage functions...")
    
    try:
        # Setup voltage functions
        cmdGetXAxisVoltage = dll.GetXAxisVoltage
        cmdGetXAxisVoltage.restype = c_int
        cmdGetXAxisVoltage.argtypes = [c_int, POINTER(c_double)]
        
        cmdGetLimitVoltage = dll.GetLimitVoltage
        cmdGetLimitVoltage.restype = c_int
        cmdGetLimitVoltage.argtypes = [c_int, POINTER(c_double)]
        
        # Test limit voltage
        limit_volt = c_double(0.0)
        result = cmdGetLimitVoltage(c_int(handle), byref(limit_volt))
        print(f"  Limit voltage: {limit_volt.value}V (result: {result})")
        
        # Test X-axis voltage
        x_volt = c_double(0.0)
        result = cmdGetXAxisVoltage(c_int(handle), byref(x_volt))
        print(f"  X-axis voltage: {x_volt.value}V (result: {result})")
        
        # Test Y and Z if 3-channel device
        if "693" in model:
            try:
                cmdGetYAxisVoltage = dll.GetYAxisVoltage
                cmdGetYAxisVoltage.restype = c_int
                cmdGetYAxisVoltage.argtypes = [c_int, POINTER(c_double)]
                
                cmdGetZAxisVoltage = dll.GetZAxisVoltage
                cmdGetZAxisVoltage.restype = c_int
                cmdGetZAxisVoltage.argtypes = [c_int, POINTER(c_double)]
                
                y_volt = c_double(0.0)
                result = cmdGetYAxisVoltage(c_int(handle), byref(y_volt))
                print(f"  Y-axis voltage: {y_volt.value}V (result: {result})")
                
                z_volt = c_double(0.0)
                result = cmdGetZAxisVoltage(c_int(handle), byref(z_volt))
                print(f"  Z-axis voltage: {z_volt.value}V (result: {result})")
                
            except AttributeError as e:
                print(f"  Y/Z axis functions not available: {e}")
        
    except Exception as e:
        print(f"  Voltage test error: {e}")

def main():
    """Main test function"""
    print("MDT SDK Command Discovery & Test")
    print("=" * 40)
    
    # 1. Discover devices
    print("1. Discovering devices...")
    devices, dll = test_device_discovery()
    
    if not devices:
        print("No devices found or discovery failed")
        return
    
    print(f"\nFound {len(devices)} device(s)")
    
    # 2. Test each device
    for serial_no, model in devices:
        test_device_connection(dll, serial_no, model)
    
    print("\nTest complete!")

if __name__ == "__main__":
    main()