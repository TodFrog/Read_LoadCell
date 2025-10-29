#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dual Load Cell Real-time Monitor
Displays data from two load cells simultaneously on the same USB bus
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QMessageBox, QGroupBox
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QFont

from loadcell_serial import LoadCellSerial
from loadcell_protocol import LoadCellProtocol


class DualLoadCellMonitor(QMainWindow):
    """Dual real-time monitor - displays two load cells side by side"""

    # Signal for thread-safe GUI updates
    data_received_signal = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()

        # Serial connection (shared by both load cells)
        self.serial = LoadCellSerial()
        self.serial.on_data_received = self.on_serial_data

        # Connect signal
        self.data_received_signal.connect(self.update_display)

        # Connection state
        self.is_connected = False

        # Load Cell 1 data (Address 3)
        self.loadcell1_address = 0x03
        self.loadcell1_weight = 0.0
        self.loadcell1_raw = 0.0
        self.loadcell1_zero = 0.0
        self.loadcell1_factor = 1.0

        # Load Cell 2 data (Address 4)
        self.loadcell2_address = 0x04
        self.loadcell2_weight = 0.0
        self.loadcell2_raw = 0.0
        self.loadcell2_zero = 0.0
        self.loadcell2_factor = 1.0

        # Response tracking
        self.waiting_for_response = False

        # Initialize UI
        self.init_ui()

        # Timer for periodic weight reading
        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.read_weight)

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle('듀얼 로드셀 모니터')
        self.setGeometry(100, 100, 900, 500)

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

        layout.addLayout(conn_layout)

        # Dual load cell display
        dual_layout = QHBoxLayout()

        # Load Cell 1
        self.loadcell1_group = self.create_loadcell_panel(
            "로드셀 #1 (주소: 0x03)",
            1
        )
        dual_layout.addWidget(self.loadcell1_group)

        # Load Cell 2
        self.loadcell2_group = self.create_loadcell_panel(
            "로드셀 #2 (주소: 0x04)",
            2
        )
        dual_layout.addWidget(self.loadcell2_group)

        layout.addLayout(dual_layout)

        # Instructions
        instructions = QLabel(
            "※ USB 버스의 두 로드셀을 동시에 모니터링합니다\n"
            "※ 각 로드셀을 독립적으로 영점 조절 및 교정 가능\n"
            "※ 체크섬 검증 및 주소 필터링 자동 적용"
        )
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #27ae60; font-size: 10pt; padding: 10px;")
        layout.addWidget(instructions)

        layout.addStretch()

    def create_loadcell_panel(self, title, loadcell_num):
        """Create panel for one load cell"""
        group = QGroupBox(title)
        group_layout = QVBoxLayout()

        # Weight display
        weight_label = QLabel("현재 중량:")
        weight_label.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(weight_label)

        weight_display = QLabel("0.0")
        weight_display.setAlignment(Qt.AlignCenter)
        weight_font = QFont()
        weight_font.setPointSize(36)
        weight_font.setBold(True)
        weight_display.setFont(weight_font)
        weight_display.setStyleSheet("color: #2c3e50; padding: 20px;")
        group_layout.addWidget(weight_display)

        unit_label = QLabel("g")
        unit_label.setAlignment(Qt.AlignCenter)
        unit_font = QFont()
        unit_font.setPointSize(18)
        unit_label.setFont(unit_font)
        group_layout.addWidget(unit_label)

        # Calibration buttons
        button_font = QFont()
        button_font.setPointSize(10)

        btn_zero = QPushButton("영점 조절")
        btn_zero.setFont(button_font)
        btn_zero.setMinimumHeight(40)
        btn_zero.setEnabled(False)
        btn_zero.setStyleSheet(
            "background-color: #3498db; color: white; "
            "border-radius: 5px; font-weight: bold;"
        )
        if loadcell_num == 1:
            btn_zero.clicked.connect(self.calibrate_zero_1)
        else:
            btn_zero.clicked.connect(self.calibrate_zero_2)
        group_layout.addWidget(btn_zero)

        btn_calibrate = QPushButton("무게 교정")
        btn_calibrate.setFont(button_font)
        btn_calibrate.setMinimumHeight(40)
        btn_calibrate.setEnabled(False)
        btn_calibrate.setStyleSheet(
            "background-color: #e67e22; color: white; "
            "border-radius: 5px; font-weight: bold;"
        )
        if loadcell_num == 1:
            btn_calibrate.clicked.connect(self.calibrate_weight_1)
        else:
            btn_calibrate.clicked.connect(self.calibrate_weight_2)
        group_layout.addWidget(btn_calibrate)

        group.setLayout(group_layout)

        # Store references
        if loadcell_num == 1:
            self.loadcell1_display = weight_display
            self.loadcell1_btn_zero = btn_zero
            self.loadcell1_btn_cal = btn_calibrate
        else:
            self.loadcell2_display = weight_display
            self.loadcell2_btn_zero = btn_zero
            self.loadcell2_btn_cal = btn_calibrate

        return group

    def refresh_ports(self):
        """Refresh available serial ports"""
        self.port_combo.clear()
        ports = LoadCellSerial.list_ports()
        for port, desc in ports:
            self.port_combo.addItem(f"{port} - {desc}", port)

        if self.port_combo.count() == 0:
            self.port_combo.addItem("포트 없음", None)

    def connect_device(self):
        """Connect to load cells"""
        port = self.port_combo.currentData()
        if port is None:
            port = self.port_combo.currentText().split(' ')[0]

        if self.serial.connect(port):
            self.is_connected = True
            self.btn_connect.setEnabled(False)
            self.btn_disconnect.setEnabled(True)
            self.port_combo.setEnabled(False)

            # Enable all calibration buttons
            self.loadcell1_btn_zero.setEnabled(True)
            self.loadcell1_btn_cal.setEnabled(True)
            self.loadcell2_btn_zero.setEnabled(True)
            self.loadcell2_btn_cal.setEnabled(True)

            self.status_label.setText("상태: 연결됨 ✓")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")

            # Start reading at 20 FPS
            self.read_timer.start(50)  # 50ms = 20 FPS
        else:
            QMessageBox.critical(self, "연결 오류", "시리얼 포트 연결에 실패했습니다.")

    def disconnect_device(self):
        """Disconnect from load cells"""
        self.read_timer.stop()
        self.serial.disconnect()
        self.is_connected = False
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        self.port_combo.setEnabled(True)

        # Disable all calibration buttons
        self.loadcell1_btn_zero.setEnabled(False)
        self.loadcell1_btn_cal.setEnabled(False)
        self.loadcell2_btn_zero.setEnabled(False)
        self.loadcell2_btn_cal.setEnabled(False)

        self.status_label.setText("상태: 연결 안됨")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def read_weight(self):
        """Send weight read command"""
        if self.is_connected and not self.waiting_for_response:
            # Clear buffer thoroughly
            self.serial.clear_rx_buffer()
            import time
            time.sleep(0.001)
            self.serial.clear_rx_buffer()

            # Send broadcast command (address 0x00)
            # Both load cells will respond
            cmd = LoadCellProtocol.create_weight_read_command()
            self.serial.send_command(cmd)
            self.waiting_for_response = True

    def on_serial_data(self, data):
        """Callback when serial data is received"""
        self.data_received_signal.emit(data)

    def update_display(self, data):
        """Update display with received data"""
        rx_buffer = self.serial.get_rx_buffer()

        # Check minimum length
        if len(rx_buffer) < 8:
            self.waiting_for_response = False
            return

        # Verify checksum
        expected_checksum = sum(rx_buffer[:7]) & 0xFF
        actual_checksum = rx_buffer[7]

        if expected_checksum != actual_checksum:
            print(f"[DEBUG] Checksum mismatch!")
            self.serial.clear_rx_buffer()
            self.waiting_for_response = False
            return

        # Check if weight response
        if len(rx_buffer) >= 3:
            func_code = rx_buffer[1]
            register = rx_buffer[2]

            if register != 0x02 or func_code not in [0x05, 0x06]:
                self.serial.clear_rx_buffer()
                self.waiting_for_response = False
                return

        # Parse weight data
        weight_data = LoadCellProtocol.parse_weight_response(rx_buffer)
        if weight_data:
            self.waiting_for_response = False

            # Determine which load cell this data is from
            address = rx_buffer[0]
            raw_weight = weight_data['weight']

            if address == self.loadcell1_address:
                # Update Load Cell 1
                self.loadcell1_raw = raw_weight
                self.loadcell1_weight = (raw_weight - self.loadcell1_zero) * self.loadcell1_factor
                self.loadcell1_display.setText(f"{self.loadcell1_weight:.1f}")

            elif address == self.loadcell2_address:
                # Update Load Cell 2
                self.loadcell2_raw = raw_weight
                self.loadcell2_weight = (raw_weight - self.loadcell2_zero) * self.loadcell2_factor
                self.loadcell2_display.setText(f"{self.loadcell2_weight:.1f}")
            else:
                print(f"[DEBUG] Unknown address: 0x{address:02X}")

    def calibrate_zero_1(self):
        """Calibrate zero for load cell 1"""
        self.loadcell1_zero = self.loadcell1_raw
        QMessageBox.information(
            self,
            "영점 조절 완료",
            f"로드셀 #1 영점이 설정되었습니다.\n센서값: {self.loadcell1_raw:.1f}g"
        )

    def calibrate_zero_2(self):
        """Calibrate zero for load cell 2"""
        self.loadcell2_zero = self.loadcell2_raw
        QMessageBox.information(
            self,
            "영점 조절 완료",
            f"로드셀 #2 영점이 설정되었습니다.\n센서값: {self.loadcell2_raw:.1f}g"
        )

    def calibrate_weight_1(self):
        """Calibrate weight for load cell 1"""
        from PyQt5.QtWidgets import QInputDialog

        actual_weight, ok = QInputDialog.getDouble(
            self,
            "로드셀 #1 무게 교정",
            f"현재 표시값: {self.loadcell1_weight:.1f}g\n\n"
            f"올려놓은 물체의 실제 무게를 입력하세요 (g):",
            value=100.0,
            min=0.1,
            max=10000.0,
            decimals=1
        )

        if ok and actual_weight > 0:
            zeroed = self.loadcell1_raw - self.loadcell1_zero

            if abs(zeroed) < 0.1:
                QMessageBox.warning(
                    self,
                    "교정 오류",
                    "영점과 현재 값이 너무 가깝습니다."
                )
                return

            self.loadcell1_factor = actual_weight / zeroed

            QMessageBox.information(
                self,
                "교정 완료",
                f"로드셀 #1 교정이 완료되었습니다!\n\n"
                f"교정 계수: {self.loadcell1_factor:.4f}\n"
                f"실제 무게: {actual_weight:.1f}g"
            )

    def calibrate_weight_2(self):
        """Calibrate weight for load cell 2"""
        from PyQt5.QtWidgets import QInputDialog

        actual_weight, ok = QInputDialog.getDouble(
            self,
            "로드셀 #2 무게 교정",
            f"현재 표시값: {self.loadcell2_weight:.1f}g\n\n"
            f"올려놓은 물체의 실제 무게를 입력하세요 (g):",
            value=100.0,
            min=0.1,
            max=10000.0,
            decimals=1
        )

        if ok and actual_weight > 0:
            zeroed = self.loadcell2_raw - self.loadcell2_zero

            if abs(zeroed) < 0.1:
                QMessageBox.warning(
                    self,
                    "교정 오류",
                    "영점과 현재 값이 너무 가깝습니다."
                )
                return

            self.loadcell2_factor = actual_weight / zeroed

            QMessageBox.information(
                self,
                "교정 완료",
                f"로드셀 #2 교정이 완료되었습니다!\n\n"
                f"교정 계수: {self.loadcell2_factor:.4f}\n"
                f"실제 무게: {actual_weight:.1f}g"
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

    window = DualLoadCellMonitor()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
