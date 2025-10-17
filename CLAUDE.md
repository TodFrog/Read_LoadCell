# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a load cell data reader application originally developed for Windows using Visual Basic .NET (Windows Forms). The project goal is to create a cross-platform version that runs on Ubuntu 18.04 with a GUI interface for reading load cell sensor data via serial communication.

## Current Architecture

### Windows Version (serialset7/)
- **Language**: Visual Basic .NET (.NET Framework 4.7.2)
- **UI Framework**: Windows Forms
- **Main Components**:
  - `Form1.vb`: Main application logic with serial communication handling
  - `Form1.Designer.vb`: Windows Forms UI component definitions
  - Serial communication at 115200 baud, 8N1 configuration

### Load Cell Communication Protocol
The application communicates with load cells using a custom serial protocol:

**Command Structure** (5-9 bytes):
```
[Address] [Function Code] [Register] [Data/Constant] [Checksum]
```

**Key Function Codes**:
- `0x05`: Read command
- `0x63`: Write command

**Key Registers**:
- `0x05`: ID read (returns 4-byte unique identifier)
- `0x02`: Weight read (returns status, division, 3-byte weight)
- `0x23`: Parameter read/write (max weight, resolution, zero range, settling zero range, scale type)
- `0x10`: Address write (1-10)
- `0x06`: Zero set

**Communication Flow**:
1. Device discovery via broadcast (address 0x00)
2. ID reading to identify connected load cells
3. Parameter configuration (resolution, max weight, zero ranges)
4. Continuous weight reading and display

**Data Processing**:
- Weight calculation: `weight = resolution × raw_value`
- Resolution table: 0.1g to 5000g (15 levels)
- Max weight: 5kg to 100kg
- Status flags: normal, error, overload, zero adjusted, calibration needed

## Ubuntu/Linux Version Requirements

### Target Platform
- Ubuntu 18.04 LTS (or compatible Linux distribution)
- Python 3.6+ (recommended for cross-platform GUI development)
- Serial port access via `/dev/ttyUSB*` or `/dev/ttyACM*`

### Recommended Technology Stack
- **Language**: Python 3
- **GUI Framework**: PyQt5 or Tkinter (for Ubuntu compatibility)
- **Serial Communication**: pyserial library
- **Build Tools**: python3-pip, python3-venv

## Development Commands

### For Python-based Linux Implementation

**Setup Development Environment**:
```bash
# Install system dependencies (Ubuntu 18.04)
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
sudo apt-get install python3-pyqt5  # For PyQt5 GUI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install pyserial pyqt5
```

**Run the Application**:
```bash
# After implementation
python3 loadcell_reader.py
```

**Serial Port Permissions**:
```bash
# Add user to dialout group for serial port access
sudo usermod -a -G dialout $USER
# Log out and log back in for changes to take effect

# Or temporarily change permissions
sudo chmod 666 /dev/ttyUSB0
```

**List Available Serial Ports**:
```bash
# Find connected serial devices
ls /dev/ttyUSB* /dev/ttyACM*
dmesg | grep tty
```

### For the Original Windows Version

**Build (requires Visual Studio)**:
- Open `serialset7/serialset.sln` in Visual Studio
- Build → Build Solution (or press F6)
- Output: `serialset7/serialset/bin/Debug/serialset.exe` or `serialset7/serialset/bin/Release/serialset.exe`

**Run**:
- Double-click the `.exe` files in the root directory (loadcell_test.exe, loadcell_v11.exe, loadcell_v20.exe)

## Key Implementation Notes

### Serial Communication
- Baud rate: 115200
- Data bits: 8
- Parity: None
- Stop bits: 1
- Timeout: Configure appropriately for read operations (recommend 1-2 seconds)

### GUI Requirements
The application must display:
1. **Connection Panel**: COM port selection, connect/disconnect buttons
2. **Address Configuration**: Change load cell address (1-10)
3. **ID Display**: 4-byte unique identifier in hexadecimal
4. **Weight Display**: Large, prominent display of current weight with unit (gr)
5. **Parameter Configuration**:
   - Max weight (5-100 kg)
   - Resolution/division (15 levels: 0.0001 to 5.0)
   - Zero range (0-9%)
   - Settling zero range (1-10%)
   - Scale type (4 types: quick, normal, crane, large crane)
6. **Status Indicators**: Normal, Error, Overload, Zero Adjusted, Calibration Needed
7. **Parameter Display**: Current load cell configuration
8. **Data Monitor**: TX/RX data in hexadecimal for debugging

### Critical Functions to Implement
1. Serial port enumeration and connection
2. Command transmission with checksum calculation
3. Response parsing with multi-byte data handling
4. Thread-safe GUI updates (async serial data reception)
5. Parameter encoding/decoding
6. Weight calculation with proper resolution scaling

### Protocol Implementation Details
- All numeric values in commands are in hexadecimal
- Multi-byte values use big-endian byte order
- Checksum: simple sum of all bytes & 0xFF
- Response timeout handling for robust communication
- Support for broadcast (address 0x00) and addressed commands

## Testing

### Manual Testing Checklist
1. Connect load cell to USB serial adapter
2. Verify serial port permissions
3. Test port detection and connection
4. Read load cell ID
5. Read current parameters
6. Test weight reading (apply known weights)
7. Test zero adjustment
8. Test parameter modification
9. Verify TX/RX data display matches expected protocol
10. Test disconnection and reconnection

### Hardware Requirements
- Load cell with serial interface (supporting the custom protocol above)
- USB-to-serial adapter (for USB connection)
- Test weights for calibration verification
