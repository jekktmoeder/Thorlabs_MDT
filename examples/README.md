# Examples

This directory contains example scripts demonstrating various features of the MDT controller library.

---

## Quick Start

All examples can be run directly from the `examples/` directory:

```powershell
# From the repository root
cd examples

# Run an example
python basic_control.py
```

**Prerequisites:**
- MDT device connected and powered on
- Dependencies installed: `pip install -r ../requirements.txt`
- Virtual environment activated (recommended)

---

## Available Examples

### 1. `basic_control.py`
**Basic connection and voltage control**

Demonstrates:
- Auto-discovery and connection
- Reading current voltages
- Setting voltage with safety limits
- Checking device status
- Zeroing axes

**Good for:** First-time users, understanding the API basics

```powershell
python basic_control.py
```

---

### 2. `multi_axis.py`
**Multi-axis control (MDT693A/B)**

Demonstrates:
- Individual axis control
- Simultaneous multi-axis setting
- Relative movements
- Creating voltage patterns
- Coordinated axis control

**Good for:** Users with 3-axis devices, coordinated positioning

**Note:** Requires MDT693A or MDT693B (3-axis device)

```powershell
python multi_axis.py
```

---

### 3. `voltage_scanning.py`
**Voltage scanning for measurements**

Demonstrates:
- Built-in scan function
- Manual scanning with custom logic
- Fine scanning (high resolution)
- Data acquisition integration points
- Up/down scan patterns

**Good for:** Experimental measurements, characterization, data collection

```powershell
python voltage_scanning.py
```

---

## Modifying Examples

All examples include clear comments and are designed to be modified for your specific needs:

1. **Copy the example:**
   ```powershell
   Copy-Item basic_control.py my_experiment.py
   ```

2. **Edit for your setup:**
   - Change COM port to match your device
   - Adjust voltage ranges for your experiment
   - Add your measurement code
   - Customize output format

3. **Run your modified script:**
   ```powershell
   python my_experiment.py
   ```

---

## Integration with Lab Equipment

### Data Acquisition Example

```python
from mdt import HighLevelMDTController
import your_daq_library  # Replace with actual library

with HighLevelMDTController() as mdt:
    if mdt.is_connected():
        # Set voltage
        mdt.set_voltage_safe("X", 25.0)
        time.sleep(0.5)  # Settling time
        
        # Acquire measurement
        data = your_daq_library.measure()
        
        # Store results
        results.append({
            'voltage': mdt.controller.get_voltage("X"),
            'measurement': data
        })
```

### Saving Data to CSV

```python
import csv

with open('scan_data.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['step', 'voltage', 'measurement'])
    writer.writeheader()
    
    for data_point in scan_data:
        writer.writerow(data_point)
```

### Plotting Results

```python
import matplotlib.pyplot as plt

voltages = [d['voltage'] for d in scan_data]
measurements = [d['measurement'] for d in scan_data]

plt.plot(voltages, measurements, 'o-')
plt.xlabel('Voltage (V)')
plt.ylabel('Measurement')
plt.title('MDT Voltage Scan Results')
plt.grid(True)
plt.show()
```

---

## Safety Reminders

All examples use `set_voltage_safe()` which respects the 100V default safety limit. To use higher voltages:

```python
# Method 1: Adjust safety limit
mdt.set_safe_max(120.0)
mdt.set_voltage_safe("X", 115.0)

# Method 2: Disable safety (use with caution!)
mdt.disable_safety()
mdt.set_voltage_safe("X", 140.0, force=True)
```

⚠️ **Warning:** Excessive voltage can damage piezo elements. Consult device specifications.

---

## Troubleshooting

### Import Errors

```
ModuleNotFoundError: No module named 'mdt'
```

**Solution:** Run examples from the `examples/` directory, or install package:
```powershell
cd ..
pip install -e .
cd examples
```

### Device Not Found

```
✗ No MDT devices found
```

**Solutions:**
1. Check physical connection and power
2. Run device discovery: `python ../find_MDT_devices.py`
3. Verify COM port in Device Manager (Windows)
4. Try specifying port manually: `HighLevelMDTController(port="COM9")`

### Permission Errors

```
serial.serialutil.SerialException: could not open port 'COM9': PermissionError
```

**Solutions:**
1. Close other programs using the COM port
2. Disconnect and reconnect the device
3. Run as administrator (if necessary)

---

## Additional Resources

- **Main Documentation:** [`../README.md`](../README.md)
- **Quick Start:** [`../QUICKSTART.md`](../QUICKSTART.md)
- **API Reference:** Run `python -c "from mdt import HighLevelMDTController; help(HighLevelMDTController)"`
- **Device Manuals:** [`../docs/manuals/`](../docs/manuals/)

---

## Contributing Examples

Have a useful example? We welcome contributions!

1. Create your example script with clear comments
2. Test thoroughly with hardware
3. Add entry to this README
4. Submit pull request

See [`../CONTRIBUTING.md`](../CONTRIBUTING.md) for guidelines.

---

**Happy Experimenting! 🔬**
