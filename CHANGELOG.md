# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Comprehensive professional documentation (README, QUICKSTART, CONTRIBUTING)
- Enhanced .gitignore with additional patterns
- Professional repository structure

### Changed
- Updated README to professional standard with badges and comprehensive sections
- Improved QUICKSTART with troubleshooting and safety reminders
- Reorganized documentation for better accessibility

---

## [0.1.0] - 2025-11-17

### Added
- Initial release of Thorlabs MDT Controller library
- **Core Features:**
  - Low-level controller (`MDTController`) for direct serial communication
  - High-level controller (`HighLevelMDTController`) with safety features
  - Multi-device PyQt5 GUI (`MDTControlGUI.py`)
  - Automatic device discovery with active probing (`find_MDT_devices.py`)
  - Context manager support for resource management
  - Factory functions for controller instantiation

- **Device Support:**
  - MDT693A (3-channel, legacy protocol with echo handling)
  - MDT693B (3-channel, modern protocol)
  - MDT694B (1-channel)
  - Support for generic USB-serial adapters (Prolific, FTDI)

- **Safety Features:**
  - Configurable voltage limits (default 100V, max 150V)
  - Range validation before operations
  - Readback verification (±1.0V tolerance for legacy devices)
  - Override mechanisms for calibration

- **GUI Features:**
  - Per-device tabs for multi-controller setups
  - Real-time voltage monitoring
  - Per-axis sliders and spinboxes (0.1V resolution)
  - Quick-set buttons (0V to 150V)
  - Safety toggle with visual indicators
  - Connection management panel

- **API Features:**
  - Type hints throughout
  - Comprehensive docstrings
  - Error handling and graceful failures
  - Voltage scanning for experiments
  - Relative movement commands
  - Batch voltage setting for multi-axis devices

- **Documentation:**
  - Complete README with usage examples
  - Quick start guide
  - Device manual PDFs (MDT693A, MDT694B)
  - DLL obtainment instructions
  - License documentation (MIT + Thorlabs EULA)
  - SPDX license identifiers in source files

- **Development:**
  - Project structured as Python package (`src/mdt/`)
  - Backwards-compatible root-level wrappers
  - Virtual environment support
  - Git repository with proper .gitignore
  - MIT License

### Protocol Implementations
- **Short-form commands** for maximum compatibility:
  - `XR?`, `YR?`, `ZR?` - Read voltage
  - `XV10`, `YV20`, `ZV30` - Set voltage
  - `XL?`, `XH?` - Get limits
  - `XL0`, `XH150` - Set limits
  - `ID?` - Device identification
  - `XYZVOLTAGE?` - Combined read (693B only)

- **Legacy device handling**:
  - Echo detection and stripping
  - Multiple terminator support (`>`, `!`, `*`, `\r\n`)
  - Relaxed verification tolerance
  - Automatic echo mode disabling on connect

### Known Issues
- Windows primary platform (Linux/macOS experimental)
- SDK DLLs not included in repository (see docs/obtain_dlls.md)
- Some USB-serial adapters may require additional drivers

---

## Release Notes

### v0.1.0 Highlights

This initial release provides a complete, production-ready system for controlling Thorlabs MDT piezo voltage controllers. Key highlights:

**For Researchers:**
- Easy-to-use GUI for interactive control
- Python API for lab automation
- Safety systems to prevent hardware damage
- Real-time monitoring and feedback

**For Developers:**
- Clean, well-documented API
- Type hints and docstrings throughout
- Extensible architecture
- Professional code structure

**For Lab Environments:**
- Multi-device support (control multiple units)
- Auto-discovery (no manual configuration)
- Legacy hardware support (MDT693A compatibility)
- Generic adapter support (Prolific, FTDI, etc.)

**Testing:**
- Validated with MDT693A, MDT693B, and MDT694B hardware
- Tested on Windows 10/11
- Verified with Prolific and native Thorlabs USB adapters
- Voltage setting accuracy: ±0.1V (modern), ±1.0V (legacy)

---

## Upgrade Guide

### From Pre-Release to v0.1.0

If you were using development versions:

1. **Update imports:**
   ```python
   # Old (may still work via compatibility wrappers)
   from controller import MDTController
   
   # New (recommended)
   from mdt import MDTController, HighLevelMDTController
   ```

2. **Update device discovery:**
   ```python
   # Old
   devices = MDT_COMMAND_LIB.mdtListDevices()
   
   # New
   from mdt import discover_mdt_devices
   devices = discover_mdt_devices()
   ```

3. **Update scripts:**
   - Root-level scripts (`MDTControlGUI.py`, `find_MDT_devices.py`) still work
   - Consider updating to import from `mdt` package directly

---

## Future Roadmap

### Planned Features (v0.2.0)
- [ ] Linux/macOS testing and support
- [ ] Automated tests with hardware mocking
- [ ] Continuous Integration (GitHub Actions)
- [ ] Pre-commit hooks for code quality
- [ ] Additional example scripts
- [ ] Performance optimizations for rapid scanning
- [ ] Configuration file support (YAML/JSON)

### Under Consideration
- [ ] TCP/IP networking for remote control
- [ ] Data logging and CSV export
- [ ] Calibration utility
- [ ] Batch scripting language
- [ ] REST API server mode
- [ ] LabVIEW VI compatibility layer

---

## Links

- **Repository**: https://github.com/JovanMarkov96/Thorlabs_MDT
- **Issues**: https://github.com/JovanMarkov96/Thorlabs_MDT/issues
- **Releases**: https://github.com/JovanMarkov96/Thorlabs_MDT/releases
- **Documentation**: See `docs/` folder
- **License**: MIT (see `docs/licenses/LICENSE`)

---

**Last Updated:** November 17, 2025
