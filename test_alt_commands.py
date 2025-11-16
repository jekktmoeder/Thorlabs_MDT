#!/usr/bin/env python
"""
Test alternative command formats for MDT693A
"""

import serial
import time

def test_alternative_commands():
    print("Testing alternative command formats for MDT693A on COM10\n")
    
    ser = serial.Serial(
        port="COM10",
        baudrate=115200,
        timeout=2.0,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE
    )
    
    time.sleep(0.5)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    # List of command variations to try
    test_commands = [
        "XVOLTAGE?",      # Original
        "XV?",            # Short form
        "X?",             # Ultra short
        "READX",          # Alt syntax
        "XVOLTS?",        # Alt word
        "GETX",           # Get command
        "QX",             # Query X
        "*X?",            # With prefix
    ]
    
    print("Testing query commands:")
    for cmd in test_commands:
        ser.reset_input_buffer()
        cmd_bytes = cmd.encode('ascii') + b'\r\n'
        ser.write(cmd_bytes)
        ser.flush()
        time.sleep(0.3)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            decoded = response.decode('ascii', errors='ignore')
            print(f"  {cmd:20s} -> {repr(decoded):50s} | hex: {response.hex()}")
        else:
            print(f"  {cmd:20s} -> (no response)")
    
    print("\nTesting set + immediate read:")
    # Try setting a value and see what happens
    ser.reset_input_buffer()
    ser.write(b'XVOLTAGE=5.00\r\n')
    ser.flush()
    time.sleep(0.5)
    
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        decoded = response.decode('ascii', errors='ignore')
        print(f"  After set command: {repr(decoded)}")
        print(f"  Hex: {response.hex()}")
    
    # Now try to read
    time.sleep(0.2)
    ser.reset_input_buffer()
    ser.write(b'XVOLTAGE?\r\n')
    ser.flush()
    time.sleep(0.3)
    
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        decoded = response.decode('ascii', errors='ignore')
        print(f"  Query after set: {repr(decoded)}")
        print(f"  Hex: {response.hex()}")
    
    ser.close()

if __name__ == "__main__":
    test_alternative_commands()
