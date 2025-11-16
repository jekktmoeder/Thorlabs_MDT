#!/usr/bin/env python
"""
Direct MDT Device Command Discovery via COM Port Communication

This script connects to each MDT device via serial communication
and tests common command protocols to discover the actual command syntax.

Based on your devices:
- COM7: MDT694B (1-channel X-axis, SN: "0")
- COM9: MDT693B (3-channel XYZ, SN: "150226175403") 
- COM10: MDT693A (3-channel XYZ, via Prolific adapter)
- COM13: MDT694B (1-channel X-axis, SN: "140317-02")
"""

import serial
import time
import json
import sys
from typing import Dict, List, Optional, Any

class MDTSerialTester:
    def __init__(self, port: str, device_info: Dict):
        self.port = port
        self.device_info = device_info
        self.model = device_info.get("Model", "Unknown")
        self.serial_no = device_info.get("SerialNumber", "")
        self.connection = None
        self.results = {
            "port": port,
            "model": self.model, 
            "serial_no": self.serial_no,
            "connection_status": "not_tested",
            "successful_commands": [],
            "failed_commands": [],
            "discoveries": {}
        }
    
    def connect(self, baud_rate=115200, timeout=2):
        """Attempt to connect to the device"""
        try:
            print(f"\n=== Connecting to {self.model} on {self.port} ===")
            print(f"Serial: {self.serial_no}, Baud: {baud_rate}")
            
            self.connection = serial.Serial(
                port=self.port,
                baudrate=baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=timeout,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            # Give device time to initialize
            time.sleep(0.5)
            
            # Clear any existing data in buffer
            self.connection.reset_input_buffer()
            self.connection.reset_output_buffer()
            
            print(f"✓ Connected to {self.port}")
            self.results["connection_status"] = "connected"
            self.results["baud_rate"] = baud_rate
            return True
            
        except Exception as e:
            print(f"✗ Failed to connect to {self.port}: {e}")
            self.results["connection_status"] = f"failed: {e}"
            return False
    
    def send_command(self, command: str, expect_response=True, response_timeout=1) -> Optional[str]:
        """Send a command and return the response"""
        if not self.connection:
            return None
        
        try:
            # Clear buffers
            self.connection.reset_input_buffer()
            
            # Send command
            cmd_bytes = command.encode('ascii') + b'\r\n'
            self.connection.write(cmd_bytes)
            self.connection.flush()
            
            if not expect_response:
                time.sleep(0.1)
                return "OK"
            
            # Wait for response
            time.sleep(0.1)
            
            response = b""
            start_time = time.time()
            
            while time.time() - start_time < response_timeout:
                if self.connection.in_waiting > 0:
                    chunk = self.connection.read(self.connection.in_waiting)
                    response += chunk
                    
                    # Check if response looks complete
                    if b'\r' in response or b'\n' in response:
                        break
                    
                time.sleep(0.05)
            
            if response:
                decoded = response.decode('ascii', errors='ignore').strip()
                return decoded
            else:
                return None
                
        except Exception as e:
            print(f"Error sending command '{command}': {e}")
            return None
    
    def test_identification_commands(self):
        """Test common device identification commands"""
        print(f"\n--- Testing Identification Commands ---")
        
        identification_commands = [
            # Standard SCPI commands
            "*IDN?", 
            "ID?",
            "VER?",
            "VERSION?",
            
            # Thorlabs specific
            "info?",
            "model?",
            "serial?",
            
            # Generic queries
            "?",
            "help",
            "HELP?",
            "status?",
            "STATUS?",
        ]
        
        working_commands = []
        
        for cmd in identification_commands:
            print(f"  Testing: {cmd}")
            response = self.send_command(cmd)
            
            if response and len(response.strip()) > 0:
                print(f"    ✓ Response: '{response}'")
                working_commands.append({"command": cmd, "response": response})
                self.results["successful_commands"].append(cmd)
            else:
                print(f"    ✗ No response")
                self.results["failed_commands"].append(cmd)
        
        self.results["discoveries"]["identification"] = working_commands
        return working_commands
    
    def test_voltage_commands(self):
        """Test voltage control commands"""
        print(f"\n--- Testing Voltage Commands ---")
        
        # Determine axes based on model
        if "694" in self.model:  # 1-channel
            axes = ["X"]
        else:  # 693A/B - 3-channel
            axes = ["X", "Y", "Z"]
        
        voltage_commands = []
        working_commands = []
        
        # Generate test commands for each axis
        for axis in axes:
            voltage_commands.extend([
                # Get voltage commands
                f"{axis}V?", f"{axis.lower()}v?", f"V{axis}?", f"v{axis}?",
                f"GET {axis}", f"get {axis}", f"{axis} GET", f"{axis} get",
                f"VOLT {axis}?", f"volt {axis}?",
                f"VOLTAGE {axis}?", f"voltage {axis}?",
                
                # Set voltage commands (using safe low value)
                f"{axis}V 1", f"{axis.lower()}v 1", f"V{axis} 1", f"v{axis} 1", 
                f"SET {axis} 1", f"set {axis} 1", f"{axis} SET 1", f"{axis} set 1",
                f"VOLT {axis} 1", f"volt {axis} 1",
                f"VOLTAGE {axis} 1", f"voltage {axis} 1",
                
                # Query limits
                f"{axis}MAX?", f"{axis.lower()}max?", f"MAX {axis}?", f"max {axis}?",
                f"{axis}MIN?", f"{axis.lower()}min?", f"MIN {axis}?", f"min {axis}?",
            ])
        
        # General voltage commands
        voltage_commands.extend([
            "VOLT?", "volt?", "V?", "v?",
            "VOLTAGE?", "voltage?", 
            "ALL?", "all?",
            "LIMIT?", "limit?", "MAX?", "max?", "MIN?", "min?",
            "RANGE?", "range?",
        ])
        
        for cmd in voltage_commands:
            print(f"  Testing: {cmd}")
            response = self.send_command(cmd)
            
            if response and len(response.strip()) > 0:
                print(f"    ✓ Response: '{response}'")
                working_commands.append({"command": cmd, "response": response})
                self.results["successful_commands"].append(cmd)
            else:
                self.results["failed_commands"].append(cmd)
        
        self.results["discoveries"]["voltage_control"] = working_commands
        return working_commands
    
    def test_scan_commands(self):
        """Test scanning/sweep commands"""
        print(f"\n--- Testing Scan/Sweep Commands ---")
        
        scan_commands = [
            # Enable/disable scanning
            "SCAN?", "scan?", "SWEEP?", "sweep?",
            "SCAN ON", "scan on", "SCAN OFF", "scan off",
            "SWEEP ON", "sweep on", "SWEEP OFF", "sweep off",
            "ENABLE?", "enable?", "DISABLE?", "disable?",
            
            # Scan parameters
            "SCANVOLT?", "scanvolt?", "SCANV?", "scanv?",
            "SWEEPVOLT?", "sweepvolt?", "SWEEPV?", "sweepv?",
        ]
        
        working_commands = []
        
        for cmd in scan_commands:
            print(f"  Testing: {cmd}")
            response = self.send_command(cmd)
            
            if response and len(response.strip()) > 0:
                print(f"    ✓ Response: '{response}'")
                working_commands.append({"command": cmd, "response": response})
                self.results["successful_commands"].append(cmd)
            else:
                self.results["failed_commands"].append(cmd)
        
        self.results["discoveries"]["scan_control"] = working_commands
        return working_commands
    
    def test_alternative_baud_rates(self):
        """Test different baud rates if initial connection fails"""
        baud_rates = [115200, 9600, 57600, 38400, 19200, 4800]
        
        for baud in baud_rates:
            print(f"\nTrying baud rate: {baud}")
            
            if self.connection:
                self.connection.close()
                time.sleep(0.5)
            
            if self.connect(baud_rate=baud):
                # Quick test with a simple command
                response = self.send_command("*IDN?")
                if response:
                    print(f"✓ Communication established at {baud} baud")
                    return baud
                else:
                    print(f"Connection established but no command response at {baud}")
        
        return None
    
    def disconnect(self):
        """Close the serial connection"""
        if self.connection:
            try:
                self.connection.close()
                print(f"✓ Disconnected from {self.port}")
            except:
                pass
            self.connection = None
    
    def run_full_test(self):
        """Run complete command discovery test"""
        print(f"\n{'='*60}")
        print(f"TESTING: {self.model} on {self.port}")
        print(f"Serial: {self.serial_no}")
        print(f"{'='*60}")
        
        # Try to connect
        if not self.connect():
            print("Trying alternative baud rates...")
            working_baud = self.test_alternative_baud_rates()
            if not working_baud:
                print("✗ Could not establish communication")
                self.results["status"] = "communication_failed"
                return self.results
        
        try:
            # Run command tests
            print("\n🔍 Running command discovery tests...")
            
            id_commands = self.test_identification_commands()
            volt_commands = self.test_voltage_commands()  
            scan_commands = self.test_scan_commands()
            
            # Summary
            total_successful = len(self.results["successful_commands"])
            total_failed = len(self.results["failed_commands"])
            
            print(f"\n--- Test Summary ---")
            print(f"Successful commands: {total_successful}")
            print(f"Failed commands: {total_failed}")
            
            if id_commands:
                print(f"✓ Found {len(id_commands)} identification commands")
            if volt_commands:
                print(f"✓ Found {len(volt_commands)} voltage control commands")
            if scan_commands:
                print(f"✓ Found {len(scan_commands)} scan control commands")
            
            self.results["status"] = "test_complete"
            
        except KeyboardInterrupt:
            print("\n⚠ Test interrupted by user")
            self.results["status"] = "interrupted"
            
        except Exception as e:
            print(f"\n✗ Test error: {e}")
            self.results["status"] = f"error: {e}"
            
        finally:
            self.disconnect()
        
        return self.results

def load_device_list():
    """Load the discovered devices"""
    try:
        with open("mdt_devices.json", "r") as f:
            devices = json.load(f)
        return {dev["Device"]: dev for dev in devices if "MDT" in dev.get("Model", "")}
    except Exception as e:
        print(f"Failed to load device list: {e}")
        return {}

def main():
    """Main test execution"""
    print("MDT Device Command Discovery via Serial Communication")
    print("=" * 60)
    
    # Load device information
    devices = load_device_list()
    
    if not devices:
        print("No MDT devices found. Run find_MDT_devices.py first.")
        return
    
    print(f"Found {len(devices)} MDT devices:")
    for port, info in devices.items():
        print(f"  {port}: {info['Model']} (SN: {info.get('SerialNumber', 'N/A')})")
    
    # Test each device
    all_results = []
    
    for port, device_info in devices.items():
        tester = MDTSerialTester(port, device_info)
        result = tester.run_full_test()
        all_results.append(result)
        
        # Brief pause between devices
        time.sleep(1)
    
    # Save results
    output_file = "mdt_command_discovery_results.json"
    try:
        with open(output_file, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"\n✓ Results saved to {output_file}")
    except Exception as e:
        print(f"✗ Failed to save results: {e}")
    
    # Print overall summary
    print(f"\n{'='*60}")
    print("OVERALL SUMMARY")
    print(f"{'='*60}")
    
    for result in all_results:
        model = result.get("model", "Unknown")
        port = result.get("port", "Unknown")
        status = result.get("status", "Unknown")
        successful = len(result.get("successful_commands", []))
        
        print(f"\n{model} ({port}): {status}")
        print(f"  Working commands: {successful}")
        
        if result.get("discoveries", {}).get("identification"):
            id_responses = result["discoveries"]["identification"]
            print(f"  Device ID responses: {len(id_responses)}")
            for cmd_info in id_responses[:2]:  # Show first 2
                print(f"    {cmd_info['command']} → '{cmd_info['response']}'")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()