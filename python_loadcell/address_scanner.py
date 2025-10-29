"""
Address Scanner - 모든 로드셀 주소를 감지하는 디버그 도구
전체 RX 데이터를 로그로 보여주고 어떤 주소가 사용되는지 분석
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QComboBox,
                             QTextEdit, QGroupBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from loadcell_serial import LoadCellSerial
from loadcell_protocol import LoadCellProtocol
import time


class AddressScannerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Load Cell Address Scanner")
        self.setGeometry(100, 100, 900, 700)

        # Serial
        self.serial = LoadCellSerial()

        # Detected addresses
        self.detected_addresses = {}  # {address: count}

        # Scanning state
        self.is_scanning = False

        self.init_ui()

        # Timer for continuous scanning
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.scan_loop)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Connection section
        conn_group = QGroupBox("연결 (Connection)")
        conn_layout = QHBoxLayout()

        self.port_combo = QComboBox()
        self.refresh_ports()
        conn_layout.addWidget(QLabel("포트:"))
        conn_layout.addWidget(self.port_combo)

        self.refresh_btn = QPushButton("새로고침")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        conn_layout.addWidget(self.refresh_btn)

        self.connect_btn = QPushButton("연결")
        self.connect_btn.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_btn)

        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)

        # Scanning control
        scan_group = QGroupBox("스캔 제어 (Scan Control)")
        scan_layout = QHBoxLayout()

        self.scan_btn = QPushButton("스캔 시작")
        self.scan_btn.clicked.connect(self.toggle_scanning)
        self.scan_btn.setEnabled(False)
        scan_layout.addWidget(self.scan_btn)

        self.clear_btn = QPushButton("로그 지우기")
        self.clear_btn.clicked.connect(self.clear_log)
        scan_layout.addWidget(self.clear_btn)

        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)

        # Detected addresses display
        addr_group = QGroupBox("감지된 주소 (Detected Addresses)")
        addr_layout = QVBoxLayout()

        self.address_label = QLabel("스캔을 시작하세요...")
        self.address_label.setFont(QFont("Consolas", 12, QFont.Bold))
        self.address_label.setStyleSheet("color: blue; padding: 10px;")
        addr_layout.addWidget(self.address_label)

        addr_group.setLayout(addr_layout)
        layout.addWidget(addr_group)

        # Log display
        log_group = QGroupBox("전체 로그 (Full Log)")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

    def refresh_ports(self):
        self.port_combo.clear()
        ports = LoadCellSerial.list_ports()
        for port, desc in ports:
            self.port_combo.addItem(f"{port} - {desc}", port)

    def toggle_connection(self):
        if not self.serial.is_connected:
            port = self.port_combo.currentData()
            if port and self.serial.connect(port):
                self.connect_btn.setText("연결 해제")
                self.scan_btn.setEnabled(True)
                self.log("✓ 연결 성공: " + port)
            else:
                self.log("✗ 연결 실패")
        else:
            self.serial.disconnect()
            self.connect_btn.setText("연결")
            self.scan_btn.setEnabled(False)
            if self.is_scanning:
                self.toggle_scanning()
            self.log("연결 해제됨")

    def toggle_scanning(self):
        if not self.is_scanning:
            # Start scanning
            self.is_scanning = True
            self.scan_btn.setText("스캔 중지")
            self.detected_addresses.clear()
            self.log("\n" + "="*70)
            self.log("스캔 시작...")
            self.log("="*70)
            self.scan_timer.start(50)  # Scan every 50ms
        else:
            # Stop scanning
            self.is_scanning = False
            self.scan_btn.setText("스캔 시작")
            self.scan_timer.stop()
            self.log("\n스캔 중지")

    def scan_loop(self):
        """Continuous scanning loop"""
        # Clear buffer before sending command
        self.serial.clear_rx_buffer()
        time.sleep(0.001)
        self.serial.clear_rx_buffer()

        # Send weight read command (broadcast to all addresses)
        cmd = LoadCellProtocol.create_weight_read_command()
        self.serial.send_command(cmd)

        # Wait for response
        time.sleep(0.05)

        # Get buffer
        rx_buffer = self.serial.get_rx_buffer()

        if len(rx_buffer) > 0:
            self.process_buffer(rx_buffer)

    def process_buffer(self, buffer):
        """Process received buffer and extract addresses"""
        # Log raw buffer
        hex_str = ' '.join([f'{b:02X}' for b in buffer])
        self.log(f"[RX] ({len(buffer)} bytes) {hex_str}")

        # Try to find valid responses in buffer
        # Look for function codes 0x05 (read response) or 0x06 (continuous)
        i = 0
        while i < len(buffer):
            # Check if this could be start of response
            if i + 8 <= len(buffer):
                address = buffer[i]
                func = buffer[i + 1]
                reg = buffer[i + 2]

                # Check if this looks like a weight response
                if (func == 0x05 or func == 0x06) and reg == 0x02:
                    # Found potential response
                    response_len = 9 if (i + 9 <= len(buffer)) else 8

                    response = buffer[i:i+response_len]

                    # Verify checksum
                    if response_len >= 8:
                        expected_checksum = sum(response[:response_len-1]) & 0xFF
                        actual_checksum = response[response_len-1]

                        checksum_ok = (expected_checksum == actual_checksum)

                        # Log this response
                        resp_hex = ' '.join([f'{b:02X}' for b in response])
                        self.log(f"  └─ [{response_len}B] {resp_hex}")
                        self.log(f"     Address: 0x{address:02X}, Func: 0x{func:02X}, Reg: 0x{reg:02X}")

                        if checksum_ok:
                            self.log(f"     ✓ Checksum OK")

                            # Add to detected addresses
                            if address not in self.detected_addresses:
                                self.detected_addresses[address] = 0
                            self.detected_addresses[address] += 1

                            # Parse weight
                            try:
                                weight_data = LoadCellProtocol.parse_weight_response(response)
                                self.log(f"     Weight: {weight_data['weight']:.1f}g (raw={weight_data['raw_weight']})")
                            except Exception as e:
                                self.log(f"     Parse error: {e}")
                        else:
                            self.log(f"     ✗ Checksum FAIL (expected 0x{expected_checksum:02X}, got 0x{actual_checksum:02X})")

                        # Update detected addresses display
                        self.update_address_display()

                        # Move to next potential response
                        i += response_len
                        continue

            i += 1

    def update_address_display(self):
        """Update the detected addresses label"""
        if not self.detected_addresses:
            self.address_label.setText("감지된 주소 없음")
            return

        # Sort by count (most frequent first)
        sorted_addrs = sorted(self.detected_addresses.items(),
                            key=lambda x: x[1], reverse=True)

        addr_text = "감지된 주소:\n\n"
        for addr, count in sorted_addrs:
            addr_text += f"  0x{addr:02X} ({addr:3d})  -  {count:4d}회\n"

        self.address_label.setText(addr_text)

    def clear_log(self):
        self.log_text.clear()

    def log(self, message):
        self.log_text.append(message)
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def closeEvent(self, event):
        if self.serial.is_connected:
            self.serial.disconnect()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddressScannerWindow()
    window.show()
    sys.exit(app.exec_())
