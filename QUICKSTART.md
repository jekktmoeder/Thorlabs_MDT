# Quick Start — Thorlabs MDT Controllers

This file contains a minimal Quick Start to get the GUI or Python API running.

Prerequisites
- Python 3.10+ (use your project's virtual environment)
- Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the GUI

```powershell
python MDTControlGUI.py
```

Quick Python usage

```python
from mdt import HighLevelMDTController

with HighLevelMDTController() as mdt:
    if mdt.is_connected():
        # Set X-axis to 25 V safely
        mdt.set_voltage_safe("X", 25.0)
        print(mdt.get_device_status()["current_voltages"])
```

Notes
- The project runtime lives under `src/mdt/` and compatibility wrappers at the repository root let you run existing scripts without changing calls.
- Default conservative safety limit is 100 V; device maximum is 150 V (software-enforced).
