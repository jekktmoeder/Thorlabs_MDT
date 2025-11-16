#!/usr/bin/env python
"""
Minimal SDK test to discover function names and basic connectivity
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
    
    if not os.path.exists(src_dll):
        raise RuntimeError(f"DLL not found: {src_dll}")
    
    if not os.path.exists(dst_dll) or os.path.getmtime(src_dll) > os.path.getmtime(dst_dll):
        shutil.copy2(src_dll, dst_dll)
        print(f"✓ Copied {dll_suffix} DLL")
    
    return dst_dll

def test_dll_functions():
    """Test various function names to find what's exported"""
    dll_path = setup_dll()
    
    try:
        dll = cdll.LoadLibrary(dll_path)
        print(f"✓ DLL loaded: {dll_path}")
    except Exception as e:
        print(f"✗ Failed to load DLL: {e}")
        return
    
    # Common function name variations to try
    function_variations = [
        # Device management
        ["ListDevices", "EnumerateDevices", "GetDeviceList", "ScanDevices"],
        ["Open", "OpenDevice", "Connect"],
        ["Close", "CloseDevice", "Disconnect"],
        ["IsOpen", "IsConnected", "CheckConnection"],
        
        # Voltage control  
        ["GetXAxisVoltage", "GetVoltageX", "ReadXVoltage"],
        ["SetXAxisVoltage", "SetVoltageX", "WriteXVoltage"],
        ["GetYAxisVoltage", "GetVoltageY", "ReadYVoltage"],
        ["SetYAxisVoltage", "SetVoltageY", "WriteYVoltage"],
        ["GetZAxisVoltage", "GetVoltageZ", "ReadZVoltage"],
        ["SetZAxisVoltage", "SetVoltageZ", "WriteZVoltage"],
        
        # Limits
        ["GetLimtVoltage", "GetLimitVoltage", "GetMaxVoltage"],
        ["SetLimtVoltage", "SetLimitVoltage", "SetMaxVoltage"],
    ]
    
    found_functions = {}
    
    for category in function_variations:
        found_in_category = []
        for func_name in category:
            try:
                func = getattr(dll, func_name)
                found_in_category.append(func_name)
                print(f"✓ Found function: {func_name}")
            except AttributeError:
                pass  # Function not found
        
        if found_in_category:
            found_functions[category[0]] = found_in_category
        else:
            print(f"✗ No functions found for category: {category[0]}")
    
    print(f"\nSummary: Found {sum(len(v) for v in found_functions.values())} functions")
    return found_functions, dll

def test_basic_connection():
    """Try to use the original Python SDK to understand the issue"""
    sdk_path = r"C:\Program Files (x86)\Thorlabs\MDT69XB\Sample\Thorlabs_MDT69XB_PythonSDK"
    
    if sdk_path not in sys.path:
        sys.path.insert(0, sdk_path)
    
    # Change directory for DLL loading
    original_cwd = os.getcwd()
    
    try:
        os.chdir(sdk_path)
        
        # Try to import the original SDK and see what happens
        print("Testing original SDK import...")
        
        # Read the SDK file to understand the structure
        with open(os.path.join(sdk_path, "MDT_COMMAND_LIB.py"), "r") as f:
            sdk_content = f.read()
        
        print("Original SDK structure analysis:")
        lines = sdk_content.split('\n')
        for i, line in enumerate(lines[:20]):  # First 20 lines
            if 'mdtLib' in line or 'LoadLibrary' in line or 'def ' in line:
                print(f"Line {i+1}: {line.strip()}")
                
    except Exception as e:
        print(f"Error analyzing original SDK: {e}")
    finally:
        os.chdir(original_cwd)

def main():
    print("MDT DLL Function Discovery")
    print("=" * 40)
    
    try:
        print("1. Testing DLL function discovery...")
        found_funcs, dll = test_dll_functions()
        
        print("\n2. Testing original SDK structure...")
        test_basic_connection()
        
        if found_funcs:
            print(f"\n3. Found functions summary:")
            for category, funcs in found_funcs.items():
                print(f"  {category}: {', '.join(funcs)}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()