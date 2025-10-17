# Installation Guide - Ubuntu 18.04

## Quick Start

```bash
# 1. Navigate to the project directory
cd python_loadcell

# 2. Run the installation script
chmod +x run.sh
./run.sh
```

## Manual Installation

### Step 1: Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
sudo apt-get install python3-pyqt5
```

### Step 2: Install Python Dependencies

Option A - Using pip:
```bash
pip3 install -r requirements.txt
```

Option B - Manual installation:
```bash
pip3 install pyserial PyQt5
```

### Step 3: Configure Serial Port Permissions

Add your user to the dialout group:
```bash
sudo usermod -a -G dialout $USER
```

**Important**: Log out and log back in for the changes to take effect.

To verify:
```bash
groups
# Should see 'dialout' in the list
```

Temporary permission (for testing only):
```bash
sudo chmod 666 /dev/ttyUSB0
```

### Step 4: Verify Serial Port

Check if your load cell is detected:
```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

Check kernel messages:
```bash
dmesg | grep tty
```

You should see output like:
```
/dev/ttyUSB0
```

### Step 5: Run the Application

```bash
python3 loadcell_gui.py
```

## Using Virtual Environment (Recommended for Development)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python loadcell_gui.py

# Deactivate when done
deactivate
```

## Troubleshooting

### Issue: "No module named 'PyQt5'"

**Solution 1**: Install system package
```bash
sudo apt-get install python3-pyqt5
```

**Solution 2**: Install via pip
```bash
pip3 install PyQt5
```

### Issue: "No module named 'serial'"

**Solution**:
```bash
pip3 install pyserial
```

### Issue: "Permission denied: '/dev/ttyUSB0'"

**Solution 1**: Add user to dialout group (permanent)
```bash
sudo usermod -a -G dialout $USER
# Log out and log back in
```

**Solution 2**: Temporary permission
```bash
sudo chmod 666 /dev/ttyUSB0
```

**Solution 3**: Run with sudo (not recommended)
```bash
sudo python3 loadcell_gui.py
```

### Issue: "No such file or directory: '/dev/ttyUSB0'"

**Check connection**:
```bash
# List all USB devices
lsusb

# Check serial devices
ls -l /dev/ttyUSB* /dev/ttyACM*

# Check kernel messages
dmesg | tail -20
```

**Possible causes**:
- USB cable not connected
- USB-to-serial adapter not recognized
- Device using different name (try /dev/ttyACM0)

### Issue: GUI doesn't start

**Check X11 display**:
```bash
echo $DISPLAY
# Should show something like :0 or :1
```

**If running over SSH**:
```bash
# Enable X11 forwarding
ssh -X user@host
```

### Issue: No data received from load cell

**Checklist**:
1. Correct COM port selected?
2. Load cell powered on?
3. Correct baud rate (115200)?
4. TX/RX cables connected correctly?
5. Check TX/RX monitor in GUI - is data being sent?

## Hardware Connection

```
Load Cell → USB-to-Serial Adapter → Computer USB Port
```

**Typical USB-to-Serial Adapter Pinout**:
- TX (Transmit) → RX on load cell
- RX (Receive) → TX on load cell
- GND → GND on load cell
- VCC → Power (if needed)

## System Requirements

- **OS**: Ubuntu 18.04 LTS or later
- **Python**: 3.6 or later
- **RAM**: 512MB minimum
- **Disk**: 50MB for application + dependencies
- **USB**: USB 2.0 or later port
- **Hardware**: USB-to-serial adapter (CH340, FTDI, CP2102, etc.)

## Tested Configurations

- Ubuntu 18.04 LTS + Python 3.6
- Ubuntu 20.04 LTS + Python 3.8
- Ubuntu 22.04 LTS + Python 3.10

## Additional Resources

- PyQt5 Documentation: https://www.riverbankcomputing.com/static/Docs/PyQt5/
- pySerial Documentation: https://pyserial.readthedocs.io/
- Ubuntu Serial Port Guide: https://help.ubuntu.com/community/SerialPort
