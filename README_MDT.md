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
- **Communication**: 115200 baud, 8N1
- **Response format**: Commands return data followed by '>' prompt (693B/694B), '!' or '*' (693A), or CR/LF
- **Voltage range**: 0-150.0V for all models (software-enforced)
- **Command format**: Controller uses short-form commands for compatibility with all devices

#### Core Commands (All Models)
```
ID?            → Device identification and firmware info
serial?        → Device serial number
?              → Complete help/command list
XR?            → Get X-axis voltage (short-form, with XVOLTAGE? fallback)
XV10.5         → Set X-axis to 10.5V (short-form: XVvalue, no = or space)
XL? / XH?      → Get X-axis min/max voltage limits
XL0 / XH150    → Set X-axis min/max voltage limits
```

#### 3-Channel Commands (MDT693A/B Only)
```
YR? / ZR?      → Get Y/Z-axis voltage (short-form)
YV25 / ZV50    → Set Y/Z-axis voltage (short-form)
YL? / YH?      → Y-axis limits (693B only)
ZL? / ZH?      → Z-axis limits (693B only)
XYZVOLTAGE?    → Get all three voltages (693B only, combined query)
```

**Note**: Controller implements short-form commands (e.g., `XV10`) for maximum compatibility with legacy devices. Long-form commands (e.g., `XVOLTAGE=10`) are supported as fallback but not primarily used.

## Controller Architecture

### MDTController (Low-Level)
Basic serial communication and command interface:

```python
from mdt import MDTController

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
from mdt import HighLevelMDTController

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

## Project Structure

### Core Package (`src/mdt/`)
- `controller.py` - Main controller classes (MDTController and HighLevelMDTController)
- `gui.py` - PyQt5 GUI for multi-device control
- `discovery.py` - Device discovery and COM port enumeration
- `utils.py` - Utility functions
- `MDT_COMMAND_LIB.py` / `MDT_COMMAND_LIB_LOCAL.py` - SDK wrapper modules
- `__init__.py` - Package API exports

### Compatibility Wrappers (Repository Root)
- `MDTControlGUI.py` - GUI launcher (thin wrapper for backwards compatibility)
- `find_MDT_devices.py` - Device discovery script (wrapper)
- `connect_mdt.py` - Connection utilities (wrapper)

### Configuration & Data
- `mdt_devices.json` - Discovered device metadata
- `.mdt_dlls/` - Vendor DLLs and LabVIEW library files
- `requirements.txt` - Python dependencies (pyserial, PyQt5)

### Documentation
- `README.md` - Main documentation with quick start
- `README_MDT.md` - This detailed technical documentation
- `MDT693A-Manual.pdf` - Device manual

## Usage Examples

### Quick Start
```python
# Simple voltage control
from mdt import HighLevelMDTController

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
from mdt import create_mdt_controller

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
- Echoes commands (often returns command as acknowledgement instead of numeric value)
- Uses '!', '*', or CR/LF terminators
- Controller applies relaxed verification (±1.0V tolerance) and accepts echo as acknowledgement
- Special handling in code: attempts to disable echo on connect, treats echo response as success

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

## PyQt5 GUI

A complete multi-device GUI is implemented in `src/mdt/gui.py` and can be launched via `MDTControlGUI.py`:

**Features:**
- Auto-discovery and connection to all available MDT devices
- Per-device tabs for independent control
- Per-axis sliders and spinboxes (synchronized)
- Safety toggle with configurable limits (default 100V, device max 150V)
- Quick-set buttons (Zero, Max, Mid)
- Live voltage readback
- Connection status indicators

**Usage:**
```bash
python MDTControlGUI.py
```

The GUI initializes control values from current device state on connect, preventing unintended voltage jumps.

## Integration & Next Steps

The system is ready for integration into lab control frameworks. The controller classes provide consistent interface patterns for programmatic control, while the GUI offers interactive operation. Both low-level (`MDTController`) and high-level (`HighLevelMDTController`) APIs are available depending on whether you need direct serial control or safety-wrapped operations.