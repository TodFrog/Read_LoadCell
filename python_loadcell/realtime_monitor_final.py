#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time Load Cell Weight Monitor (Final Version)
- Absolute value mode for off-center loads
- Better noise filtering
- Auto-calibration support
"""

import sys
import numpy as np
from collections import deque
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QMessageBox, QCheckBox, QGroupBox,
    QRadioButton, QButtonGroup
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QKeyEvent
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from loadcell_serial import LoadCellSerial
from loadcell_protocol import LoadCellProtocol


class RealtimeMonitorFinal(QMainWindow):
    """Final version with absolute value and improved handling"""

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

        # Moving average filter
        self.filter_size = 5  # Average last 5 readings
        self.raw_weights = deque(maxlen=self.filter_size)

        # Zero offset
        self.zero_offset = 0.0
        self.current_weight = 0.0
        self.raw_weight = 0.0

        # Measurement mode
        self.use_absolute_value = True  # Use absolute value by default

        # Connection state
        self.is_connected = False

        # Filter enable/disable
        self.filter_enabled = True

        # Debug info
        self.last_resolution = 0
        self.last_division = 0
        self.last_raw_value = 0

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
        self.setWindowTitle('로드셀 실시간 모니터 (개선판)')
        self.setGeometry(100, 100, 1100, 800)

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

        # Settings panel
        settings_group = QGroupBox("측정 설정")
        settings_layout = QHBoxLayout()

        # Filter checkbox
        self.filter_checkbox = QCheckBox("노이즈 필터")
        self.filter_checkbox.setChecked(True)
        self.filter_checkbox.stateChanged.connect(self.toggle_filter)
        settings_layout.addWidget(self.filter_checkbox)

        # Measurement mode
        mode_label = QLabel("측정 모드:")
        settings_layout.addWidget(mode_label)

        self.mode_group = QButtonGroup()

        self.radio_absolute = QRadioButton("절대값 모드 (외곽 물체 대응)")
        self.radio_absolute.setChecked(True)
        self.radio_absolute.toggled.connect(self.on_mode_changed)
        self.mode_group.addButton(self.radio_absolute)
        settings_layout.addWidget(self.radio_absolute)

        self.radio_signed = QRadioButton("부호 모드 (센터 전용)")
        self.radio_signed.toggled.connect(self.on_mode_changed)
        self.mode_group.addButton(self.radio_signed)
        settings_layout.addWidget(self.radio_signed)

        settings_layout.addStretch()
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Debug info panel
        debug_group = QGroupBox("디버그 정보")
        debug_layout = QHBoxLayout()

        self.label_resolution = QLabel("분해도: --")
        debug_layout.addWidget(self.label_resolution)

        self.label_division = QLabel("Division: --")
        debug_layout.addWidget(self.label_division)

        self.label_raw_value = QLabel("Raw Value: --")
        debug_layout.addWidget(self.label_raw_value)

        debug_layout.addStretch()
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)

        # Graph
        self.figure = Figure(figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Time (s)', fontsize=12)
        self.ax.set_ylabel('Weight (g)', fontsize=12)
        self.ax.set_title('실시간 중량 모니터링', fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)

        self.line, = self.ax.plot([], [], 'b-', linewidth=2, label='중량')
        self.ax.axhline(y=0, color='r', linestyle='--', alpha=0.3, label='영점')
        self.ax.legend(loc='upper right')

        layout.addWidget(self.canvas)

        # Weight display
        weight_layout = QHBoxLayout()

        # Current weight (filtered)
        current_box = QVBoxLayout()
        current_label = QLabel("현재 중량 (필터링)")
        current_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        current_label.setFont(font)
        current_box.addWidget(current_label)

        self.weight_display = QLabel("0.0 g")
        self.weight_display.setAlignment(Qt.AlignCenter)
        self.weight_display.setStyleSheet(
            "background-color: #2c3e50; color: #00ff00; "
            "border: 3px solid #34495e; border-radius: 10px; "
            "padding: 20px; font-size: 48pt; font-weight: bold; "
            "font-family: 'Courier New';"
        )
        current_box.addWidget(self.weight_display)
        weight_layout.addLayout(current_box)

        # Raw weight display
        raw_box = QVBoxLayout()
        raw_label = QLabel("원본 값 (부호 포함)")
        raw_label.setAlignment(Qt.AlignCenter)
        raw_label.setFont(font)
        raw_box.addWidget(raw_label)

        self.raw_display = QLabel("0.0 g")
        self.raw_display.setAlignment(Qt.AlignCenter)
        self.raw_display.setStyleSheet(
            "background-color: #34495e; color: #ffaa00; "
            "border: 2px solid #2c3e50; border-radius: 10px; "
            "padding: 20px; font-size: 32pt; font-weight: bold; "
            "font-family: 'Courier New';"
        )
        raw_box.addWidget(self.raw_display)
        weight_layout.addLayout(raw_box)

        layout.addLayout(weight_layout)

        # Instructions
        instructions = QLabel(
            "⌨ [0] 키: 영점 조정 | "
            "절대값 모드 권장 (외곽 물체가 음수로 나올 때)"
        )
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #3498db; font-size: 14pt; padding: 10px;")
        layout.addWidget(instructions)

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

    def toggle_filter(self, state):
        """Toggle noise filter on/off"""
        self.filter_enabled = (state == Qt.Checked)
        if not self.filter_enabled:
            self.raw_weights.clear()

    def on_mode_changed(self):
        """Handle measurement mode change"""
        self.use_absolute_value = self.radio_absolute.isChecked()
        print(f"측정 모드 변경: {'절대값' if self.use_absolute_value else '부호 포함'}")

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
            # Clear buffer before sending new command
            self.serial.clear_rx_buffer()
            cmd = LoadCellProtocol.create_weight_read_command()
            self.serial.send_command(cmd)

    def on_data_received(self, data):
        """Callback when data is received"""
        # Get fresh buffer
        rx_buffer = self.serial.get_rx_buffer()

        # Try to parse weight response
        weight_data = LoadCellProtocol.parse_weight_response(rx_buffer)
        if weight_data:
            # Debug info
            self.last_resolution = weight_data['resolution']
            self.last_division = weight_data['division']
            self.last_raw_value = weight_data['raw_weight']

            # Get raw weight with sign
            raw_weight_signed = weight_data['weight']

            # Apply absolute value mode if enabled
            if self.use_absolute_value:
                # Always use absolute value (ignore sign bit)
                raw_weight_abs = abs(raw_weight_signed)
                self.raw_weight = raw_weight_abs - self.zero_offset
            else:
                # Use signed value (respect sign bit)
                self.raw_weight = raw_weight_signed - self.zero_offset

            # Apply moving average filter if enabled
            if self.filter_enabled:
                self.raw_weights.append(self.raw_weight)
                if len(self.raw_weights) > 0:
                    self.current_weight = np.mean(self.raw_weights)
                else:
                    self.current_weight = self.raw_weight
            else:
                self.current_weight = self.raw_weight

            # Add to data queue (for graph)
            self.time_data.append(self.current_time)
            self.weight_data.append(self.current_weight)
            self.current_time += self.time_step

    def update_display(self):
        """Update graph and numeric display"""
        # Update debug info
        self.label_resolution.setText(f"분해도: {self.last_resolution}g")
        self.label_division.setText(f"Division: {self.last_division} (0x{self.last_division:X})")
        self.label_raw_value.setText(f"Raw Value: {self.last_raw_value}")

        # Update numeric displays
        self.weight_display.setText(f"{self.current_weight:.1f} g")
        self.raw_display.setText(f"{self.raw_weight:.1f} g")

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
            # Zero calibration: add current weight to offset
            self.zero_offset += self.current_weight

            # Clear moving average buffer to reset filter
            self.raw_weights.clear()

            # Visual feedback
            self.weight_display.setStyleSheet(
                "background-color: #27ae60; color: white; "
                "border: 3px solid #229954; border-radius: 10px; "
                "padding: 20px; font-size: 48pt; font-weight: bold; "
                "font-family: 'Courier New';"
            )

            # Reset style after 500ms
            QTimer.singleShot(500, self.reset_display_style)

            print(f"영점 조정됨! 누적 오프셋: {self.zero_offset:.1f} g")

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

    window = RealtimeMonitorFinal()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
