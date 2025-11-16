"""Test script for MDT693A commands from the manual (safe defaults).

By default this script only sends queries (no set or limit-changing commands).
To enable set/limit commands use the `--do-sets` flag (manual confirmation recommended).

Outputs:
- `test_mdt693a_manual_results.txt` : raw hex + ascii log
- `test_mdt693a_manual_results_clean.txt` : cleaned ASCII view

Run (safe default):
  python test_mdt693a_manual_commands.py

Run with set attempts (use with caution):
  python test_mdt693a_manual_commands.py --do-sets
"""
import time
import serial
from pathlib import Path

OUT_RAW = Path('test_mdt693a_manual_results.txt')
OUT_CLEAN = Path('test_mdt693a_manual_results_clean.txt')

# Commands derived from manual attachments
QUERY_COMMANDS = [
    # Identification / info
    'I', 'IDN?', 'MODEL?', 'VER?', '*IDN?',
    # Voltage queries (read commands in manual: XR?, YR?, ZR?)
    'XR?', 'YR?', 'ZR?', 'XV?', 'YV?', 'ZV?',
    # Limits queries
    'XL?', 'YL?', 'ZL?', 'XH?', 'YH?', 'ZH?', '%',
    # Echo / misc
    'E', 'E?', 'E=0', 'E=1',
]

# Set commands (disabled by default; use --do-sets to enable)
SET_COMMANDS = [
    'AV=1.00', 'XV=1.00', 'YV=1.00', 'ZV=1.00',
    # limit-setting commands (dangerous unless you know what you're doing)
    'XL=0.00', 'XH=150.00',
]

TERMINATORS = ['\r', '\r\n', '\n']

def send_and_collect(ser, cmd, term, timeout=1.0):
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    to_send = (cmd + term).encode('ascii', errors='ignore')
    ser.write(to_send)
    ser.flush()
    time.sleep(0.12)
    end = time.time() + timeout
    parts = []
    while time.time() < end:
        data = ser.read(256)
        if not data:
            break
        parts.append(data)
    raw = b''.join(parts)
    return raw

def main(port='COM10', baud=115200, do_sets=False):
    out = []
    out.append(f'Starting MDT693A manual commands test: port={port} baud={baud} do_sets={do_sets}\n')
    try:
        ser = serial.Serial(port, baudrate=baud, timeout=0.5)
    except Exception as e:
        out.append('Failed to open serial port: ' + str(e) + '\n')
        OUT_RAW.write_text('\n'.join(out), encoding='utf-8')
        print('Failed to open serial port:', e)
        return

    with ser:
        time.sleep(0.15)
        # First, probe ID/MODEL reliably
        for idcmd in ('MODEL?', 'IDN?', 'I'):
            for term in TERMINATORS:
                raw = send_and_collect(ser, idcmd, term)
                out.append(f'ID CMD: {idcmd!r} TERM: {repr(term)}')
                out.append('RAW_BYTES: ' + raw.hex())
                out.append('ASCII: ' + raw.decode('ascii', errors='replace'))
                out.append('-' * 40)
        # Run queries
        for cmd in QUERY_COMMANDS:
            for term in TERMINATORS:
                raw = send_and_collect(ser, cmd, term)
                out.append(f'Q: {cmd!r} TERM: {repr(term)}')
                out.append('RAW_BYTES: ' + raw.hex())
                out.append('ASCII: ' + raw.decode('ascii', errors='replace'))
                out.append('-' * 40)
        # Optionally run safe set commands
        if do_sets:
            out.append('Running set commands (user enabled)')
            for cmd in SET_COMMANDS:
                for term in TERMINATORS:
                    raw = send_and_collect(ser, cmd, term)
                    out.append(f'SET: {cmd!r} TERM: {repr(term)}')
                    out.append('RAW_BYTES: ' + raw.hex())
                    out.append('ASCII: ' + raw.decode('ascii', errors='replace'))
                    out.append('-' * 40)

    OUT_RAW.write_text('\n'.join(out), encoding='utf-8')
    # write cleaned view (decode ascii with replacement)
    cleaned = '\n'.join(out)
    OUT_CLEAN.write_text(cleaned, encoding='utf-8')
    print('Test completed. Results saved to', OUT_RAW, 'and', OUT_CLEAN)

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description='Test MDT693A manual commands on COM port')
    ap.add_argument('--port', default='COM10')
    ap.add_argument('--baud', type=int, default=115200)
    ap.add_argument('--do-sets', action='store_true', help='Enable set/limit commands (use with caution)')
    args = ap.parse_args()
    main(port=args.port, baud=args.baud, do_sets=args.do_sets)
