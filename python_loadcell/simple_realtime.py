#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Real-time Weight Monitor
Uses the exact same logic as loadcell_gui.py but continuously at 30 FPS
No filtering, no absolute value, no offset - just raw weight display
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QFont

from loadcell_serial import LoadCellSerial
from loadcell_protocol import LoadCellProtocol


class SimpleRealtimeMonitor(QMainWindow):
    """Simple real-time monitor - exact same logic as loadcell_gui.py"""

    # Signal for thread-safe GUI updates
    data_received_signal = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()

        # Serial connection
        self.serial = LoadCellSerial()
        self.serial.on_data_received = self.on_serial_data

        # Connect signal
        self.data_received_signal.connect(self.update_display)

        # Connection state
        self.is_connected = False

        # Current weight
        self.current_weight = 0.0
        self.raw_weight = 0.0

        # Calibration
        self.zero_offset = 0.0  # Zero point offset (applied before curve correction)

        # Nonlinear correction coefficients (quadratic: actual = a*measured^2 + b*measured + c)
        # Derived from calibration data:
        # - 17g object: measured 17g
        # - 51g object: measured 60.3g
        # - 499g object: measured 403.4g
        # Using 2nd order polynomial fit
        self.correction_a = 0.001261538  # x^2 coefficient
        self.correction_b = 0.715034     # x coefficient
        self.correction_c = 5.158309     # constant offset

        # Initialize UI
        self.init_ui()

        # Timer for periodic weight reading
        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.read_weight)

        # Response tracking to avoid sending too fast
        self.waiting_for_response = False
        self.last_valid_weight = 0.0

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle('단순 실시간 중량 모니터')
        self.setGeometry(100, 100, 600, 400)

        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Connection panel
        conn_layout = QHBoxLayout()

        conn_label = QLabel("통신포트:")
        conn_layout.addWidget(conn_label)

        self.port_combo = QComboBox()
        self.refresh_ports()
        conn_layout.addWidget(self.port_combo)

        self.btn_connect = QPushButton("연결")
        self.btn_connect.clicked.connect(self.connect_device)
        conn_layout.addWidget(self.btn_connect)

        self.btn_disconnect = QPushButton("연결 해제")
        self.btn_disconnect.clicked.connect(self.disconnect_device)
        self.btn_disconnect.setEnabled(False)
        conn_layout.addWidget(self.btn_disconnect)

        self.status_label = QLabel("상태: 연결 안됨")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        conn_layout.addWidget(self.status_label)

        conn_layout.addStretch()
        layout.addLayout(conn_layout)

        # Add some spacing
        layout.addSpacing(40)

        # Weight display
        weight_label = QLabel("현재 중량")
        weight_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        weight_label.setFont(font)
        layout.addWidget(weight_label)

        self.weight_display = QLabel("0.0 g")
        self.weight_display.setAlignment(Qt.AlignCenter)
        self.weight_display.setStyleSheet(
            "background-color: #2c3e50; color: #00ff00; "
            "border: 5px solid #34495e; border-radius: 15px; "
            "padding: 40px; font-size: 72pt; font-weight: bold; "
            "font-family: 'Courier New';"
        )
        layout.addWidget(self.weight_display)

        # Calibration buttons
        cal_layout = QHBoxLayout()

        self.btn_zero = QPushButton("영점 조절 (0g)")
        self.btn_zero.clicked.connect(self.calibrate_zero)
        self.btn_zero.setEnabled(False)
        button_font = QFont()
        button_font.setPointSize(12)
        self.btn_zero.setFont(button_font)
        self.btn_zero.setMinimumHeight(50)
        self.btn_zero.setStyleSheet(
            "background-color: #3498db; color: white; "
            "border-radius: 5px; font-weight: bold;"
        )
        cal_layout.addWidget(self.btn_zero)

        layout.addLayout(cal_layout)

        # Instructions
        instructions = QLabel(
            "※ 2차 곡선 보정이 적용되어 있습니다 (17g~499g 범위)\n"
            "1. 아무것도 없는 상태에서 '영점 조절' 클릭\n"
            "2. 물체를 올리면 자동으로 보정된 무게가 표시됩니다"
        )
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #27ae60; font-size: 11pt; padding: 20px;")
        layout.addWidget(instructions)

        layout.addStretch()

    def refresh_ports(self):
        """Refresh available serial ports"""
        self.port_combo.clear()
        ports = LoadCellSerial.list_ports()
        for port, desc in ports:
            self.port_combo.addItem(f"{port} - {desc}", port)

        if self.port_combo.count() == 0:
            self.port_combo.addItem("포트 없음", None)

    def connect_device(self):
        """Connect to load cell"""
        if self.port_combo.count() == 0 or self.port_combo.currentData() is None:
            QMessageBox.warning(self, "연결 오류", "사용 가능한 시리얼 포트가 없습니다.")
            return

        port = self.port_combo.currentData()
        if not port:
            port = self.port_combo.currentText().split(' ')[0]

        if self.serial.connect(port):
            self.is_connected = True
            self.btn_connect.setEnabled(False)
            self.btn_disconnect.setEnabled(True)
            self.port_combo.setEnabled(False)
            self.btn_zero.setEnabled(True)
            self.status_label.setText("상태: 연결됨 ✓")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")

            # Start reading at 20 FPS (50ms interval)
            # More stable than 30 FPS, gives sensor time to respond
            self.read_timer.start(50)  # 50ms = 20 FPS
        else:
            QMessageBox.critical(self, "연결 오류", "시리얼 포트 연결에 실패했습니다.")

    def disconnect_device(self):
        """Disconnect from load cell"""
        self.read_timer.stop()
        self.serial.disconnect()
        self.is_connected = False
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        self.port_combo.setEnabled(True)
        self.btn_zero.setEnabled(False)
        self.status_label.setText("상태: 연결 안됨")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def read_weight(self):
        """Send weight read command - same as loadcell_gui.py on_read_weight()"""
        if self.is_connected and not self.waiting_for_response:
            # IMPORTANT: Clear buffer before sending new command
            # to prevent mixing old and new responses
            self.serial.clear_rx_buffer()
            cmd = LoadCellProtocol.create_weight_read_command()
            self.serial.send_command(cmd)
            self.waiting_for_response = True

    def on_serial_data(self, data):
        """Callback when serial data is received"""
        # Emit signal for thread-safe GUI update
        self.data_received_signal.emit(data)

    def update_display(self, data):
        """
        Update display with received data
        EXACT SAME LOGIC AS loadcell_gui.py lines 496-510
        WITH calibration applied
        """
        # Parse received data
        rx_buffer = self.serial.get_rx_buffer()

        # Debug: Check buffer length
        if len(rx_buffer) < 8:
            # Incomplete response - ignore and wait for complete packet
            print(f"[DEBUG] Incomplete buffer: {len(rx_buffer)} bytes - {' '.join([f'{b:02X}' for b in rx_buffer])}")
            self.waiting_for_response = False
            return

        # IMPORTANT: Check if this is a weight response
        # Sensor sends weight data with EITHER:
        # - Byte[1] = 0x05 (read response) OR
        # - Byte[1] = 0x06 (continuous weight updates)
        # Both use Byte[2] = 0x02 (weight register)
        if len(rx_buffer) >= 3:
            func_code = rx_buffer[1]
            register = rx_buffer[2]

            # Accept both 0x05 (read response) and 0x06 (continuous updates)
            # But register must always be 0x02 for weight data
            if register != 0x02:
                print(f"[DEBUG] Not a weight response - Func=0x{func_code:02X}, Reg=0x{register:02X}, ignoring: {' '.join([f'{b:02X}' for b in rx_buffer[:8]])}")
                self.serial.clear_rx_buffer()  # Clear this junk data
                self.waiting_for_response = False
                return

            if func_code not in [0x05, 0x06]:
                print(f"[DEBUG] Unknown function code - Func=0x{func_code:02X}, ignoring: {' '.join([f'{b:02X}' for b in rx_buffer[:8]])}")
                self.serial.clear_rx_buffer()
                self.waiting_for_response = False
                return

        # Try to parse as weight response
        weight_data = LoadCellProtocol.parse_weight_response(rx_buffer)
        if weight_data:
            # Response received successfully
            self.waiting_for_response = False

            # Debug: Print raw bytes
            raw_value = weight_data['raw_weight']
            status = weight_data['status']

            # Check for suspicious zero values
            if raw_value == 0 and self.last_valid_weight > 1.0:
                print(f"[DEBUG] Suspicious zero! Status=0x{status:02X}, Buffer={' '.join([f'{b:02X}' for b in rx_buffer[:8]])}")
                # Keep last valid weight instead of showing zero
                return

            # Store raw weight from sensor
            self.raw_weight = weight_data['weight']

            # Step 1: Apply zero offset
            zeroed_weight = self.raw_weight - self.zero_offset

            # Step 2: Apply nonlinear correction (quadratic curve)
            # actual = a * measured^2 + b * measured + c
            self.current_weight = (
                self.correction_a * (zeroed_weight ** 2) +
                self.correction_b * zeroed_weight +
                self.correction_c
            )

            # Ensure non-negative weight (can't be negative after zero calibration)
            if self.current_weight < 0:
                self.current_weight = 0.0

            # Save as last valid weight (only if not zero)
            if raw_value > 0 or self.current_weight < 0.1:
                self.last_valid_weight = self.current_weight

            # Display calibrated weight
            self.weight_display.setText(f"{self.current_weight:.1f}")

    def calibrate_zero(self):
        """Set current reading as zero point"""
        self.zero_offset = self.raw_weight

        # Visual feedback
        self.btn_zero.setStyleSheet(
            "background-color: #27ae60; color: white; "
            "border-radius: 5px; font-weight: bold;"
        )
        QTimer.singleShot(1000, self.reset_zero_button_style)

        QMessageBox.information(
            self,
            "영점 조절 완료",
            f"영점이 설정되었습니다.\n현재 센서값: {self.raw_weight:.1f}g"
        )

    def reset_zero_button_style(self):
        """Reset zero button style"""
        self.btn_zero.setStyleSheet(
            "background-color: #3498db; color: white; "
            "border-radius: 5px; font-weight: bold;"
        )


    def closeEvent(self, event):
        """Handle window close event"""
        if self.is_connected:
            self.disconnect_device()
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    window = SimpleRealtimeMonitor()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
