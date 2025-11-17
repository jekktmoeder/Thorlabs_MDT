# Quick Start Guide — Thorlabs MDT Controllers

Get up and running with Thorlabs MDT piezo controllers in under 5 minutes.

---

## Prerequisites

- **Python 3.8+** (Check: `python --version`)
- **Windows OS** (primary support)
- **Thorlabs MDT Device** (MDT693A/B or MDT694B)
- **USB/Serial Connection** to your MDT controller

---

## Installation (2 minutes)

### 1. Clone and Setup Environment

```powershell
# Clone the repository
git clone https://github.com/JovanMarkov96/Thorlabs_MDT.git
cd Thorlabs_MDT

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Installation

```powershell
python -c "from mdt import HighLevelMDTController; print('✓ Installation successful')"
```

---

## Launch the GUI (Recommended for First-Time Users)

```powershell
python MDTControlGUI.py
```

**What happens:**
1. GUI opens with device discovery panel
2. Click **"Refresh"** to scan COM ports
3. Select your device from dropdown
4. Click **"Connect"**
5. Use sliders/spinboxes to control voltages
6. Safety limits are enabled by default (100V max)

**GUI Features:**
- Real-time voltage monitoring
- Per-device tabs for multi-controller setups
- Quick-set buttons (0V, 10V, 25V, 50V, 75V, 100V, 150V)
- Safety toggle with visual indicators

---

## Python Quick Examples

### Example 1: Connect and Read Voltage

```python
from mdt import HighLevelMDTController

# Auto-discover and connect to first available device
with HighLevelMDTController() as mdt:
    if mdt.is_connected():
        # Get device status
        status = mdt.get_device_status()
        print(f"Connected to: {status['model']} on {status['port']}")
        print(f"Current voltages: {status['current_voltages']}")
```

### Example 2: Set Voltage Safely

```python
from mdt import HighLevelMDTController

with HighLevelMDTController(port="COM9") as mdt:
    if mdt.is_connected():
        # Set X-axis to 25V (safe mode, 100V limit)
        success = mdt.set_voltage_safe("X", 25.0)
        
        if success:
            print(f"✓ Voltage set to 25V")
            # Read back to verify
            actual = mdt.controller.get_voltage("X")
            print(f"Actual voltage: {actual:.2f}V")
```

### Example 3: Control Multiple Axes (MDT693A/B)

```python
from mdt import HighLevelMDTController

with HighLevelMDTController(port="COM9") as mdt:  # 3-axis device
    if mdt.is_connected():
        # Set all three axes simultaneously
        voltages = {"X": 20.0, "Y": 30.0, "Z": 40.0}
        mdt.set_all_voltages_safe(voltages)
        
        print(f"All axes set: {mdt.controller.get_all_voltages()}")
```

### Example 4: Voltage Sweep for Experiments

```python
from mdt import HighLevelMDTController
import time

with HighLevelMDTController() as mdt:
    if mdt.is_connected():
        # Sweep X-axis from 0 to 50V in 5V steps
        for voltage in range(0, 55, 5):
            mdt.set_voltage_safe("X", float(voltage))
            time.sleep(0.2)  # Settling time
            
            actual = mdt.controller.get_voltage("X")
            print(f"Set: {voltage}V → Actual: {actual:.2f}V")
        
        # Return to zero
        mdt.zero_all_axes()
```

---

## Discover Devices

Find all connected MDT controllers:

```powershell
# Scan and probe all COM ports (default)
python find_MDT_devices.py

# Save results to JSON
python find_MDT_devices.py --json --out my_devices.json

# Passive scan only (no active probing)
python find_MDT_devices.py --no-probe
```

**Active Probing:**
- Default behavior sends safe MDT queries to detect devices
- Works with generic USB-serial adapters (Prolific, FTDI, etc.)
- Identifies model from device responses
- Output saved to `mdt_devices.json` (local-only, not committed)

---

## Common Tasks

### Set Safety Limit

```python
# Increase safety limit to 120V
mdt.set_safe_max(120.0)

# Disable safety entirely (use with caution!)
mdt.disable_safety()
```

### Zero All Axes

```python
mdt.zero_all_axes()  # Set all axes to 0V
```

### Move Relative

```python
# Add 5V to current X-axis voltage
mdt.move_relative("X", +5.0)

# Subtract 2V from current Z-axis voltage
mdt.move_relative("Z", -2.0)
```

### Get Device Information

```python
status = mdt.get_device_status()
print(f"Model: {status['model']}")
print(f"Port: {status['port']}")
print(f"Axes: {status['axes']}")
print(f"Voltage limits: {status['voltage_limits']}")
```

---

## Troubleshooting

### Device Not Found

**Issue:** GUI shows no devices or `discover_mdt_devices()` returns empty list.

**Solutions:**
1. Verify USB connection and device is powered on
2. Check Windows Device Manager for COM port assignment
3. Run discovery with probing: `python find_MDT_devices.py --probe`
4. Install USB-serial drivers if needed (for generic adapters)

### Connection Fails

**Issue:** `mdt.is_connected()` returns `False`.

**Solutions:**
1. Ensure no other software is using the COM port
2. Check baud rate is 115200 (default)
3. Try different COM port if multiple devices connected
4. Verify device is not in local mode (check device front panel)

### Voltage Won't Change

**Issue:** `set_voltage_safe()` returns `False` or voltage doesn't update.

**Solutions:**
1. Check safety limits: default is 100V max
2. Try `mdt.disable_safety()` temporarily
3. Verify axis name is correct ("X", "Y", or "Z")
4. Ensure device supports the axis (MDT694B only has X-axis)

### Import Errors

**Issue:** `ModuleNotFoundError: No module named 'mdt'`

**Solutions:**
1. Activate virtual environment: `.\.venv\Scripts\Activate.ps1`
2. Install requirements: `pip install -r requirements.txt`
3. Verify you're in the project root directory

---

## Next Steps

- **Read the full README**: [`README.md`](./README.md)
- **Explore examples**: See `examples/` directory (if available)
- **Review API documentation**: `help(HighLevelMDTController)`
- **Check device manuals**: [`docs/manuals/`](./docs/manuals/)
- **Optional SDK setup**: [`docs/obtain_dlls.md`](./docs/obtain_dlls.md)

---

## Safety Reminders

⚠️ **Important Safety Guidelines:**

1. **Default Safety Limit**: 100V (configurable to 150V max)
2. **Piezo Damage Risk**: Excessive voltage can damage piezo elements
3. **Verify Settings**: Always check readback values after setting voltage
4. **Gradual Changes**: Avoid sudden large voltage jumps
5. **Know Your Hardware**: Consult device manuals for specifications

---

## Support

- **Issues**: [GitHub Issues](https://github.com/JovanMarkov96/Thorlabs_MDT/issues)
- **Documentation**: [`docs/`](./docs/)
- **Community**: Discussions tab (if enabled)

---

**Happy Controlling! 🔬**
