# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a load cell data reader application originally developed for Windows using Visual Basic .NET (Windows Forms). The project has been successfully ported to Python for cross-platform compatibility, particularly targeting Ubuntu 18.04 with GUI interfaces for reading load cell sensor data via serial communication.

## Repository Structure

```
Read_LoadCell/
├── serialset7/              # Original VB.NET Windows application
│   └── serialset/
│       ├── Form1.vb         # Main application logic
│       └── Form1.Designer.vb # Windows Forms UI
├── python_loadcell/         # Python cross-platform implementation
│   ├── loadcell_protocol.py      # Protocol implementation
│   ├── loadcell_serial.py        # Serial communication manager
│   ├── loadcell_gui.py           # Test/debug GUI (manual)
│   ├── realtime_monitor_improved.py  # Real-time monitoring GUI (30 FPS)
│   ├── test_protocol.py          # Protocol unit tests
│   ├── requirements.txt          # Python dependencies
│   ├── README.md                 # User guide (Korean)
│   ├── INSTALL.md                # Installation guide (Ubuntu)
│   └── run.sh                    # Launch script
└── CLAUDE.md                # This file
```

## Python Implementation (python_loadcell/)

### Quick Start

**Ubuntu 18.04:**
```bash
cd python_loadcell
chmod +x run.sh
./run.sh
```

**Manual Installation:**
```bash
pip install -r requirements.txt
python3 realtime_monitor_improved.py  # Real-time monitoring
python3 loadcell_gui.py              # Test/debug GUI
```

### Application Files

#### 1. loadcell_protocol.py
**Purpose**: Load cell communication protocol implementation

**Key Classes/Functions**:
- `LoadCellProtocol.create_*_command()`: Generate protocol commands
- `LoadCellProtocol.parse_*_response()`: Parse responses
- `LoadCellProtocol.calculate_checksum()`: Checksum calculation

**Important Protocol Details**:
- **Sign Bit Handling**: `data[4] & 0x80` indicates negative weight
  - If bit 7 is set → weight is negative
  - Critical for accurate weight measurement when load is removed
- Resolution table: 15 levels from 0.1g to 5000g
- Weight calculation: `weight = resolution × raw_value × sign`

#### 2. loadcell_serial.py
**Purpose**: Serial communication manager with threading

**Key Features**:
- Asynchronous data reception via background thread
- Buffer management with `clear_rx_buffer()` before each command
- Thread-safe operations with locks
- Automatic port enumeration

**Important**:
- Always clear buffer before sending new command to prevent data mixing
- 115200 baud, 8N1 configuration

#### 3. loadcell_gui.py
**Purpose**: Test/debug GUI for protocol verification

**Measurement Method**:
- ❌ NOT real-time: Manual button click required
- ❌ NOT cumulative: Displays absolute weight from hardware
- ✅ Good for: Protocol testing, TX/RX monitoring, parameter configuration

**Usage**:
1. Click "중량읽기" button to read weight
2. Displays last measured value (snapshot)
3. No automatic updates

#### 4. realtime_monitor_improved.py
**Purpose**: Production-ready real-time weight monitoring

**Measurement Method**:
- ✅ Real-time: 30 FPS continuous measurement
- ✅ Filtered: Moving average filter (configurable)
- ✅ Accurate zero calibration: Software offset management
- ✅ Dual display: Filtered value + raw value

**Key Features**:
```python
# Buffer cleared before each read
self.serial.clear_rx_buffer()
cmd = LoadCellProtocol.create_weight_read_command()
self.serial.send_command(cmd)

# Moving average filter (5 samples)
self.raw_weights.append(self.raw_weight)
self.current_weight = np.mean(self.raw_weights)

# Accurate zero calibration
self.zero_offset += self.current_weight  # Cumulative
```

**Keyboard Controls**:
- `[0]` key: Zero calibration (set current weight to 0g)

**Filter Toggle**: Checkbox to enable/disable noise filtering

## Load Cell Communication Protocol

### Command Structure
```
[Address] [Function Code] [Register] [Data/Constant] [Checksum]
5-9 bytes total
```

### Function Codes
- `0x05`: Read response (requested data)
- `0x06`: Continuous weight updates (auto-sent by sensor)
- `0x63`: Write command

### Key Registers
- `0x05`: ID read (4-byte unique identifier)
- `0x02`: Weight read (status, division, 3-byte weight)
- `0x23`: Parameter read/write
- `0x10`: Address write (1-10)
- `0x06`: Zero set

### Weight Response Format
```
Byte 0: Address
Byte 1: Function (0x05 or 0x06)
Byte 2: Register (0x02)
Byte 3: Status flags
Byte 4: [S][X][X][X][D][D][D][D]
        ↑              ↑
    Sign bit      Division (0-14)
Bytes 6-7: Raw weight (2-byte BCD format)
           Each hex nibble = decimal digit
           Example: 0x0123 = 123 decimal
```

**BCD Weight Parsing**:
```python
# Bytes 6-7 contain weight in BCD
byte6 = data[6]  # Thousands/hundreds
byte7 = data[7]  # Tens/ones

thousands = (byte6 >> 4) & 0x0F
hundreds = byte6 & 0x0F
tens = (byte7 >> 4) & 0x0F
ones = byte7 & 0x0F

raw_weight = (thousands * 1000) + (hundreds * 100) + (tens * 10) + ones

# Check sign bit (bit 7 of data[4])
if data[4] & 0x80:  # Bit 7 set = negative
    weight = -weight
```

### Final Weight Calculation
```python
# After BCD parsing, apply resolution and sign
resolution = RESOLUTION_TABLE[division]
weight = resolution * raw_weight

# Apply sign bit
if data[4] & 0x80:
    weight = -weight
```

### Linear Correction
The load cell sensor requires linear correction after user calibration. Based on 499g calibration data from 8 measurement points:

```python
actual_weight = correction_slope * measured + correction_intercept

# Coefficients (derived from 8-point calibration after 499g calibration):
correction_slope = 0.990527
correction_intercept = -2.990644

# Achieves RMS error of 11.16g across 51g-537g range
```

**Application order:**
1. Zero offset: `zeroed = raw - zero_offset`
2. Linear correction: `corrected = 0.990527 * zeroed + (-2.990644)`
3. User calibration: `final = corrected * calibration_factor`

**Important notes:**
- Negative values are allowed and displayed (supports <20g measurements)
- Sensor is pressure-sensitive: place objects in center for consistent readings
- Different positions (center vs corners) yield different readings

### Status Flags (Byte 3)
- Bit 0: Zero error
- Bit 1: Error
- Bit 2: Overload
- Bit 3: Zero adjusted
- Bit 4: Calibration needed

## Serial Communication

### Configuration
- Baud rate: 115200
- Data bits: 8
- Parity: None
- Stop bits: 1
- Timeout: 1-2 seconds

### Best Practices
1. **Clear buffer before each command**:
   ```python
   self.serial.clear_rx_buffer()
   self.serial.send_command(cmd)
   ```
2. **Thread-safe GUI updates**: Use Qt signals
3. **30 FPS for real-time**: Timer interval = 33ms
4. **Moving average filter**: Reduce noise (5-10 samples)

## Platform Compatibility

### Windows
- COM ports: COM1, COM3, etc.
- No special permissions needed
- Works with same Python code

### Ubuntu 18.04
- Ports: /dev/ttyUSB0, /dev/ttyACM0, etc.
- **Required**: Add user to dialout group
  ```bash
  sudo usermod -a -G dialout $USER
  # Log out and log back in
  ```
- Dependencies: python3-pyqt5, matplotlib, numpy, pyserial

## Weight Measurement Concepts

### How Load Cells Work
Load cells are **absolute weight sensors**:
- Measure total weight on platform at any moment
- Not cumulative (don't "add" weights)
- Return current strain gauge reading

**Example Sequence**:
1. Empty: 0g (after zero calibration)
2. Place 100g: reads 100g
3. Add 200g more: reads 300g (total)
4. Remove 100g: reads 200g
5. Remove all: reads 0g

### Zero Calibration Methods

#### Hardware Zero (VB.NET approach)
```python
# Send zero command to load cell chip
cmd = LoadCellProtocol.create_zero_set_command()
serial.send_command(cmd)
```
- Permanent until power cycle
- Hardware saves offset internally

#### Software Zero (Python real-time monitor)
```python
# Accumulate offset in software
self.zero_offset += self.current_weight
adjusted_weight = raw_weight - self.zero_offset
```
- Flexible, can be reset anytime
- Allows multiple zero adjustments
- Key for real-time applications

## Development Commands

### Testing
```bash
# Run protocol tests
cd python_loadcell
python test_protocol.py
```

All tests should pass before deployment.

### Running Applications
```bash
# Real-time monitoring (recommended)
python3 realtime_monitor_improved.py

# Test/debug GUI
python3 loadcell_gui.py
```

### Serial Port Troubleshooting
```bash
# List ports
ls /dev/ttyUSB* /dev/ttyACM*

# Check permissions
ls -l /dev/ttyUSB0

# View kernel messages
dmesg | grep tty

# Test with screen
screen /dev/ttyUSB0 115200
```

## Common Issues and Solutions

### Issue: Values show + when placing weight, - when removing
**Cause**: Sign bit not being checked
**Solution**: Ensure `data[4] & 0x80` logic is implemented

### Issue: Old data mixed with new responses
**Cause**: RX buffer not cleared
**Solution**: Call `clear_rx_buffer()` before each command

### Issue: Noisy/unstable readings
**Cause**: Electrical noise, vibration
**Solution**: Enable moving average filter (5-10 samples)

### Issue: Zero calibration doesn't work properly
**Cause**: Incorrect offset calculation
**Solution**: Use cumulative offset: `offset += current_weight`

### Issue: Permission denied on Linux
**Cause**: User not in dialout group
**Solution**:
```bash
sudo usermod -a -G dialout $USER
# Log out and log back in
```

## Important Notes for Future Development

1. **Always check sign bit**: Load cells can report negative values
2. **Clear buffer strategy**: Prevents protocol parsing errors
3. **30 FPS is optimal**: Balance between responsiveness and CPU usage
4. **Filter is essential**: Raw sensor data is noisy in industrial environments
5. **Dual display helpful**: Show both filtered and raw for debugging
6. **Software zero preferred**: More flexible for continuous monitoring
7. **Test on target platform**: Ubuntu 18.04 has specific PyQt5 requirements

## Dependencies

**Python packages** (requirements.txt):
```
pyserial>=3.5
PyQt5>=5.15.0
matplotlib>=3.3.0
numpy>=1.19.0
```

**Ubuntu system packages**:
```bash
sudo apt-get install python3 python3-pip python3-pyqt5
```

## Hardware Requirements
- Load cell with serial interface (custom protocol)
- USB-to-serial adapter (CH340, FTDI, CP2102, etc.)
- Test weights for calibration verification
