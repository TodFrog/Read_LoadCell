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

        # Initialize UI
        self.init_ui()

        # Timer for periodic weight reading (30 FPS)
        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.read_weight)

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

        # Instructions
        instructions = QLabel(
            "loadcell_gui.py와 동일한 로직으로 30 FPS 자동 측정\n"
            "필터링 없음, 절대값 처리 없음, 오프셋 없음"
        )
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #7f8c8d; font-size: 12pt; padding: 20px;")
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
            self.status_label.setText("상태: 연결됨 ✓")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")

            # Start reading at ~30 FPS (same as loadcell_gui.py button clicks)
            self.read_timer.start(33)  # 33ms ≈ 30 FPS
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
        """Send weight read command - same as loadcell_gui.py on_read_weight()"""
        if self.is_connected:
            cmd = LoadCellProtocol.create_weight_read_command()
            self.serial.send_command(cmd)

    def on_serial_data(self, data):
        """Callback when serial data is received"""
        # Emit signal for thread-safe GUI update
        self.data_received_signal.emit(data)

    def update_display(self, data):
        """
        Update display with received data
        EXACT SAME LOGIC AS loadcell_gui.py lines 496-510
        """
        # Parse received data
        rx_buffer = self.serial.get_rx_buffer()

        # Try to parse as weight response
        weight_data = LoadCellProtocol.parse_weight_response(rx_buffer)
        if weight_data:
            # EXACT same line as loadcell_gui.py line 510
            self.weight_display.setText(f"{weight_data['weight']:.1f}")
            self.current_weight = weight_data['weight']

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
