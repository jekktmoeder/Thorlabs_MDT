# SPDX-License-Identifier: MIT
# MDT package public API
from .controller import MDTController, HighLevelMDTController, discover_mdt_devices as _discover_from_controller

# discovery.py provides a CLI-style scanner (main()). The simple helper
# `discover_mdt_devices()` used by other code lives in controller.py and
# is the canonical programmatic entry-point for reading `mdt_devices.json`.
try:
	# Prefer the programmatic helper from controller module
	discover_mdt_devices = _discover_from_controller
except Exception:
	# Fallback: if controller doesn't expose it, try discovery module
	from .discovery import discover_mdt_devices

__all__ = ["MDTController", "HighLevelMDTController", "discover_mdt_devices"]
