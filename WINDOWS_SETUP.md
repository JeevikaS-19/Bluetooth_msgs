# Windows Setup Guide

PyBluez has known compatibility issues on Windows. Here are solutions:

## Option 1: Use Pre-compiled Wheel (Easiest)

Download and install pre-compiled PyBluez wheel for Windows:

1. Check your Python version:
```bash
python --version
```

2. Download the appropriate `.whl` file from:
   https://www.lfd.uci.edu/~gohlke/pythonlibs/#pybluez

3. Install the wheel:
```bash
pip install PyBluez-0.23-cp311-cp311-win_amd64.whl
```
(Replace with your downloaded filename)

## Option 2: Install Build Tools

If you want to build from source:

1. Install Microsoft C++ Build Tools:
   https://visualstudio.microsoft.com/visual-cpp-build-tools/

2. During installation, select "Desktop development with C++"

3. Then install PyBluez:
```bash
pip install pybluez
```

## Option 3: Use Python 3.7-3.9

PyBluez works better with older Python versions:

1. Install Python 3.9 from python.org
2. Create virtual environment:
```bash
py -3.9 -m venv venv
venv\Scripts\activate
pip install pybluez
```

## Quick Test

After installation, test if it works:

```python
import bluetooth
print("PyBluez installed successfully!")
```

## Alternative: Run on WSL (Linux)

If all else fails, use Windows Subsystem for Linux:

```bash
wsl --install
# After WSL is installed
sudo apt-get update
sudo apt-get install python3 python3-pip libbluetooth-dev
pip3 install pybluez
```

## Troubleshooting

**Error**: "Microsoft Visual C++ 14.0 or greater is required"
- **Solution**: Install Build Tools (Option 2)

**Error**: "bluetooth.exe not found"
- **Solution**: Make sure Bluetooth is enabled in Windows settings

**Error**: "Access denied"
- **Solution**: Run terminal as Administrator
