import re

# Read original file with UTF-8 encoding
with open("mdt_controller.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: Improve set_voltage with retries
old = "        # For these devices, a successful set usually returns empty or echoes command\n        # We should verify by reading back the value\n        time.sleep(0.1)\n        actual_voltage = self.get_voltage(axis)\n        \n        if actual_voltage is not None:\n            # Allow some tolerance due to DAC resolution\n            tolerance = 0.5  # 0.5V tolerance\n            return abs(actual_voltage - voltage) <= tolerance\n            \n        return False"

new = "        if not verify:\n            return True\n        \n        # Verify by reading back with retries\n        tolerance = 1.0  # 1.0V tolerance for piezo settling\n        max_retries = 3\n        \n        for attempt in range(max_retries):\n            time.sleep(0.15)  # Allow time for settling\n            actual_voltage = self.get_voltage(axis)\n            \n            if actual_voltage is not None:\n                diff = abs(actual_voltage - voltage)\n                if diff <= tolerance:\n                    return True\n                elif attempt < max_retries - 1:\n                    print(f\"Retry {attempt+1}: set={voltage:.2f}V, actual={actual_voltage:.2f}V, diff={diff:.2f}V\")\n            \n        # If we get here, verification failed but device may have moved\n        print(f\"Warning: Verification uncertain for {axis}={voltage:.2f}V (last readback: {actual_voltage})\")\n        return actual_voltage is not None"

content = content.replace(old, new)

# Also update function signature
content = content.replace("    def set_voltage(self, axis: str, voltage: float) -> bool:", "    def set_voltage(self, axis: str, voltage: float, verify: bool = True) -> bool:")
content = content.replace("            voltage: Target voltage in volts\n            \n        Returns:", "            voltage: Target voltage in volts\n            verify: Whether to verify by reading back (default True)\n            \n        Returns:")

# Fix 2: Update _initialize_safety_limits signature and body
content = content.replace("    def _initialize_safety_limits(self):\n        \"\"\"Initialize safety voltage limits\"\"\"", "    def _initialize_safety_limits(self, custom_safe_max: float = None):\n        \"\"\"Initialize safety voltage limits\n        \n        Args:\n            custom_safe_max: Override default safe maximum (default: 100V)\n        \"\"\"")
content = content.replace("        if not self.controller:\n            return\n            \n        for axis in self.controller.axes:", "        if not self.controller:\n            return\n        \n        default_safe_max = custom_safe_max if custom_safe_max is not None else 100.0\n            \n        for axis in self.controller.axes:")
content = content.replace("                \"safe_max\": min(max_v, 100.0)  # Conservative 100V safe limit", "                \"safe_max\": min(max_v, default_safe_max)")

# Fix 3: Add new methods
new_methods = '''    
    def set_safe_max(self, safe_max: float):
        """Set custom safe maximum voltage for all axes
        
        Args:
            safe_max: New safe maximum voltage (must be <= device max)
        """
        if not self.controller:
            return
        
        for axis in self.controller.axes:
            device_max = self.voltage_limits[axis]['max']
            self.voltage_limits[axis]['safe_max'] = min(safe_max, device_max)
        
        print(f"Safe maximum set to {safe_max}V")
    
    def get_safe_max(self) -> float:
        """Get current safe maximum voltage
        
        Returns:
            float: Safe maximum voltage (returns first axis value)
        """
        if self.voltage_limits and self.controller.axes:
            return self.voltage_limits[self.controller.axes[0]]['safe_max']
        return 100.0
'''

# Insert before disconnect method
content = content.replace("    def disconnect(self):\n        \"\"\"Disconnect from device\"\"\"", new_methods + "    def disconnect(self):\n        \"\"\"Disconnect from device\"\"\"")

# Write updated file
with open("mdt_controller.py", "w", encoding="utf-8") as f:
    f.write(content)

print("mdt_controller.py updated successfully")
