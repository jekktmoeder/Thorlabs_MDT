"""Probe script for MDT693A (COM10) using candidate commands inspired by LabVIEW VI.

This script sends a short list of read and write command variants to the device
and logs raw responses to `probe_mdt693a_results.txt` for inspection.

Safe defaults:
- Port: COM10 (change with --port)
- Baud: 115200
- Writes that change voltage are limited to 1.00 V to avoid risk.
"""
import time
import serial
from pathlib import Path

OUTPATH = Path(__file__).with_name('probe_mdt693a_results.txt')

COMMANDS = [
    # Queries (variants)
    'XVOLTAGE?', 'xvoltage?', 'YVOLTAGE?', 'ZVOLTAGE?',
    '*IDN?', 'IDN?', 'MODEL?', 'VER?',
    # Echo control attempts
    'ECHO=0', 'ECHO OFF', 'ECHO=OFF',
    # Safe set commands (small voltage)
    'XVOLTAGE=1.00', 'XVOLTAGE=1', 'xvoltage=1.00',
]

TERMINATORS = ['\r', '\r\n', '\n']

def send_and_read(ser, text, term, timeout=1.0):
    raw = []
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    to_send = (text + term).encode('ascii', errors='ignore')
    ser.write(to_send)
    ser.flush()
    # short settle
    time.sleep(0.12)
    # read any available data
    end = time.time() + timeout
    while time.time() < end:
        data = ser.read(256)
        if not data:
            break
        raw.append(data)
    return b''.join(raw)

def main(port='COM10', baud=115200):
    out = []
    out.append(f'Probe started: port={port} baud={baud}\n')
    try:
        ser = serial.Serial(port, baudrate=baud, timeout=0.5)
    except Exception as e:
        out.append('Failed to open serial port: ' + str(e) + '\n')
        OUTPATH.write_text('\n'.join(out), encoding='utf-8')
        print('Failed to open serial port:', e)
        return

    with ser:
        # small initial pause
        time.sleep(0.2)
        for cmd in COMMANDS:
            for term in TERMINATORS:
                try:
                    raw = send_and_read(ser, cmd, term)
                except Exception as e:
                    out.append(f'ERROR sending {cmd!r} term={term!r}: {e}')
                    continue
                out.append(f'CMD: {cmd!r} TERM: {repr(term)}')
                out.append('RAW_BYTES: ' + raw.hex())
                try:
                    decoded = raw.decode('ascii', errors='replace')
                except Exception:
                    decoded = str(raw)
                out.append('ASCII: ' + decoded)
                out.append('-' * 40)
                # short pause between commands
                time.sleep(0.08)

    OUTPATH.write_text('\n'.join(out), encoding='utf-8')
    print('Probe completed. Results written to', OUTPATH)

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', default='COM10')
    ap.add_argument('--baud', type=int, default=115200)
    args = ap.parse_args()
    main(port=args.port, baud=args.baud)
