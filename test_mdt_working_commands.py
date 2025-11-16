#!/usr/bin/env python
"""
MDT Device Command Analysis and Working Commands Test

Based on the command discovery, we found key differences between MDT models:

MDT693A (COM10) - 3-channel, older firmware:
- Different protocol: Echoes commands back with '!' terminators
- Basic responses but different format than 693B/694B

MDT693B/694B (COM9/7/13) - Newer firmware:
- Standard protocol with '>' prompt
- Full help system via '?' command
- Proper command definitions in help text

DISCOVERED WORKING COMMANDS:
=============================

Common to all models:
- ID?       → Device identification
- serial?   → Serial number  
- ?         → Help/command list
-- XMAX?/XMIN? → Voltage limits (device reports 150.50V max; software enforces 150.0V)

For MDT693B/694B (from help output):
- XVOLTAGE?  → Get X-axis voltage
- XVOLTAGE=  → Set X-axis voltage  
- YVOLTAGE?  → Get Y-axis voltage (693B only)
- YVOLTAGE=  → Set Y-axis voltage (693B only)
- ZVOLTAGE?  → Get Z-axis voltage (693B only)
- ZVOLTAGE=  → Set Z-axis voltage (693B only)
- XYZVOLTAGE? → Get all voltages (693B only)
- XYZVOLTAGE= → Set all voltages (693B only)
- ALLVOLTAGE= → Set all outputs to same voltage (693B only)

This script will test the actual working commands.
"""

import serial
import time
import json
from typing import Dict, List, Optional, Tuple

class MDTCommandTester:
    def __init__(self, port: str, model: str, serial_no: str):
        self.port = port
        self.model = model
        self.serial_no = serial_no
        self.connection = None
        self.working_commands = {}
        
    def connect(self):
        """Connect to device"""
        try:
            self.connection = serial.Serial(
                port=self.port,
                baudrate=115200,
                timeout=2,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            time.sleep(0.5)
            self.connection.reset_input_buffer()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from device"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def send_command(self, command: str, timeout: float = 1.0) -> Optional[str]:
        """Send command and get response"""
        if not self.connection:
            return None
            
        try:
            # Clear buffers
            self.connection.reset_input_buffer()
            
            # Send command
            cmd_bytes = command.encode('ascii') + b'\r\n'
            self.connection.write(cmd_bytes)
            self.connection.flush()
            
            # Get response
            time.sleep(0.1)
            
            response = b""
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if self.connection.in_waiting > 0:
                    chunk = self.connection.read(self.connection.in_waiting)
                    response += chunk
                    
                    # Check for completion markers
                    if b'>' in response or b'!' in response:
                        break
                        
                time.sleep(0.05)
            
            if response:
                return response.decode('ascii', errors='ignore').strip()
            return None
            
        except Exception as e:
            print(f"Command error: {e}")
            return None
    
    def test_identification_commands(self):
        """Test device identification"""
        print(f"\n--- Testing Identification ---")
        
        commands = {
            "device_info": "ID?",
            "serial_number": "serial?", 
            "help": "?"
        }
        
        results = {}
        
        for name, cmd in commands.items():
            print(f"  {cmd}")
            response = self.send_command(cmd)
            if response:
                # Clean up response for display
                clean_response = response.replace('\r', ' ').replace('\n', ' ')
                if len(clean_response) > 100:
                    clean_response = clean_response[:100] + "..."
                print(f"    ✓ {clean_response}")
                results[name] = response
            else:
                print(f"    ✗ No response")
        
        return results
    
    def test_voltage_commands(self):
        """Test voltage control commands based on device model"""
        print(f"\n--- Testing Voltage Commands ---")
        
        results = {}
        
        # Determine axes based on model
        if "694" in self.model:  # 1-channel
            axes = ["X"]
        else:  # 693A/B - 3-channel  
            axes = ["X", "Y", "Z"]
        
        # Test individual axis commands
        for axis in axes:
            print(f"  {axis}-Axis:")
            axis_results = {}
            
            # Get current voltage
            get_cmd = f"{axis}VOLTAGE?"
            print(f"    {get_cmd}")
            response = self.send_command(get_cmd)
            if response and "CMD_NOT_DEFINED" not in response:
                voltage_value = self._extract_number(response)
                print(f"      ✓ Current: {voltage_value}V")
                axis_results["get_voltage"] = voltage_value
            else:
                print(f"      ✗ Failed")
                
            # Get min/max limits
            for limit_type in ["MIN", "MAX"]:
                limit_cmd = f"{axis}{limit_type}?"
                print(f"    {limit_cmd}")
                response = self.send_command(limit_cmd)
                if response and "CMD_NOT_DEFINED" not in response:
                    limit_value = self._extract_number(response)
                    print(f"      ✓ {limit_type}: {limit_value}V")
                    axis_results[f"{limit_type.lower()}_limit"] = limit_value
                else:
                    print(f"      ✗ Failed")
            
            results[f"{axis.lower()}_axis"] = axis_results
        
        # Test multi-axis commands (693B only)
        if "693B" in self.model:
            print(f"  Multi-Axis:")
            
            # Get all voltages
            get_all_cmd = "XYZVOLTAGE?"
            print(f"    {get_all_cmd}")
            response = self.send_command(get_all_cmd)
            if response and "CMD_NOT_DEFINED" not in response:
                print(f"      ✓ All voltages: {response}")
                results["xyz_voltages"] = response
            else:
                print(f"      ✗ Failed")
        
        return results
    
    def test_safe_voltage_set(self):
        """Test setting voltage safely (low value)"""
        print(f"\n--- Testing Safe Voltage Setting ---")
        
        results = {}
        
        # Test setting X-axis to 1V (safe low value)
        test_voltage = 1.0
        
        # Get current value first
        current_response = self.send_command("XVOLTAGE?")
        if current_response:
            current_voltage = self._extract_number(current_response)
            print(f"  Current X voltage: {current_voltage}V")
            
            # Set new voltage
            set_cmd = f"XVOLTAGE={test_voltage}"
            print(f"  Setting: {set_cmd}")
            response = self.send_command(set_cmd, timeout=2.0)
            
            time.sleep(0.5)  # Allow time for change
            
            # Verify the change
            verify_response = self.send_command("XVOLTAGE?")
            if verify_response:
                new_voltage = self._extract_number(verify_response)
                print(f"  New X voltage: {new_voltage}V")
                
                if abs(new_voltage - test_voltage) < 0.1:
                    print(f"  ✓ Voltage set successfully!")
                    results["set_test"] = True
                else:
                    print(f"  ⚠ Voltage not set as expected")
                    results["set_test"] = False
                
                # Restore original voltage
                restore_cmd = f"XVOLTAGE={current_voltage}"
                print(f"  Restoring: {restore_cmd}")
                self.send_command(restore_cmd)
                
            results["test_voltage"] = test_voltage
            results["original_voltage"] = current_voltage
        
        return results
        
    def _extract_number(self, response: str) -> Optional[float]:
        """Extract numeric value from response"""
        if not response:
            return None
            
        # Remove control characters and extra text
        clean = response.replace('>', '').replace('!', '').replace('\r', '').replace('\n', '').strip()
        
        # Try to extract number
        import re
        numbers = re.findall(r'[-+]?\d*\.?\d+', clean)
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                pass
        return None
    
    def run_comprehensive_test(self):
        """Run all command tests"""
        print(f"\n{'='*60}")
        print(f"TESTING: {self.model} on {self.port}")
        print(f"Serial: {self.serial_no}")
        print(f"{'='*60}")
        
        if not self.connect():
            return {"status": "connection_failed"}
        
        try:
            results = {
                "port": self.port,
                "model": self.model,
                "serial_no": self.serial_no,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "testing"
            }
            
            # Test identification
            results["identification"] = self.test_identification_commands()
            
            # Test voltage queries  
            results["voltage_queries"] = self.test_voltage_commands()
            
            # Test voltage setting (if supported)
            if "693B" in self.model or "694B" in self.model:
                results["voltage_setting"] = self.test_safe_voltage_set()
            
            results["status"] = "complete"
            
        except KeyboardInterrupt:
            print("\n⚠ Test interrupted")
            results["status"] = "interrupted"
        except Exception as e:
            print(f"\n✗ Test error: {e}")
            results["status"] = f"error: {e}"
        finally:
            self.disconnect()
        
        return results

def load_devices():
    """Load device list"""
    try:
        with open("mdt_devices.json", "r") as f:
            devices = json.load(f)
        return {d["Device"]: d for d in devices if "MDT" in d.get("Model", "")}
    except Exception as e:
        print(f"Failed to load devices: {e}")
        return {}

def main():
    """Main test execution"""
    print("MDT Working Commands Test")
    print("=" * 30)
    
    devices = load_devices()
    
    if not devices:
        print("No devices found")
        return
    
    all_results = []
    
    for port, device_info in devices.items():
        tester = MDTCommandTester(
            port=port,
            model=device_info.get("Model", "Unknown"),
            serial_no=device_info.get("SerialNumber", "")
        )
        
        result = tester.run_comprehensive_test()
        all_results.append(result)
        
        time.sleep(1)
    
    # Save results
    output_file = "mdt_working_commands_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n✓ Results saved to {output_file}")
    
    # Print summary
    print(f"\n{'='*60}")
    print("COMMAND SUMMARY")
    print(f"{'='*60}")
    
    for result in all_results:
        model = result.get("model", "Unknown")
        port = result.get("port", "Unknown")
        status = result.get("status", "Unknown")
        
        print(f"\n{model} ({port}): {status}")
        
        if "identification" in result:
            print(f"  ✓ Device identification working")
            
        if "voltage_queries" in result:
            axes = [k for k in result["voltage_queries"].keys() if "axis" in k]
            print(f"  ✓ Voltage queries: {len(axes)} axes")
            
        if "voltage_setting" in result:
            if result["voltage_setting"].get("set_test"):
                print(f"  ✓ Voltage setting confirmed working")
            else:
                print(f"  ⚠ Voltage setting needs verification")

if __name__ == "__main__":
    main()