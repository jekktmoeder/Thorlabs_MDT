# Python environment & requirements (Windows PowerShell)

This document explains how to create a Python virtual environment and install the project's Python dependencies on Windows using PowerShell. The project expects Python 3.10+ (3.10 used for development).

1) Verify your Python installation

```powershell
python --version
# or, if multiple Python installs exist:
py -3 --version
```

2) Create a virtual environment (recommended name: `.venv`)

```powershell
python -m venv .venv
```

3) Activate the virtual environment (PowerShell)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
.\.venv\Scripts\Activate.ps1
# Your prompt should show '(.venv)' when active
```

Note: If your system prevents script execution, the `Set-ExecutionPolicy` line above sets a process-local relaxed policy just for this shell session.

4) Upgrade tooling and install requirements

```powershell
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Note: Active COM port probing (the `find_MDT_devices.py` convenience wrapper) requires `pyserial` to be installed. The `requirements.txt` provided includes `pyserial`, but if you install dependencies manually ensure `pyserial` is present for device probing to work.

5) (Optional) Install the package in editable mode for local development

```powershell
pip install -e .
```

6) Quick verification

```powershell
python -c "import serial, PyQt5; print('pyserial and PyQt5 imports OK')"
```

7) Run the GUI (once dependencies are installed)

```powershell
python MDTControlGUI.py
```

Conda alternative (if you prefer conda):

```powershell
conda create -n mdt python=3.10
conda activate mdt
pip install -r requirements.txt
```

Troubleshooting notes
- If `PyQt5` installation via `pip` fails on Windows, try a specific version or use conda-forge:

```powershell
pip install PyQt5==5.15.11
# or with conda
conda install -c conda-forge pyqt
```

- If `pip install -r requirements.txt` fails due to network or wheel issues, re-run the command or install the problem package manually and check the error for guidance.

Best practices
- Keep the virtual environment out of version control: ensure `.venv/` is listed in `.gitignore`.
- Keep `requirements.txt` at the repository root so tooling and CI can find it easily.
- If you frequently rebuild environments, consider adding a `pyproject.toml` and `pip-tools` workflow or a `dev-requirements.txt` for developer-only tools.

If you want, I can also:
- Add this file to the repository (done).
- Add a short entry into `docs/index.md` linking to this file and the manuals.
- Create a `pyproject.toml` or `setup.cfg` skeleton to support `pip install -e .` more formally.
