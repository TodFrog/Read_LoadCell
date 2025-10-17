"""
Serial Communication Manager for Load Cell
Handles serial port operations with threading
"""

import serial
import serial.tools.list_ports
import threading
import time
from loadcell_protocol import LoadCellProtocol


class LoadCellSerial:
    """Manages serial communication with load cell"""

    def __init__(self):
        self.serial_port = None
        self.is_connected = False
        self.rx_buffer = []
        self.rx_lock = threading.Lock()
        self.read_thread = None
        self.running = False

        # Callbacks
        self.on_data_received = None
        self.on_connection_changed = None

    @staticmethod
    def list_ports():
        """
        List available serial ports

        Returns:
            list of tuples (port, description)
        """
        ports = serial.tools.list_ports.comports()
        return [(port.device, port.description) for port in ports]

    def connect(self, port_name, baudrate=115200):
        """
        Connect to serial port

        Args:
            port_name: COM port name (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
            baudrate: Baud rate (default 115200)

        Returns:
            bool: True if connected successfully
        """
        try:
            self.serial_port = serial.Serial(
                port=port_name,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1.0
            )
            self.is_connected = True
            self.running = True

            # Start read thread
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()

            if self.on_connection_changed:
                self.on_connection_changed(True)

            return True

        except Exception as e:
            print(f"Connection error: {e}")
            self.is_connected = False
            if self.on_connection_changed:
                self.on_connection_changed(False)
            return False

    def disconnect(self):
        """Disconnect from serial port"""
        self.running = False

        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2.0)

        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

        self.is_connected = False
        if self.on_connection_changed:
            self.on_connection_changed(False)

    def send_command(self, command):
        """
        Send command to load cell

        Args:
            command: bytes to send

        Returns:
            bool: True if sent successfully
        """
        if not self.is_connected or not self.serial_port:
            return False

        try:
            # Clear RX buffer before sending
            with self.rx_lock:
                self.rx_buffer.clear()

            self.serial_port.write(command)
            return True

        except Exception as e:
            print(f"Send error: {e}")
            return False

    def _read_loop(self):
        """Background thread to read serial data"""
        while self.running and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    # Read available bytes
                    data = self.serial_port.read(self.serial_port.in_waiting)

                    with self.rx_lock:
                        self.rx_buffer.extend(data)

                    # Notify callback
                    if self.on_data_received:
                        self.on_data_received(data)

                time.sleep(0.01)  # Small delay to prevent CPU hogging

            except Exception as e:
                print(f"Read error: {e}")
                break

    def get_rx_buffer(self):
        """
        Get received data buffer

        Returns:
            list of bytes
        """
        with self.rx_lock:
            return self.rx_buffer.copy()

    def clear_rx_buffer(self):
        """Clear received data buffer"""
        with self.rx_lock:
            self.rx_buffer.clear()

    # High-level command methods
    def read_id(self):
        """Send ID read command"""
        cmd = LoadCellProtocol.create_id_read_command()
        return self.send_command(cmd)

    def read_weight(self):
        """Send weight read command"""
        cmd = LoadCellProtocol.create_weight_read_command()
        return self.send_command(cmd)

    def read_parameters(self):
        """Send parameter read command"""
        cmd = LoadCellProtocol.create_param_read_command()
        return self.send_command(cmd)

    def change_address(self, new_address):
        """
        Change load cell address

        Args:
            new_address: New address (1-10)
        """
        if 1 <= new_address <= 10:
            cmd = LoadCellProtocol.create_address_change_command(new_address)
            return self.send_command(cmd)
        return False

    def set_zero(self):
        """Send zero set command"""
        cmd = LoadCellProtocol.create_zero_set_command()
        return self.send_command(cmd)

    def write_parameters(self, max_weight_idx, division_idx, zero_range_idx,
                        down_range_idx, kind_idx):
        """
        Write parameters to load cell

        Args:
            max_weight_idx: Max weight index (0-14)
            division_idx: Division/resolution index (0-14)
            zero_range_idx: Zero range (0-9)
            down_range_idx: Settling zero range (1-10)
            kind_idx: Scale type (0-3)
        """
        cmd = LoadCellProtocol.create_param_write_command(
            max_weight_idx, division_idx, zero_range_idx,
            down_range_idx, kind_idx
        )
        return self.send_command(cmd)
