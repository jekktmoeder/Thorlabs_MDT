"""Test short-form set command variants on MDT693A (COM10).

Sends variants like `XV1`, `XV 1`, `XV=1` for axes X/Y/Z and logs responses.
Writes results to `test_shortform_results.txt`.
"""
import time
from pathlib import Path
import serial

OUT = Path('test_shortform_results.txt')

VARIANTS = ['XV1', 'XV 1', 'XV=1', 'XV1.00', 'XV 1.00', 'XV=1.00']
AXES = ['X', 'Y', 'Z']
TERMS = ['\r', '\r\n']

def send_and_read(ser, s, timeout=0.5):
    ser.reset_input_buffer(); ser.reset_output_buffer()
    ser.write(s.encode('ascii', errors='ignore'))
    ser.flush()
    time.sleep(0.12)
    data = ser.read(512)
    return data

def main(port='COM10', baud=115200):
    out = []
    out.append(f'Starting shortform variants test on {port} @ {baud}\n')
    try:
        ser = serial.Serial(port, baudrate=baud, timeout=0.5)
    except Exception as e:
        out.append('Failed to open serial port: ' + str(e))
        OUT.write_text('\n'.join(out), encoding='utf-8')
        print(out[-1])
        return

    with ser:
        time.sleep(0.15)
        for ax in AXES:
            for v in VARIANTS:
                # replace XV prefix axis letter if variant starts with XV
                cmd = v
                if cmd.upper().startswith('XV'):
                    cmd = cmd.replace('XV', ax+'V')
                for term in TERMS:
                    s = cmd + term
                    data = send_and_read(ser, s)
                    out.append(f'SENT: {s!r}')
                    out.append('RAW_BYTES: ' + data.hex())
                    out.append('ASCII: ' + data.decode('ascii', errors='replace'))
                    out.append('-'*40)

    OUT.write_text('\n'.join(out), encoding='utf-8')
    print('Done. Results written to', OUT)

if __name__ == '__main__':
    main()
