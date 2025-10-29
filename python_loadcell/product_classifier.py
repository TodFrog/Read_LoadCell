#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Product Classification System
상품 추가/제거 감지 및 로깅 시스템
"""

import sys
import time
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QMessageBox, QGroupBox, QTextEdit,
    QSpinBox
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QFont

from loadcell_serial import LoadCellSerial
from loadcell_protocol import LoadCellProtocol


# ============================================================
# 튜닝 가능한 파라미터 (TUNABLE PARAMETERS)
# ============================================================
STABLE_COUNT_THRESHOLD = 5  # 안정 상태 판단: 같은 무게가 N번 반복되면 안정
WEIGHT_TOLERANCE = 1.0      # 무게 허용 오차: ±1g는 같은 무게로 간주
# ============================================================


class ProductClassifier(QMainWindow):
    """상품 분류 시스템 - 무게 추가/제거 감지"""

    data_received_signal = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()

        # Serial connection
        self.serial = LoadCellSerial()
        self.serial.on_data_received = self.on_serial_data
        self.data_received_signal.connect(self.update_display)

        # Connection state
        self.is_connected = False

        # Weight tracking
        self.current_weight = 0.0
        self.raw_weight = 0.0
        self.zero_offset = 0.0
        self.calibration_factor = 1.0

        # Stability detection
        self.stable_count_threshold = STABLE_COUNT_THRESHOLD  # Tunable
        self.weight_tolerance = WEIGHT_TOLERANCE  # Tunable
        self.weight_history = []  # Recent weight readings
        self.is_stable = False
        self.stable_weight = 0.0

        # Change tracking
        self.last_stable_weight = 0.0
        self.product_id = 1

        # Log file
        self.log_file = "product_log.txt"

        # Initialize UI
        self.init_ui()

        # Timer for periodic reading
        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.read_weight)

    def init_ui(self):
        self.setWindowTitle('상품 분류 시스템 (Product Classifier)')
        self.setGeometry(100, 100, 800, 700)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Tuning parameters section
        tuning_group = QGroupBox("튜닝 파라미터 (Tuning Parameters)")
        tuning_layout = QHBoxLayout()

        tuning_layout.addWidget(QLabel("안정 상태 판단 횟수:"))
        self.stable_count_spin = QSpinBox()
        self.stable_count_spin.setRange(1, 20)
        self.stable_count_spin.setValue(STABLE_COUNT_THRESHOLD)
        self.stable_count_spin.valueChanged.connect(self.update_stable_threshold)
        tuning_layout.addWidget(self.stable_count_spin)

        tuning_layout.addWidget(QLabel("무게 허용 오차 (±g):"))
        self.tolerance_spin = QSpinBox()
        self.tolerance_spin.setRange(0, 10)
        self.tolerance_spin.setValue(int(WEIGHT_TOLERANCE))
        self.tolerance_spin.valueChanged.connect(self.update_tolerance)
        tuning_layout.addWidget(self.tolerance_spin)

        tuning_layout.addStretch()

        tuning_group.setLayout(tuning_layout)
        layout.addWidget(tuning_group)

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

        # Current weight display
        weight_group = QGroupBox("현재 무게")
        weight_layout = QVBoxLayout()

        self.weight_display = QLabel("0.0")
        self.weight_display.setFont(QFont("Arial", 60, QFont.Bold))
        self.weight_display.setAlignment(Qt.AlignCenter)
        self.weight_display.setStyleSheet(
            "border: 2px solid #333; background-color: #000; color: #0f0; padding: 20px;"
        )
        weight_layout.addWidget(self.weight_display)

        unit_label = QLabel("g")
        unit_label.setFont(QFont("Arial", 20))
        unit_label.setAlignment(Qt.AlignCenter)
        weight_layout.addWidget(unit_label)

        # Stability indicator
        self.stability_label = QLabel("상태: 대기 중...")
        self.stability_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.stability_label.setAlignment(Qt.AlignCenter)
        self.stability_label.setStyleSheet("color: gray; padding: 10px;")
        weight_layout.addWidget(self.stability_label)

        weight_group.setLayout(weight_layout)
        layout.addWidget(weight_group)

        # Calibration buttons
        cal_layout = QHBoxLayout()

        zero_btn = QPushButton("영점 조절 [0]")
        zero_btn.clicked.connect(self.calibrate_zero)
        cal_layout.addWidget(zero_btn)

        cal_btn = QPushButton("무게 교정")
        cal_btn.clicked.connect(self.calibrate_weight)
        cal_layout.addWidget(cal_btn)

        reset_btn = QPushButton("기록 초기화")
        reset_btn.clicked.connect(self.reset_log)
        cal_layout.addWidget(reset_btn)

        layout.addLayout(cal_layout)

        # Change detection display
        change_group = QGroupBox("무게 변화 감지")
        change_layout = QVBoxLayout()

        self.change_display = QTextEdit()
        self.change_display.setFont(QFont("Consolas", 12))
        self.change_display.setReadOnly(True)
        self.change_display.setMaximumHeight(150)
        change_layout.addWidget(self.change_display)

        change_group.setLayout(change_layout)
        layout.addWidget(change_group)

        # Product log display
        log_group = QGroupBox("상품 기록 (product_log.txt)")
        log_layout = QVBoxLayout()

        self.product_log_display = QTextEdit()
        self.product_log_display.setFont(QFont("Consolas", 10))
        self.product_log_display.setReadOnly(True)
        log_layout.addWidget(self.product_log_display)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # Load existing log
        self.load_product_log()

    def update_stable_threshold(self, value):
        """Update stability threshold"""
        self.stable_count_threshold = value

    def update_tolerance(self, value):
        """Update weight tolerance"""
        self.weight_tolerance = float(value)

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
            else:
                QMessageBox.critical(self, "연결 오류", "포트 연결에 실패했습니다.")
        else:
            self.read_timer.stop()
            self.serial.disconnect()
            self.is_connected = False
            self.connect_btn.setText("연결")
            self.status_label.setText("상태: 연결 안됨")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def read_weight(self):
        if self.is_connected:
            # Clear buffer
            self.serial.clear_rx_buffer()
            time.sleep(0.001)
            self.serial.clear_rx_buffer()

            # Send command
            cmd = LoadCellProtocol.create_weight_read_command()
            self.serial.send_command(cmd)

    def on_serial_data(self, data):
        self.data_received_signal.emit(data)

    def update_display(self, data):
        rx_buffer = self.serial.get_rx_buffer()

        if len(rx_buffer) < 8:
            return

        # Parse weight
        try:
            weight_data = LoadCellProtocol.parse_weight_response(rx_buffer)
            if weight_data:
                self.raw_weight = weight_data['weight']
                self.current_weight = (self.raw_weight - self.zero_offset) * self.calibration_factor

                # Update display
                self.weight_display.setText(f"{self.current_weight:.1f}")

                # Check stability
                self.check_stability()

        except Exception as e:
            pass

    def check_stability(self):
        """
        안정 상태 감지:
        - 같은 무게가 N번 반복되면 안정 상태
        - ±tolerance 범위 내는 같은 무게로 간주
        """
        # Add to history
        self.weight_history.append(self.current_weight)

        # Keep only recent readings
        if len(self.weight_history) > self.stable_count_threshold + 5:
            self.weight_history = self.weight_history[-self.stable_count_threshold-5:]

        # Check if we have enough data
        if len(self.weight_history) < self.stable_count_threshold:
            self.stability_label.setText("상태: 데이터 수집 중...")
            self.stability_label.setStyleSheet("color: gray; padding: 10px;")
            return

        # Get recent N readings
        recent = self.weight_history[-self.stable_count_threshold:]

        # Check if all readings are within tolerance of each other
        avg = sum(recent) / len(recent)
        all_stable = all(abs(w - avg) <= self.weight_tolerance for w in recent)

        if all_stable:
            # Stable state detected
            if not self.is_stable:
                # Transition to stable state
                self.is_stable = True
                self.stable_weight = avg

                # Check if weight changed from last stable state
                weight_change = self.stable_weight - self.last_stable_weight

                if abs(weight_change) > self.weight_tolerance:
                    # Significant change detected
                    self.on_weight_change(weight_change)
                    self.last_stable_weight = self.stable_weight

                self.stability_label.setText(f"상태: 안정 ({self.stable_weight:.1f}g)")
                self.stability_label.setStyleSheet("color: green; padding: 10px; font-weight: bold;")
        else:
            # Not stable
            if self.is_stable:
                # Transition from stable to unstable
                self.is_stable = False
                self.stability_label.setText("상태: 변화 감지 중...")
                self.stability_label.setStyleSheet("color: orange; padding: 10px;")

    def on_weight_change(self, change):
        """
        무게 변화 감지 시 호출
        change > 0: 상품 추가
        change < 0: 상품 제거
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if change > 0:
            # Product added
            message = f"✓ {abs(change):.1f}g 추가"
            self.log_change(message, "green")

            # Save to file
            self.save_product_log(f"id.{self.product_id}", abs(change))
            self.product_id += 1

        else:
            # Product removed
            message = f"✗ {abs(change):.1f}g 제거"
            self.log_change(message, "red")

            # Save to file (optional: you can skip this for removals)
            # For now, we'll log removals too
            self.save_product_log(f"id.{self.product_id}", abs(change), removed=True)
            self.product_id += 1

    def log_change(self, message, color):
        """Display change in the change display area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        html = f'<span style="color: {color}; font-weight: bold;">[{timestamp}] {message}</span><br>'
        self.change_display.append(html)

        # Auto-scroll
        scrollbar = self.change_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def save_product_log(self, product_id, weight, removed=False):
        """Save product log to txt file"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                action = "제거" if removed else "추가"
                f.write(f"{product_id} {weight:.1f}g ({action}) - {timestamp}\n")

            # Reload display
            self.load_product_log()

        except Exception as e:
            QMessageBox.warning(self, "로그 저장 오류", f"파일 저장 실패: {e}")

    def load_product_log(self):
        """Load and display product log from txt file"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.product_log_display.setPlainText(content)

            # Auto-scroll to bottom
            scrollbar = self.product_log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

        except FileNotFoundError:
            # File doesn't exist yet
            self.product_log_display.setPlainText("(기록 없음)")
        except Exception as e:
            self.product_log_display.setPlainText(f"로그 로드 오류: {e}")

    def reset_log(self):
        """Reset product log"""
        reply = QMessageBox.question(
            self,
            "기록 초기화",
            "모든 상품 기록을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Clear file
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write("")

                # Reset ID
                self.product_id = 1

                # Clear displays
                self.product_log_display.setPlainText("(기록 없음)")
                self.change_display.clear()

                # Reset tracking
                self.last_stable_weight = self.stable_weight

                QMessageBox.information(self, "완료", "기록이 초기화되었습니다.")

            except Exception as e:
                QMessageBox.warning(self, "오류", f"초기화 실패: {e}")

    def calibrate_zero(self):
        """Zero calibration"""
        self.zero_offset = self.raw_weight

        # Reset tracking
        self.last_stable_weight = 0.0
        self.stable_weight = 0.0
        self.weight_history.clear()
        self.is_stable = False

        QMessageBox.information(
            self,
            "영점 조절 완료",
            f"영점이 설정되었습니다.\n센서값: {self.raw_weight:.1f}g"
        )

    def calibrate_weight(self):
        """Weight calibration"""
        from PyQt5.QtWidgets import QInputDialog

        current_weight = self.current_weight

        known_weight, ok = QInputDialog.getDouble(
            self,
            "무게 교정",
            f"현재 표시 무게: {current_weight:.1f}g\n\n실제 무게를 입력하세요 (g):",
            current_weight,
            0.0,
            10000.0,
            1
        )

        if ok and abs(current_weight) > 0.1:
            factor = known_weight / current_weight
            self.calibration_factor *= factor

            # Reset tracking after calibration
            self.weight_history.clear()
            self.is_stable = False

            QMessageBox.information(
                self,
                "무게 교정 완료",
                f"교정이 완료되었습니다.\n교정 계수: {self.calibration_factor:.4f}"
            )

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_0:
            self.calibrate_zero()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        if self.is_connected:
            self.serial.disconnect()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ProductClassifier()
    window.show()
    sys.exit(app.exec_())
