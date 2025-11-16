"""Set and read short-form commands on MDT693A (COM10).

This script uses short form set commands like `XV1` (sets X axis to 1 V), then
attempts to read back using `XR?` and `XVOLTAGE?`. It logs raw bytes and ASCII
responses to `test_shortform_set_and_read_results.txt`.

Defaults are conservative voltages: [0.0, 1.0, 5.0, 10.0, 50.0].
"""
import time
from pathlib import Path
import serial

OUT = Path('test_shortform_set_and_read_results.txt')

AXES = ['X','Y','Z']
VALUES = [0.0, 1.0, 5.0, 10.0, 50.0]
SET_TERMINATOR = '\r'
READ_COMMANDS = ['{axis}R?', '{axis}VOLTAGE?']

def fmt_short_set(axis, value):
    # prefer integer short form when no fraction, otherwise two decimals
    if abs(value - round(value)) < 1e-9:
        return f"{axis}V{int(round(value))}"
    else:
        return f"{axis}V{value:.2f}"

def send_and_read(ser, s, timeout=0.4):
    ser.reset_input_buffer(); ser.reset_output_buffer()
    ser.write(s.encode('ascii', errors='ignore'))
    ser.flush()
    time.sleep(0.15)
    data = ser.read(1024)
    return data

def main(port='COM10', baud=115200):
    out = []
    out.append(f'Starting shortform set+read test on {port} @ {baud}\n')
    try:
        ser = serial.Serial(port, baudrate=baud, timeout=0.5)
    except Exception as e:
        out.append('Failed to open serial port: ' + str(e))
        OUT.write_text('\n'.join(out), encoding='utf-8')
        print(out[-1])
        return

    with ser:
        time.sleep(0.15)
        for axis in AXES:
            out.append(f'--- Axis {axis} ---')
            for v in VALUES:
                set_cmd = fmt_short_set(axis, v) + SET_TERMINATOR
                data = send_and_read(ser, set_cmd)
                out.append(f'SET {set_cmd!r}')
                out.append('RAW_BYTES: ' + data.hex())
                out.append('ASCII: ' + data.decode('ascii', errors='replace'))
                out.append('WAIT 0.25s')
                out.append('')
                time.sleep(0.25)
                # Attempt reads
                for rfmt in READ_COMMANDS:
                    rcmd = rfmt.format(axis=axis) + SET_TERMINATOR
                    rdata = send_and_read(ser, rcmd)
                    out.append(f'READ {rcmd!r}')
                    out.append('RAW_BYTES: ' + rdata.hex())
                    out.append('ASCII: ' + rdata.decode('ascii', errors='replace'))
                    out.append('-'*30)
                out.append('\n')

    OUT.write_text('\n'.join(out), encoding='utf-8')
    print('Done. Results written to', OUT)

if __name__ == '__main__':
    main()
