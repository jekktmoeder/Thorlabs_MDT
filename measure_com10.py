"""
Measure timing of MDTController operations against COM10.
Runs a few send/read/set operations and prints durations.
"""
import time
from mdt_controller import MDTController

PORT = 'COM10'
MODEL = 'MDT693A'

def tprint(msg):
    print(msg)


def measure():
    ctrl = MDTController(port=PORT, model=MODEL, timeout=2.0)
    tprint(f"Connecting to {PORT}...")
    t0 = time.time()
    ok = ctrl.connect()
    tprint(f"Connect returned {ok} (took {time.time()-t0:.3f}s)")
    if not ok:
        return

    # ID? timing
    t0 = time.time()
    idr = ctrl.send_command('ID?')
    tprint(f"ID? response (took {time.time()-t0:.3f}s): {repr(idr)[:200]}")

    # XR? timing (3 repeats)
    for i in range(3):
        t0 = time.time()
        r = ctrl.send_command('XR?')
        tprint(f"XR? #{i+1} (took {time.time()-t0:.3f}s): {repr(r)}")

    # Use get_voltage (higher-level) timing
    for i in range(3):
        t0 = time.time()
        v = ctrl.get_voltage('X')
        tprint(f"get_voltage X #{i+1} (took {time.time()-t0:.3f}s): {v}")

    # Measure set_voltage without verification (fast-path)
    cur = ctrl.get_voltage('X')
    if cur is None:
        tprint("Could not read current X voltage; skipping set tests")
    else:
        # set to same value (no change) to avoid moving device much
        t0 = time.time()
        ok = ctrl.set_voltage('X', cur, verify=False)
        tprint(f"set_voltage verify=False (took {time.time()-t0:.3f}s): {ok}")

        # set with verification (will read back)
        t0 = time.time()
        ok = ctrl.set_voltage('X', cur, verify=True)
        tprint(f"set_voltage verify=True (took {time.time()-t0:.3f}s): {ok}")

    ctrl.disconnect()
    tprint("Done")

if __name__ == '__main__':
    measure()
