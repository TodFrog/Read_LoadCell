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
        self.zero_offset = 0.0  # Zero point offset
        self.calibration_factor = 1.0  # Scaling factor

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

        self.btn_calibrate = QPushButton("무게 교정")
        self.btn_calibrate.clicked.connect(self.calibrate_weight)
        self.btn_calibrate.setEnabled(False)
        self.btn_calibrate.setFont(button_font)
        self.btn_calibrate.setMinimumHeight(50)
        self.btn_calibrate.setStyleSheet(
            "background-color: #e67e22; color: white; "
            "border-radius: 5px; font-weight: bold;"
        )
        cal_layout.addWidget(self.btn_calibrate)

        layout.addLayout(cal_layout)

        # Instructions
        instructions = QLabel(
            "1. 아무것도 없는 상태에서 '영점 조절' 클릭\n"
            "2. 정확한 무게를 알고 있는 물체를 올림\n"
            "3. '무게 교정' 클릭 후 실제 무게 입력"
        )
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #27ae60; font-size: 12pt; padding: 20px;")
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
            self.btn_calibrate.setEnabled(True)
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
        self.btn_calibrate.setEnabled(False)
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
            # Incomplete response - ignore
            print(f"[DEBUG] Incomplete buffer: {len(rx_buffer)} bytes - {' '.join([f'{b:02X}' for b in rx_buffer])}")
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

            # Apply calibration: (raw - zero) * factor
            self.current_weight = (self.raw_weight - self.zero_offset) * self.calibration_factor

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

    def calibrate_weight(self):
        """Calibrate using known weight"""
        from PyQt5.QtWidgets import QInputDialog

        # Get actual weight from user
        actual_weight, ok = QInputDialog.getDouble(
            self,
            "무게 교정",
            f"현재 표시값: {self.current_weight:.1f}g\n\n"
            f"올려놓은 물체의 실제 무게를 입력하세요 (g):",
            value=100.0,
            min=0.1,
            max=10000.0,
            decimals=1
        )

        if ok and actual_weight > 0:
            # Calculate calibration factor
            # current_weight = (raw - zero) * factor
            # We want: actual_weight = (raw - zero) * new_factor
            # So: new_factor = actual_weight / (raw - zero)

            raw_minus_zero = self.raw_weight - self.zero_offset

            if abs(raw_minus_zero) < 0.1:
                QMessageBox.warning(
                    self,
                    "교정 오류",
                    "영점과 현재 값이 너무 가깝습니다.\n"
                    "먼저 영점을 조절한 후, 물체를 올리고 교정하세요."
                )
                return

            self.calibration_factor = actual_weight / raw_minus_zero

            # Visual feedback
            self.btn_calibrate.setStyleSheet(
                "background-color: #27ae60; color: white; "
                "border-radius: 5px; font-weight: bold;"
            )
            QTimer.singleShot(1000, self.reset_calibrate_button_style)

            QMessageBox.information(
                self,
                "교정 완료",
                f"교정이 완료되었습니다!\n\n"
                f"교정 계수: {self.calibration_factor:.4f}\n"
                f"입력한 실제 무게: {actual_weight:.1f}g\n"
                f"현재 센서 원본값: {self.raw_weight:.1f}g"
            )

    def reset_calibrate_button_style(self):
        """Reset calibrate button style"""
        self.btn_calibrate.setStyleSheet(
            "background-color: #e67e22; color: white; "
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
