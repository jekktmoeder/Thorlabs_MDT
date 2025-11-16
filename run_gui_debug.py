import faulthandler
import sys
import traceback

faulthandler.enable()

try:
    import MDTControlGUI
    if hasattr(MDTControlGUI, 'main'):
        MDTControlGUI.main()
    else:
        print('MDTControlGUI.main not found')
except Exception:
    traceback.print_exc()
    sys.exit(1)
