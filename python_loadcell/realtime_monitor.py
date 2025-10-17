#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time Load Cell Weight Monitor
Shows live weight graph and numeric display with zero adjustment
"""

import sys
import numpy as np
from collections import deque
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QKeyEvent
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from loadcell_serial import LoadCellSerial
from loadcell_protocol import LoadCellProtocol


class RealtimeMonitor(QMainWindow):
    """Real-time load cell weight monitoring window"""

    def __init__(self):
        super().__init__()

        # Serial connection
        self.serial = LoadCellSerial()
        self.serial.on_data_received = self.on_data_received

        # Data storage
        self.max_points = 300  # Show last 10 seconds at 30 FPS
        self.weight_data = deque(maxlen=self.max_points)
        self.time_data = deque(maxlen=self.max_points)
        self.current_time = 0
        self.time_step = 1.0 / 30.0  # 30 FPS

        # Zero offset
        self.zero_offset = 0.0
        self.current_weight = 0.0

        # Connection state
        self.is_connected = False

        # Initialize UI
        self.init_ui()

        # Timer for periodic weight reading
        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.read_weight)

        # Timer for graph update
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(33)  # ~30 FPS (33ms)

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle('Real-time Load Cell Monitor')
        self.setGeometry(100, 100, 1000, 700)

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

        # Graph
        self.figure = Figure(figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Time (s)', fontsize=12)
        self.ax.set_ylabel('Weight (g)', fontsize=12)
        self.ax.set_title('Real-time Weight Monitoring', fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)

        self.line, = self.ax.plot([], [], 'b-', linewidth=2, label='Weight')
        self.ax.legend(loc='upper right')

        layout.addWidget(self.canvas)

        # Weight display
        weight_layout = QVBoxLayout()

        weight_label = QLabel("현재 중량")
        weight_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        weight_label.setFont(font)
        weight_layout.addWidget(weight_label)

        self.weight_display = QLabel("0.0 g")
        self.weight_display.setAlignment(Qt.AlignCenter)
        self.weight_display.setStyleSheet(
            "background-color: #2c3e50; color: #00ff00; "
            "border: 3px solid #34495e; border-radius: 10px; "
            "padding: 20px; font-size: 48pt; font-weight: bold; "
            "font-family: 'Courier New';"
        )
        weight_layout.addWidget(self.weight_display)

        # Instructions
        instructions = QLabel("⌨ 키보드 [0] 키를 누르면 영점 조정 (Zero Calibration)")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #3498db; font-size: 14pt; padding: 10px;")
        weight_layout.addWidget(instructions)

        layout.addLayout(weight_layout)

        # Set focus policy to receive key events
        self.setFocusPolicy(Qt.StrongFocus)

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
        """Send weight read command"""
        if self.is_connected:
            cmd = LoadCellProtocol.create_weight_read_command()
            self.serial.send_command(cmd)

    def on_data_received(self, data):
        """Callback when data is received"""
        rx_buffer = self.serial.get_rx_buffer()

        # Try to parse weight response
        weight_data = LoadCellProtocol.parse_weight_response(rx_buffer)
        if weight_data:
            # Apply zero offset
            raw_weight = weight_data['weight']
            self.current_weight = raw_weight - self.zero_offset

            # Add to data queue
            self.time_data.append(self.current_time)
            self.weight_data.append(self.current_weight)
            self.current_time += self.time_step

    def update_display(self):
        """Update graph and numeric display"""
        # Update numeric display
        self.weight_display.setText(f"{self.current_weight:.1f} g")

        # Update graph if we have data
        if len(self.weight_data) > 0:
            # Convert to numpy arrays
            times = np.array(self.time_data)
            weights = np.array(self.weight_data)

            # Update line data
            self.line.set_data(times, weights)

            # Auto-scale axes
            if len(times) > 0:
                self.ax.set_xlim(times[0], times[-1] + 1)

                # Y-axis with some margin
                if len(weights) > 0:
                    min_weight = np.min(weights)
                    max_weight = np.max(weights)
                    margin = max(abs(max_weight - min_weight) * 0.1, 10)
                    self.ax.set_ylim(min_weight - margin, max_weight + margin)

            # Redraw canvas
            self.canvas.draw()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard events"""
        if event.key() == Qt.Key_0:
            # Zero calibration
            self.zero_offset = self.current_weight + self.zero_offset
            self.current_weight = 0.0

            # Update all data points
            if len(self.weight_data) > 0:
                # Recalculate all weights with new offset
                temp_weights = list(self.weight_data)
                self.weight_data.clear()
                for w in temp_weights:
                    self.weight_data.append(0.0)  # Reset to zero

            # Visual feedback
            self.weight_display.setStyleSheet(
                "background-color: #27ae60; color: white; "
                "border: 3px solid #229954; border-radius: 10px; "
                "padding: 20px; font-size: 48pt; font-weight: bold; "
                "font-family: 'Courier New';"
            )

            # Reset style after 500ms
            QTimer.singleShot(500, self.reset_display_style)

            print(f"영점 조정됨! 새로운 오프셋: {self.zero_offset:.1f} g")

    def reset_display_style(self):
        """Reset display style to normal"""
        self.weight_display.setStyleSheet(
            "background-color: #2c3e50; color: #00ff00; "
            "border: 3px solid #34495e; border-radius: 10px; "
            "padding: 20px; font-size: 48pt; font-weight: bold; "
            "font-family: 'Courier New';"
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

    window = RealtimeMonitor()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
