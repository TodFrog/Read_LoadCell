#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Real-time Monitor
Shows raw sensor data to understand what's happening
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QMessageBox, QTextEdit, QGroupBox
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QFont

from loadcell_serial import LoadCellSerial
from loadcell_protocol import LoadCellProtocol


class DebugRealtimeMonitor(QMainWindow):
    """Debug monitor to see raw sensor data"""

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

        # Initialize UI
        self.init_ui()

        # Timer for periodic weight reading (30 FPS)
        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.read_weight)

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle('디버그 모니터 - 센서 데이터 분석')
        self.setGeometry(100, 100, 900, 700)

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

        # Weight display
        weight_group = QGroupBox("현재 중량")
        weight_layout = QVBoxLayout()

        self.weight_display = QLabel("0.0 g")
        self.weight_display.setAlignment(Qt.AlignCenter)
        self.weight_display.setStyleSheet(
            "background-color: #2c3e50; color: #00ff00; "
            "border: 3px solid #34495e; border-radius: 10px; "
            "padding: 20px; font-size: 48pt; font-weight: bold; "
            "font-family: 'Courier New';"
        )
        weight_layout.addWidget(self.weight_display)
        weight_group.setLayout(weight_layout)
        layout.addWidget(weight_group)

        # Debug info
        debug_group = QGroupBox("센서 원본 데이터 (16진수)")
        debug_layout = QVBoxLayout()

        self.raw_hex_display = QTextEdit()
        self.raw_hex_display.setReadOnly(True)
        self.raw_hex_display.setMaximumHeight(100)
        self.raw_hex_display.setStyleSheet(
            "background-color: #1e1e1e; color: #00ff00; "
            "font-family: 'Courier New'; font-size: 11pt;"
        )
        debug_layout.addWidget(self.raw_hex_display)
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)

        # Parsed data
        parsed_group = QGroupBox("파싱된 데이터")
        parsed_layout = QVBoxLayout()

        info_font = QFont("Courier New", 11)

        self.label_status = QLabel("Status: --")
        self.label_status.setFont(info_font)
        parsed_layout.addWidget(self.label_status)

        self.label_division = QLabel("Division Index: --")
        self.label_division.setFont(info_font)
        parsed_layout.addWidget(self.label_division)

        self.label_resolution = QLabel("Resolution: -- g")
        self.label_resolution.setFont(info_font)
        parsed_layout.addWidget(self.label_resolution)

        self.label_raw_weight = QLabel("Raw Weight Value (3-byte): --")
        self.label_raw_weight.setFont(info_font)
        parsed_layout.addWidget(self.label_raw_weight)

        self.label_sign = QLabel("Sign Bit: --")
        self.label_sign.setFont(info_font)
        parsed_layout.addWidget(self.label_sign)

        self.label_calculated = QLabel("Calculated Weight: -- g")
        self.label_calculated.setFont(info_font)
        parsed_layout.addWidget(self.label_calculated)

        self.label_formula = QLabel("Formula: --")
        self.label_formula.setFont(info_font)
        self.label_formula.setWordWrap(True)
        parsed_layout.addWidget(self.label_formula)

        parsed_group.setLayout(parsed_layout)
        layout.addWidget(parsed_group)

        # Instructions
        instructions = QLabel(
            "이 화면으로 각 물체마다 센서가 보내는 실제 데이터를 확인하세요.\n"
            "Division, Resolution, Raw Value가 물체마다 다르게 나오는지 확인!"
        )
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #e74c3c; font-size: 11pt; padding: 10px;")
        layout.addWidget(instructions)

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
            self.status_label.setText("상태: 연결됨 ✓")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")

            # Start reading at ~30 FPS
            self.read_timer.start(33)
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
        self.status_label.setText("상태: 연결 안됨")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def read_weight(self):
        """Send weight read command"""
        if self.is_connected:
            cmd = LoadCellProtocol.create_weight_read_command()
            self.serial.send_command(cmd)

    def on_serial_data(self, data):
        """Callback when serial data is received"""
        self.data_received_signal.emit(data)

    def update_display(self, data):
        """Update display with received data"""
        # Show raw hex data
        rx_buffer = self.serial.get_rx_buffer()

        # Add function code indicator
        if len(rx_buffer) >= 2:
            func_code = rx_buffer[1]
            func_name = "READ(0x05)" if func_code == 0x05 else f"FUNC(0x{func_code:02X})"
            hex_str = f"[{func_name}] " + ' '.join([f'{b:02X}' for b in rx_buffer])
        else:
            hex_str = ' '.join([f'{b:02X}' for b in rx_buffer])

        self.raw_hex_display.append(hex_str)

        # Auto-scroll to bottom and limit lines
        cursor = self.raw_hex_display.textCursor()
        cursor.movePosition(cursor.End)
        self.raw_hex_display.setTextCursor(cursor)

        # Try to parse as weight response
        weight_data = LoadCellProtocol.parse_weight_response(rx_buffer)
        if weight_data:
            # Display weight
            self.weight_display.setText(f"{weight_data['weight']:.1f}")

            # Show detailed parsing
            status = weight_data['status']
            division = weight_data['division']
            resolution = weight_data['resolution']
            raw_weight = weight_data['raw_weight']
            is_negative = weight_data.get('is_negative', False)
            calculated_weight = weight_data['weight']

            self.label_status.setText(f"Status: 0x{status:02X} ({status})")
            self.label_division.setText(f"Division Index: {division} (0x{division:X})")
            self.label_resolution.setText(f"Resolution: {resolution} g")
            self.label_raw_weight.setText(f"Raw Weight Value (3-byte): {raw_weight} (0x{raw_weight:X})")
            self.label_sign.setText(f"Sign Bit: {'NEGATIVE (-)' if is_negative else 'POSITIVE (+)'}")
            self.label_calculated.setText(f"Calculated Weight: {calculated_weight:.1f} g")

            # Show formula
            sign_str = '-' if is_negative else '+'
            formula = (
                f"Formula: {sign_str}({resolution} g/division × {raw_weight}) = "
                f"{sign_str}{abs(calculated_weight):.1f} g"
            )
            self.label_formula.setText(formula)

            # Show raw bytes breakdown
            if len(rx_buffer) >= 8:
                breakdown = (
                    f"\nByte breakdown:\n"
                    f"  [0] Address: 0x{rx_buffer[0]:02X}\n"
                    f"  [1] Function: 0x{rx_buffer[1]:02X}\n"
                    f"  [2] Register: 0x{rx_buffer[2]:02X}\n"
                    f"  [3] Status: 0x{rx_buffer[3]:02X}\n"
                    f"  [4] Sign+Division: 0x{rx_buffer[4]:02X} = "
                    f"[{'1' if rx_buffer[4] & 0x80 else '0'}][xxx][{division:04b}]\n"
                    f"  [5] Weight High: 0x{rx_buffer[5]:02X} ({rx_buffer[5]})\n"
                    f"  [6] Weight Mid: 0x{rx_buffer[6]:02X} ({rx_buffer[6]})\n"
                    f"  [7] Weight Low: 0x{rx_buffer[7]:02X} ({rx_buffer[7]})\n"
                )
                self.label_formula.setText(formula + breakdown)

    def closeEvent(self, event):
        """Handle window close event"""
        if self.is_connected:
            self.disconnect_device()
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = DebugRealtimeMonitor()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
