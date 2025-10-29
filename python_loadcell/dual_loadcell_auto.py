#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dual Load Cell Real-time Monitor (Auto Address Detection)
- Automatically detects load cell addresses
- Uses raw_val directly as weight (no conversion)
- Supports calibration and zero adjustment
"""

import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QMessageBox, QGroupBox, QTextEdit
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QFont

from loadcell_serial import LoadCellSerial
from loadcell_protocol import LoadCellProtocol


class DualLoadCellMonitorAuto(QMainWindow):
    """Dual real-time monitor with auto address detection"""

    data_received_signal = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()

        # Serial connection
        self.serial = LoadCellSerial()
        self.serial.on_data_received = self.on_serial_data
        self.data_received_signal.connect(self.update_display)

        # Connection state
        self.is_connected = False

        # Auto-detected addresses
        self.detected_addresses = []  # List of detected addresses
        self.address_data = {}  # {address: {'raw': 0, 'zero': 0, 'factor': 1.0, 'weight': 0}}

        # Initialize UI
        self.init_ui()

        # Timer for periodic reading
        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.read_weight)

    def init_ui(self):
        self.setWindowTitle('듀얼 로드셀 모니터 (자동 주소 감지)')
        self.setGeometry(100, 100, 1000, 700)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Connection panel
        conn_group = QGroupBox("연결 설정")
        conn_layout = QHBoxLayout()

        conn_label = QLabel("통신포트:")
        conn_layout.addWidget(conn_label)

        self.port_combo = QComboBox()
        self.refresh_ports()
        conn_layout.addWidget(self.port_combo)

        refresh_btn = QPushButton("새로고침")
        refresh_btn.clicked.connect(self.refresh_ports)
        conn_layout.addWidget(refresh_btn)

        self.connect_btn = QPushButton("연결")
        self.connect_btn.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_btn)

        self.status_label = QLabel("상태: 연결 안됨")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        conn_layout.addWidget(self.status_label)

        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)

        # Detected addresses info
        addr_group = QGroupBox("감지된 로드셀")
        addr_layout = QVBoxLayout()

        self.addr_info_label = QLabel("연결 후 자동으로 로드셀 주소를 감지합니다...")
        self.addr_info_label.setFont(QFont("Consolas", 10))
        self.addr_info_label.setStyleSheet("color: blue; padding: 5px;")
        addr_layout.addWidget(self.addr_info_label)

        addr_group.setLayout(addr_layout)
        layout.addWidget(addr_group)

        # Load cells display (dynamically created)
        self.loadcells_layout = QHBoxLayout()
        layout.addLayout(self.loadcells_layout)

        # Log display
        log_group = QGroupBox("디버그 로그")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setFont(QFont("Consolas", 8))
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)

        clear_log_btn = QPushButton("로그 지우기")
        clear_log_btn.clicked.connect(lambda: self.log_text.clear())
        log_layout.addWidget(clear_log_btn)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

    def refresh_ports(self):
        self.port_combo.clear()
        ports = LoadCellSerial.list_ports()
        for port, desc in ports:
            self.port_combo.addItem(f"{port} - {desc}", port)

    def toggle_connection(self):
        if not self.is_connected:
            port = self.port_combo.currentData()
            if port and self.serial.connect(port):
                self.is_connected = True
                self.connect_btn.setText("연결 해제")
                self.status_label.setText(f"상태: 연결됨 ({port})")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
                self.read_timer.start(50)  # 20 Hz
                self.log(f"✓ 연결 성공: {port}")
            else:
                QMessageBox.critical(self, "연결 오류", "포트 연결에 실패했습니다.")
        else:
            self.read_timer.stop()
            self.serial.disconnect()
            self.is_connected = False
            self.connect_btn.setText("연결")
            self.status_label.setText("상태: 연결 안됨")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.log("연결 해제됨")

    def read_weight(self):
        if self.is_connected:
            # Clear buffer
            self.serial.clear_rx_buffer()
            time.sleep(0.001)
            self.serial.clear_rx_buffer()

            # Send broadcast command
            cmd = LoadCellProtocol.create_weight_read_command()
            self.serial.send_command(cmd)

    def on_serial_data(self, data):
        self.data_received_signal.emit(data)

    def update_display(self, data):
        rx_buffer = self.serial.get_rx_buffer()

        if len(rx_buffer) < 8:
            return

        # Parse all responses in buffer
        i = 0
        while i < len(rx_buffer):
            # Look for response start
            if i + 8 <= len(rx_buffer):
                func = rx_buffer[i + 1]
                reg = rx_buffer[i + 2]

                # Check if weight response
                if (func == 0x05 or func == 0x06) and reg == 0x02:
                    # Determine response length
                    response_len = 9 if (i + 9 <= len(rx_buffer)) else 8
                    response = rx_buffer[i:i+response_len]

                    # Verify checksum
                    expected_cs = sum(response[:response_len-1]) & 0xFF
                    actual_cs = response[response_len-1]

                    if expected_cs == actual_cs:
                        # Valid response
                        address = response[0]

                        try:
                            weight_data = LoadCellProtocol.parse_weight_response(response)
                            raw_weight = weight_data['weight']  # This is now the direct raw value
                            raw_value = weight_data['raw_weight']

                            # Log
                            hex_str = ' '.join([f'{b:02X}' for b in response])
                            self.log(f"[RX] Addr=0x{address:02X}, raw={raw_value}, weight={raw_weight:.1f}g | {hex_str}")

                            # Add to detected addresses if new
                            if address not in self.detected_addresses:
                                self.detected_addresses.append(address)
                                self.detected_addresses.sort()
                                self.address_data[address] = {
                                    'raw': 0.0,
                                    'zero': 0.0,
                                    'factor': 1.0,
                                    'weight': 0.0
                                }
                                self.rebuild_loadcell_panels()
                                self.log(f"✓ 새 로드셀 감지: 0x{address:02X}")

                            # Update data
                            self.address_data[address]['raw'] = raw_weight
                            self.address_data[address]['weight'] = (
                                (raw_weight - self.address_data[address]['zero'])
                                * self.address_data[address]['factor']
                            )

                            # Update display
                            self.update_loadcell_display(address)

                        except Exception as e:
                            self.log(f"[ERROR] Parse error: {e}")

                    i += response_len
                    continue

            i += 1

    def rebuild_loadcell_panels(self):
        """Rebuild load cell display panels for detected addresses"""
        # Clear existing panels
        while self.loadcells_layout.count():
            item = self.loadcells_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Update info label
        addr_str = ", ".join([f"0x{addr:02X}" for addr in self.detected_addresses])
        self.addr_info_label.setText(f"감지된 로드셀: {addr_str}")

        # Create panel for each detected address
        for address in self.detected_addresses:
            panel = self.create_loadcell_panel(address)
            self.loadcells_layout.addWidget(panel)

    def create_loadcell_panel(self, address):
        """Create display panel for one load cell"""
        group = QGroupBox(f"로드셀 0x{address:02X}")
        layout = QVBoxLayout()

        # Weight display
        weight_label = QLabel("무게:")
        layout.addWidget(weight_label)

        display = QLabel("0.0")
        display.setFont(QFont("Arial", 48, QFont.Bold))
        display.setAlignment(Qt.AlignCenter)
        display.setStyleSheet("border: 2px solid #333; background-color: #000; color: #0f0; padding: 20px;")
        display.setMinimumHeight(120)
        layout.addWidget(display)

        # Store reference
        setattr(self, f"display_{address:02X}", display)

        unit_label = QLabel("g")
        unit_label.setFont(QFont("Arial", 16))
        unit_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(unit_label)

        # Zero button
        zero_btn = QPushButton("영점 조절 [0]")
        zero_btn.clicked.connect(lambda: self.calibrate_zero(address))
        layout.addWidget(zero_btn)

        # Calibration button
        cal_btn = QPushButton("무게 교정")
        cal_btn.clicked.connect(lambda: self.calibrate_weight(address))
        layout.addWidget(cal_btn)

        group.setLayout(layout)
        return group

    def update_loadcell_display(self, address):
        """Update display for specific address"""
        display = getattr(self, f"display_{address:02X}", None)
        if display:
            weight = self.address_data[address]['weight']
            display.setText(f"{weight:.1f}")

    def calibrate_zero(self, address):
        """Zero calibration for specific address"""
        raw = self.address_data[address]['raw']
        self.address_data[address]['zero'] = raw
        self.log(f"✓ 영점 설정 (0x{address:02X}): {raw:.1f}g")
        QMessageBox.information(
            self,
            "영점 조절 완료",
            f"로드셀 0x{address:02X} 영점이 설정되었습니다.\n센서값: {raw:.1f}g"
        )

    def calibrate_weight(self, address):
        """Weight calibration for specific address"""
        from PyQt5.QtWidgets import QInputDialog

        # Get current displayed weight
        current_weight = self.address_data[address]['weight']

        # Ask for known weight
        known_weight, ok = QInputDialog.getDouble(
            self,
            "무게 교정",
            f"로드셀 0x{address:02X}\n\n현재 표시 무게: {current_weight:.1f}g\n\n실제 무게를 입력하세요 (g):",
            current_weight,
            0.0,
            10000.0,
            1
        )

        if ok and abs(current_weight) > 0.1:
            # Calculate calibration factor
            factor = known_weight / current_weight
            self.address_data[address]['factor'] *= factor
            self.log(f"✓ 무게 교정 (0x{address:02X}): factor={self.address_data[address]['factor']:.4f}")
            QMessageBox.information(
                self,
                "무게 교정 완료",
                f"로드셀 0x{address:02X} 교정이 완료되었습니다.\n"
                f"교정 계수: {self.address_data[address]['factor']:.4f}"
            )

    def log(self, message):
        self.log_text.append(message)
        # Auto-scroll
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_0:
            # Zero all detected load cells
            for address in self.detected_addresses:
                self.calibrate_zero(address)
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        if self.is_connected:
            self.serial.disconnect()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DualLoadCellMonitorAuto()
    window.show()
    sys.exit(app.exec_())
