#!/bin/bash
# Load Cell Reader launcher script for Ubuntu

echo "Load Cell Reader - Python Version"
echo "=================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install it with: sudo apt-get install python3 python3-pip"
    exit 1
fi

# Check if required packages are installed
echo "Checking dependencies..."

if ! python3 -c "import serial" 2> /dev/null; then
    echo "Warning: pyserial not found"
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

if ! python3 -c "import PyQt5" 2> /dev/null; then
    echo "Warning: PyQt5 not found"
    echo "Installing dependencies..."
    sudo apt-get install python3-pyqt5 || pip3 install PyQt5
fi

# Check serial port permissions
if [ ! -w /dev/ttyUSB0 ] 2> /dev/null && [ ! -w /dev/ttyACM0 ] 2> /dev/null; then
    echo ""
    echo "Warning: You may not have permission to access serial ports"
    echo "Please run: sudo usermod -a -G dialout $USER"
    echo "Then log out and log back in"
    echo ""
    echo "Or temporarily: sudo chmod 666 /dev/ttyUSB0"
    echo ""
fi

# Run the application
echo "Starting Load Cell Reader..."
python3 loadcell_gui.py
