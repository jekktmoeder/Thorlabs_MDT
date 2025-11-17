#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

"""
Enumerate COM ports on Windows and flag likely Thorlabs MDT693B/694B devices.
Also (optionally) cross-check with the MDT Python SDK if available.

Usage (PowerShell):
  python .\find_mdt_devices.py
"""

import sys
import re
import argparse
import json
import time
from typing import List

# ---- pyserial is required for COM enumeration ----
try:
    from serial.tools import list_ports
except Exception:
    print("ERROR: pyserial is required for device discovery and probing.\nInstall it into your active Python environment with:\n  pip install pyserial\nOr install all project requirements:\n  pip install -r requirements.txt")
    sys.exit(1)

# ---- Try to import MDT SDK wrappers if available (optional) ----
mdt_available = False
mdt_devices = []
try:
    # This import will succeed only if your MDT wrapper can import its DLLs.
    from MDT_COMMAND_LIB import mdtListDevices
    try:
        mdt_devices = mdtListDevices()  # -> [[serialNumber, model], ...]
        mdt_available = True
    except Exception as ex:
        print(f"(Note) MDT SDK present but mdtListDevices() failed: {ex}")
except Exception:
    # Totally fine; we can still enumerate COM ports without SDK.
    pass

# ---- Heuristics for identifying likely MDT devices on USB-Serial ----
MDT_KEYWORDS = [
    "thorlabs",
    "mdt",
    "mdt69",
    "mdt693b",
    "mdt694b",
]

# ---- Active probe defaults (safe, non-destructive commands) ----
ID_COMMANDS = [b'XR?\r', b'ID?\r', b'*IDN?\r', b'XR?\n', b'XR?']
PROBE_BAUD = 115200
PROBE_TIMEOUT = 0.3

try:
    import serial
except Exception:
    serial = None

def is_mdt_candidate(portinfo) -> bool:
    """
    Return True if any known MDT keywords appear in relevant fields.
    """
    fields = [
        str(getattr(portinfo, "manufacturer", "")),
        str(getattr(portinfo, "product", "")),
        str(getattr(portinfo, "description", "")),
        str(getattr(portinfo, "name", "")),
        str(getattr(portinfo, "device", "")),
        str(getattr(portinfo, "hwid", "")),
    ]
    combined = " ".join(f for f in fields if f).lower()
    return any(k in combined for k in MDT_KEYWORDS)

def fmt_vid_pid(p):
    vid = getattr(p, "vid", None)
    pid = getattr(p, "pid", None)
    if vid is None and pid is None:
        # Try to parse from HWID if present e.g. 'USB VID:PID=0403:6001'
        hwid = str(getattr(p, "hwid", ""))
        m = re.search(r"VID:PID=([0-9A-Fa-f]{4}):([0-9A-Fa-f]{4})", hwid)
        if m:
            return f"{m.group(1)}:{m.group(2)}"
        return ""
    if vid is not None and pid is not None:
        return f"{vid:04X}:{pid:04X}"
    return ""

def main():
    parser = argparse.ArgumentParser(description="Enumerate COM ports and optionally filter by vendor/manufacturer.")
    parser.add_argument("--vendors", "-v", help="Comma-separated vendor keywords to filter (case-insensitive). Defaults to 'Thorlabs'", default="Thorlabs")
    parser.add_argument("--json", help="Output results as JSON", action="store_true")
    parser.add_argument("--out", "-o", help="Output JSON file path (default: mdt_devices.json)", default="mdt_devices.json")
    parser.add_argument("--assign", "-a", help="Assign model by rule. Format: key=value. Key can be COM port (e.g. COM10), manufacturer (Prolific), or VID:PID (067B:23A3). Can be repeated.", action="append", default=[])
    # Probe enabled by default for convenience; allow disabling with --no-probe
    parser.add_argument("--probe", dest="probe", action="store_true", help="Actively probe COM ports using MDT-safe serial queries to confirm device identity. (default: enabled)", default=True)
    parser.add_argument("--no-probe", dest="probe", action="store_false", help="Disable active probing (opposite of --probe).")
    parser.add_argument("--probe-only-manufacturer", action="store_true", help="When probing, only probe ports whose manufacturer field contains 'Thorlabs'. By default probing checks all COM ports.")
    args = parser.parse_args()

    vendor_filters: List[str] = [v.strip().lower() for v in args.vendors.split(",") if v.strip()] if args.vendors else ["thorlabs", "prolific"]

    # Parse assignments into lists of matchers
    assigns = []
    for a in args.assign:
        if "=" in a:
            k, v = a.split("=", 1)
            assigns.append((k.strip().lower(), v.strip()))

    print("=== COM Port Scan (Windows) ===")
    ports = list(list_ports.comports())
    if not ports:
        print("No COM ports found.")
        return

    # Build a quick index for cross-reference by serial number (if SDK is available)
    mdt_serials = set()
    mdt_models = {}
    if mdt_available:
        for sn, model in mdt_devices:
            mdt_serials.add(str(sn))
            mdt_models[str(sn)] = model

    rows = []
    for p in ports:
        row = {
            "Device": p.device,
            "Desc": getattr(p, "description", ""),
            "Manufacturer": getattr(p, "manufacturer", ""),
            "Product": getattr(p, "product", ""),
            "SerialNumber": getattr(p, "serial_number", ""),
            "VID:PID": fmt_vid_pid(p),
            "Location": getattr(p, "location", ""),
            "HWID": getattr(p, "hwid", ""),
        }
        row["LikelyMDT"] = "YES" if is_mdt_candidate(p) else ""
        # Cross-ref with MDT SDK serials if available
        sn = row["SerialNumber"]
        if mdt_available and sn and sn in mdt_serials:
            row["MDT_SDK_Model"] = mdt_models.get(sn, "")
        # Determine model
        model = ""
        # Priority 1: SDK reported model
        if "MDT_SDK_Model" in row and row.get("MDT_SDK_Model"):
            model = row.get("MDT_SDK_Model")
        # Priority 2: try to parse from description/product/name
        if not model:
            combined_parse = " ".join([str(row.get(k, "")) for k in ("Desc", "Product")])
            m = re.search(r"MDT[- ]?\d{3,4}[A-Za-z]?", combined_parse, re.IGNORECASE)
            if m:
                model = m.group(0).replace(" ", "")
        # Priority 3: apply assignments provided by user (--assign)
        if not model and assigns:
            combined_fields = " ".join([str(row.get(k, "")) for k in ("Device", "Manufacturer", "VID:PID", "HWID")]).lower()
            for key, val in assigns:
                if key in combined_fields:
                    model = val
                    break
                # allow matching by exact COM port
                if key.upper() == str(row.get("Device", "")).upper():
                    model = val
                    break
        # (No default mapping for generic adapters like Prolific.)
        row["Model"] = model

        # If active probing was requested, perform a short, safe probe on the port.
        if args.probe:
            probe_allowed = True
            if args.probe_only_manufacturer:
                probe_allowed = (str(row.get("Manufacturer", "")).lower().find("thorlabs") != -1)
            if probe_allowed:
                # Perform a safe serial probe; if pyserial is unavailable, skip.
                probe_result = {"ProbeAvailable": False}
                if serial is None:
                    probe_result["error"] = "pyserial not installed"
                else:
                    try:
                        ser = serial.Serial(port=row.get("Device"), baudrate=PROBE_BAUD, timeout=PROBE_TIMEOUT)
                        try:
                            ser.reset_input_buffer()
                            ser.reset_output_buffer()
                        except Exception:
                            pass
                        best_reply = None
                        matched = False
                        for cmd in ID_COMMANDS:
                            try:
                                ser.write(cmd)
                            except Exception:
                                continue
                            # short delay and read
                            try:
                                time.sleep(0.05)
                                raw = ser.read(2048)
                            except Exception:
                                raw = b''
                            try:
                                decoded = raw.decode('ascii', errors='ignore').strip()
                            except Exception:
                                decoded = str(raw)
                            # strip echoed command and prompts
                            try:
                                cmd_text = cmd.decode('ascii', errors='ignore').strip()
                                if cmd_text and decoded.startswith(cmd_text):
                                    decoded = decoded[len(cmd_text):].strip()
                            except Exception:
                                pass
                            decoded = decoded.strip('\r\n >!*')
                            if decoded:
                                best_reply = decoded
                                up = decoded.upper()
                                if 'MDT' in up or 'THOR' in up or re.search(r'69[34]', up):
                                    matched = True
                                    break
                                if re.search(r'-?\d+\.\d+', decoded):
                                    matched = True
                                    break
                        try:
                            ser.close()
                        except Exception:
                            pass
                        probe_result = {"ProbeAvailable": True, "ProbeMatch": bool(matched), "ProbeReply": best_reply}
                    except Exception as e:
                        probe_result = {"ProbeAvailable": False, "error": str(e)}
                # merge probe_result into row
                row.update(probe_result)

        # Collect all rows first; we'll filter for output after probing.
        rows.append(row)

    # Pretty print
    def w(s, n):
        s = "" if s is None else str(s)
        return s if len(s) <= n else s[: n - 1] + "…"

    headers = [
        "Device", "Desc", "Manufacturer", "Product",
        "SerialNumber", "VID:PID", "Location", "LikelyMDT"
    ]
    # Include HWID and SDK_Model as extended columns at the end
    headers_ext = headers + ["MDT_SDK_Model", "HWID"]

    # Compute column widths
    widths = {h: max(len(h), *(len(str(r.get(h, ""))) for r in rows)) for h in headers_ext}
    # Print header
    line = " | ".join(h.ljust(widths[h]) for h in headers_ext)
    print(line)
    print("-" * len(line))
    # Add Model to headers and write output
    headers_ext = headers + ["MDT_SDK_Model", "Model", "HWID"]
    widths = {h: max(len(h), *(len(str(r.get(h, ""))) for r in rows)) for h in headers_ext}

    # If probing was requested, include ports that matched a probe even if
    # their manufacturer didn't match vendor_filters. Otherwise filter by
    # vendor_filters (if provided).
    if args.probe and vendor_filters:
        def include_row(r):
            combined = " ".join([str(r.get(k, "")) for k in ("Manufacturer", "Product", "Desc", "HWID")]).lower()
            if any(v in combined for v in vendor_filters):
                return True
            if r.get('ProbeMatch'):
                return True
            return False
        filtered = [r for r in rows if include_row(r)]
    else:
        if vendor_filters:
            filtered = [r for r in rows if any(v in (" ".join([str(r.get(k, "")) for k in ("Manufacturer", "Product", "Desc", "HWID")])).lower() for v in vendor_filters)]
        else:
            filtered = rows

    if args.json:
        print(json.dumps(filtered, indent=2))
    else:
        # Print header
        line = " | ".join(h.ljust(widths[h]) for h in headers_ext)
        print(line)
        print("-" * len(line))
        for r in filtered:
            print(" | ".join(w(r.get(h, ""), widths[h]).ljust(widths[h]) for h in headers_ext))

    # Always write JSON output file with the rows (including Model)
    try:
        out_path = args.out
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(filtered, fh, indent=2)
        print(f"\nSaved {len(filtered)} entries to JSON: {out_path}")
    except Exception as e:
        print(f"Failed to write JSON output {args.out}: {e}")

    print("\nTips:")
    print(" - 'LikelyMDT' = YES means the port description/manufacturer matched MDT/Thorlabs keywords.")
    print(" - If 'MDT_SDK_Model' appears, your MDT SDK reported a device with matching USB serial.")
    print(" - You can refine matches by adding exact VID:PID or product strings to MDT_KEYWORDS in this script.")
    if not mdt_available:
        print(" - MDT SDK was not imported; that’s fine. To enable cross-check, fix the SDK DLL loading and rerun.")

if __name__ == "__main__":
    main()
