# MDT Piezo Device Controller System

## Overview

Complete MDT piezo device control system following your existing motor controller architecture patterns. This system provides both low-level and high-level control interfaces for MDT693A/B (3-channel) and MDT694B (1-channel) piezo controllers.

## Device Discovery & Command Mapping

### Discovered Devices
- **COM7**: MDT694B (1-channel X-axis, SN: "0")
- **COM9**: MDT693B (3-channel XYZ, SN: "150226175403") 
- **COM10**: MDT693A (3-channel XYZ, via Prolific adapter)
- **COM13**: MDT694B (1-channel X-axis, SN: "140317-02")

### Working Command Protocol
- **Communication**: 115200 baud, 8N1, CR+LF terminated
- **Response format**: Commands return data followed by '>' prompt (693B/694B) or '!' (693A)
- **Voltage range**: 0-150.0V for all models (software-enforced)

#### Core Commands (All Models)
```
ID?            → Device identification and firmware info
serial?        → Device serial number
?              → Complete help/command list
XVOLTAGE?      → Get X-axis voltage
XVOLTAGE=n     → Set X-axis voltage to n volts
XMIN?/XMAX?    → Get X-axis voltage limits
```

#### 3-Channel Commands (MDT693A/B Only)
```
YVOLTAGE?      → Get Y-axis voltage
YVOLTAGE=n     → Set Y-axis voltage
ZVOLTAGE?      → Get Z-axis voltage  
ZVOLTAGE=n     → Set Z-axis voltage
XYZVOLTAGE?    → Get all three voltages (693B only)
XYZVOLTAGE=    → Set all three voltages (693B only)
```

#### Advanced Commands (693B/694B)
```
ALLVOLTAGE=n   → Set all outputs to same voltage (693B only)
YMIN?/YMAX?    → Y-axis limits (693B only)
ZMIN?/ZMAX?    → Z-axis limits (693B only)
```

## Controller Architecture

### MDTController (Low-Level)
Basic serial communication and command interface:

```python
from mdt_controller import MDTController

# Connect to specific device
controller = MDTController(port="COM9", model="MDT693B")
controller.connect()

# Basic operations
voltage = controller.get_voltage("X")           # Get X voltage
controller.set_voltage("X", 10.5)              # Set X to 10.5V
all_voltages = controller.get_all_voltages()    # Get all axes
controller.disconnect()

# Context manager usage
with MDTController("COM9") as controller:
    info = controller.get_device_info()
    controller.set_voltage("Y", 5.0)
```

### HighLevelMDTController (Recommended)
User-friendly interface with safety features:

```python  
from mdt_controller import HighLevelMDTController

# Auto-discover and connect
with HighLevelMDTController() as mdt:
    # Safe operations with built-in limits
    mdt.set_voltage_safe("X", 25.0)                    # Safe voltage setting
    mdt.move_relative("X", 2.0)                        # Relative movement (+2V)
    mdt.set_all_voltages_safe({"X": 10, "Y": 15, "Z": 20})
    
    # Advanced features  
    mdt.zero_all_axes()                                 # Set all to 0V
    mdt.enable_safety(False)                           # Disable safety limits
    scan_data = mdt.scan_axis("X", 0, 50, 21)         # Voltage scan
    
    # Device status
    status = mdt.get_device_status()
    print(f"Connected: {status['model']} on {status['port']}")
    print(f"Current voltages: {status['current_voltages']}")
```

## Safety Features

### Built-in Safety Limits
- **Conservative limit**: 100V (configurable)
- **Hardware limit**: device reports up to 150.50V, but software enforces 150.0V
- **Validation**: All voltages checked before setting
- **Override**: Use `force=True` to bypass safety

### Error Handling
- Connection validation before operations
- Voltage range checking  
- Axis validation per device model
- Timeout protection on commands
- Graceful disconnection

## Files Created

### Core System
- `find_MDT_devices.py` - Device discovery and enumeration
- `mdt_controller.py` - Main controller classes (low and high level)
- `mdt_devices.json` - Device metadata and configuration

### Testing & Discovery  
- `test_mdt_serial_commands.py` - Command protocol discovery
- `test_mdt_working_commands.py` - Verify working commands
- `test_mdt_controllers.py` - Comprehensive controller testing
- `simple_mdt_test.py` - Basic connection testing

### Results & Documentation
- `mdt_command_discovery_results.json` - Complete command mapping
- `mdt_working_commands_results.json` - Verified working commands
- `README_MDT.md` - This documentation

## Usage Examples

### Quick Start
```python
# Simple voltage control
from mdt_controller import HighLevelMDTController

with HighLevelMDTController() as mdt:
    if mdt.is_connected():
        # Set X-axis to 25V safely
        mdt.set_voltage_safe("X", 25.0)
        
        # Get current status  
        status = mdt.get_device_status()
        print(f"X voltage: {status['current_voltages']['X']}V")
```

### Multi-Axis Control (MDT693A/B)
```python
# Control 3-axis device
with HighLevelMDTController(port="COM9") as mdt:  # MDT693B
    # Set all three axes simultaneously
    voltages = {"X": 20.0, "Y": 25.0, "Z": 30.0}
    mdt.set_all_voltages_safe(voltages)
    
    # Scan X-axis while Y,Z remain constant
    scan_data = mdt.scan_axis("X", 0, 50, 21, step_time=0.2)
    
    # Return to center position
    mdt.set_all_voltages_safe({"X": 75, "Y": 75, "Z": 75})
```

### Laboratory Integration
```python
# Integrate with existing lab control
from mdt_controller import create_mdt_controller

# Auto-discover device
mdt = create_mdt_controller(high_level=True)

if mdt.is_connected():
    # Get device capabilities
    status = mdt.get_device_status()
    axes = status['axes']
    limits = status['voltage_limits']
    
    # Experimental sequence
    for voltage in range(0, 51, 5):  # 0-50V in 5V steps
        for axis in axes:
            mdt.set_voltage_safe(axis, voltage)
            time.sleep(0.1)  # Settling time
            
        # Record data here...
        current_voltages = mdt.controller.get_all_voltages()
        print(f"Set: {voltage}V, Actual: {current_voltages}")
    
    # Return to safe state
    mdt.zero_all_axes()
```

## Architecture Integration

This MDT controller system follows the same patterns as your existing motor controller:

1. **Low-level controller** (`MDTController`) - Direct device communication
2. **High-level controller** (`HighLevelMDTController`) - User-friendly interface with safety
3. **Factory functions** - Auto-discovery and device creation
4. **Context managers** - Automatic connection management
5. **Safety systems** - Built-in limits and validation
6. **Error handling** - Graceful failure and recovery

The interface is designed to be familiar to users of your motor control system while providing the specific functionality needed for piezo voltage control.

## Device-Specific Notes

### MDT693A (COM10) - Legacy Protocol
- Older firmware with different response format
- Echoes commands with '!' terminator  
- Basic voltage control working
- May need special handling for some advanced features

### MDT693B (COM9) - Modern 3-Channel
- Full command set support
- Combined XYZ voltage commands available
- Master scan voltage control
- Complete help system via '?' command

### MDT694B (COM7/13) - Single Channel
- X-axis only control
- Same modern protocol as 693B
- Full safety and limit features
- Ideal for single-axis experiments

## Next Steps

The system is ready for integration into your lab control framework. The controller classes provide the same interface patterns as your existing motor controllers, making integration straightforward.

For GUI development, you can now create `MDTControlGUI.py` using the same patterns as `MotorControlGUI.py`, with the high-level controller providing all the device control capabilities needed.