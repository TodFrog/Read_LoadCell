"""
Load Cell Reader GUI Application
PyQt5-based GUI matching the original VB.NET interface
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QComboBox, QPushButton, QTextEdit, QLineEdit,
    QRadioButton, QButtonGroup, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont
from loadcell_serial import LoadCellSerial
from loadcell_protocol import LoadCellProtocol


class LoadCellGUI(QMainWindow):
    """Main application window"""

    # Signals for thread-safe GUI updates
    data_received_signal = pyqtSignal(bytes)
    connection_changed_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.serial = LoadCellSerial()
        self.serial.on_data_received = self.on_serial_data
        self.serial.on_connection_changed = self.on_connection_changed

        # Connect signals
        self.data_received_signal.connect(self.update_rx_display)
        self.connection_changed_signal.connect(self.update_connection_status)

        # Initialize UI
        self.init_ui()

        # Timer for periodic updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(500)  # 500ms interval

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle('Load Cell Reader')
        self.setGeometry(100, 100, 850, 550)

        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # Left panel
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)

        # Right panel (Load Cell 1)
        right_panel = self.create_loadcell_panel()
        main_layout.addWidget(right_panel)

    def create_left_panel(self):
        """Create left control panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Communication settings group
        comm_group = QGroupBox("통신설정")
        comm_layout = QVBoxLayout()

        # Port selection
        port_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.refresh_ports()
        port_layout.addWidget(self.port_combo)
        port_label = QLabel("통신포트")
        port_layout.addWidget(port_label)
        comm_layout.addLayout(port_layout)

        # Connect/Disconnect buttons
        btn_layout = QHBoxLayout()
        self.btn_connect = QPushButton("열기")
        self.btn_connect.clicked.connect(self.on_connect)
        btn_layout.addWidget(self.btn_connect)

        self.btn_disconnect = QPushButton("닫기")
        self.btn_disconnect.clicked.connect(self.on_disconnect)
        self.btn_disconnect.setEnabled(False)
        btn_layout.addWidget(self.btn_disconnect)
        comm_layout.addLayout(btn_layout)

        comm_group.setLayout(comm_layout)
        layout.addWidget(comm_group)

        # Control buttons
        self.btn_read_id = QPushButton("id읽기")
        self.btn_read_id.clicked.connect(self.on_read_id)
        layout.addWidget(self.btn_read_id)

        self.btn_read_param = QPushButton("param읽기")
        self.btn_read_param.clicked.connect(self.on_read_param)
        layout.addWidget(self.btn_read_param)

        self.btn_zero = QPushButton("영점조정")
        self.btn_zero.clicked.connect(self.on_zero_set)
        layout.addWidget(self.btn_zero)

        self.btn_read_weight = QPushButton("중량읽기")
        self.btn_read_weight.clicked.connect(self.on_read_weight)
        layout.addWidget(self.btn_read_weight)

        layout.addStretch()
        return panel

    def create_loadcell_panel(self):
        """Create load cell display panel"""
        panel = QGroupBox("로드셀1")
        panel_font = QFont()
        panel_font.setPointSize(14)
        panel.setFont(panel_font)

        layout = QVBoxLayout()

        # Top section: Address change
        addr_layout = QHBoxLayout()
        self.addr_combo = QComboBox()
        for i in range(1, 11):
            self.addr_combo.addItem(str(i))
        addr_layout.addWidget(self.addr_combo)

        self.btn_addr_change = QPushButton("주소변경")
        self.btn_addr_change.clicked.connect(self.on_address_change)
        addr_layout.addWidget(self.btn_addr_change)
        addr_layout.addStretch()
        layout.addLayout(addr_layout)

        # Weight display
        weight_layout = QHBoxLayout()
        self.weight_display = QLineEdit()
        self.weight_display.setReadOnly(True)
        weight_font = QFont()
        weight_font.setPointSize(24)
        self.weight_display.setFont(weight_font)
        self.weight_display.setAlignment(Qt.AlignRight)
        weight_layout.addWidget(self.weight_display)

        weight_label = QLabel("gr")
        weight_label.setFont(panel_font)
        weight_layout.addWidget(weight_label)
        layout.addLayout(weight_layout)

        # Middle section: Parameters and ID side by side
        middle_layout = QHBoxLayout()

        # Parameter configuration group
        param_config = self.create_param_config_group()
        middle_layout.addWidget(param_config)

        # Status group
        status_group = self.create_status_group()
        middle_layout.addWidget(status_group)

        layout.addLayout(middle_layout)

        # Bottom section: Parameter display, ID, and Address
        bottom_layout = QHBoxLayout()

        # Parameter display
        param_display = self.create_param_display_group()
        bottom_layout.addWidget(param_display)

        # ID display
        id_display = self.create_id_display_group()
        bottom_layout.addWidget(id_display)

        # Address display
        addr_display = self.create_address_display_group()
        bottom_layout.addWidget(addr_display)

        layout.addLayout(bottom_layout)

        # TX/RX data display
        data_layout = QVBoxLayout()

        tx_layout = QHBoxLayout()
        tx_label = QLabel("송신데이터")
        tx_layout.addWidget(tx_label)
        self.tx_display = QTextEdit()
        self.tx_display.setMaximumHeight(30)
        self.tx_display.setReadOnly(True)
        tx_layout.addWidget(self.tx_display)
        data_layout.addLayout(tx_layout)

        rx_layout = QHBoxLayout()
        rx_label = QLabel("수신데이터")
        rx_layout.addWidget(rx_label)
        self.rx_display = QTextEdit()
        self.rx_display.setMaximumHeight(80)
        self.rx_display.setReadOnly(True)
        rx_layout.addWidget(self.rx_display)
        data_layout.addLayout(rx_layout)

        layout.addLayout(data_layout)

        panel.setLayout(layout)
        return panel

    def create_param_config_group(self):
        """Create parameter configuration group"""
        group = QGroupBox("파라미터 변경")
        group_font = QFont()
        group_font.setPointSize(10)
        group.setFont(group_font)

        layout = QGridLayout()

        # Max weight
        layout.addWidget(QLabel("최대중량값(kg)"), 0, 0)
        self.combo_max_weight = QComboBox()
        for weight in LoadCellProtocol.MAX_WEIGHT_TABLE[:15]:
            self.combo_max_weight.addItem(str(weight))
        layout.addWidget(self.combo_max_weight, 0, 1)

        # Division
        layout.addWidget(QLabel("분해도"), 1, 0)
        self.combo_division = QComboBox()
        division_labels = [
            "0(0.0001)", "1(0.0002)", "2(0.0005)", "3(0.001)",
            "4(0.002)", "5(0.005)", "6(0.01)", "7(0.02)",
            "8(0.05)", "9(0.1)", "A(0.2)", "B(0.5)",
            "C(1.0)", "D(2.0)", "E(5.0)"
        ]
        for label in division_labels:
            self.combo_division.addItem(label)
        layout.addWidget(self.combo_division, 1, 1)

        # Zero range
        layout.addWidget(QLabel("영점범위(%)"), 2, 0)
        self.combo_zero_range = QComboBox()
        for i in range(10):
            self.combo_zero_range.addItem(str(i))
        layout.addWidget(self.combo_zero_range, 2, 1)

        # Settling zero range
        layout.addWidget(QLabel("안착영점범위(%)"), 3, 0)
        self.combo_down_range = QComboBox()
        for i in range(1, 11):
            self.combo_down_range.addItem(str(i))
        layout.addWidget(self.combo_down_range, 3, 1)

        # Scale type
        layout.addWidget(QLabel("저울종류"), 4, 0)
        self.combo_kind = QComboBox()
        for kind in LoadCellProtocol.SCALE_TYPES:
            self.combo_kind.addItem(kind)
        layout.addWidget(self.combo_kind, 4, 1)

        # Write button
        self.btn_param_write = QPushButton("변경")
        btn_font = QFont()
        btn_font.setPointSize(12)
        btn_font.setBold(True)
        self.btn_param_write.setFont(btn_font)
        self.btn_param_write.clicked.connect(self.on_param_write)
        layout.addWidget(self.btn_param_write, 5, 0, 1, 2)

        group.setLayout(layout)
        return group

    def create_status_group(self):
        """Create status indicator group"""
        group = QGroupBox("상태")
        group_font = QFont()
        group_font.setPointSize(10)
        group.setFont(group_font)

        layout = QVBoxLayout()

        self.status_ok = QRadioButton("정상")
        self.status_error = QRadioButton("에러")
        self.status_overload = QRadioButton("과중량")
        self.status_zero_adjusted = QRadioButton("영점조정됨")
        self.status_cal_needed = QRadioButton("조정필요")

        layout.addWidget(self.status_ok)
        layout.addWidget(self.status_error)
        layout.addWidget(self.status_overload)
        layout.addWidget(self.status_zero_adjusted)
        layout.addWidget(self.status_cal_needed)

        group.setLayout(layout)
        return group

    def create_param_display_group(self):
        """Create parameter display group"""
        group = QGroupBox("parameter")
        group_font = QFont()
        group_font.setPointSize(10)
        group.setFont(group_font)

        layout = QGridLayout()

        layout.addWidget(QLabel("최대중량값(kg)"), 0, 0)
        self.label_max_weight = QLabel("xx")
        layout.addWidget(self.label_max_weight, 0, 1)

        layout.addWidget(QLabel("분해도"), 1, 0)
        self.label_division = QLabel("xx")
        layout.addWidget(self.label_division, 1, 1)

        layout.addWidget(QLabel("ad값"), 1, 2)
        self.label_ad_value = QLabel("xx")
        layout.addWidget(self.label_ad_value, 1, 3)

        layout.addWidget(QLabel("영점범위(%)"), 2, 0)
        self.label_zero_range = QLabel("xx")
        layout.addWidget(self.label_zero_range, 2, 1)

        layout.addWidget(QLabel("안착 영점범위(%)"), 2, 2)
        self.label_down_zero = QLabel("xx")
        layout.addWidget(self.label_down_zero, 2, 3)

        layout.addWidget(QLabel("저울종류"), 0, 2)
        self.label_kind = QLabel("xx")
        layout.addWidget(self.label_kind, 0, 3)

        group.setLayout(layout)
        return group

    def create_id_display_group(self):
        """Create ID display group"""
        group = QGroupBox("고유id")
        group_font = QFont()
        group_font.setPointSize(10)
        group.setFont(group_font)

        layout = QGridLayout()

        layout.addWidget(QLabel("id0"), 0, 0)
        self.label_id0 = QLabel("xx")
        layout.addWidget(self.label_id0, 0, 1)

        layout.addWidget(QLabel("id1"), 1, 0)
        self.label_id1 = QLabel("xx")
        layout.addWidget(self.label_id1, 1, 1)

        layout.addWidget(QLabel("id2"), 2, 0)
        self.label_id2 = QLabel("xx")
        layout.addWidget(self.label_id2, 2, 1)

        layout.addWidget(QLabel("id3"), 3, 0)
        self.label_id3 = QLabel("xx")
        layout.addWidget(self.label_id3, 3, 1)

        group.setLayout(layout)
        return group

    def create_address_display_group(self):
        """Create address display group"""
        group = QGroupBox("주소(adr)")
        group_font = QFont()
        group_font.setPointSize(10)
        group.setFont(group_font)

        layout = QVBoxLayout()

        self.label_address = QLabel("xx")
        addr_font = QFont()
        addr_font.setPointSize(20)
        addr_font.setBold(True)
        self.label_address.setFont(addr_font)
        layout.addWidget(self.label_address)

        group.setLayout(layout)
        return group

    def refresh_ports(self):
        """Refresh available serial ports"""
        self.port_combo.clear()
        ports = LoadCellSerial.list_ports()
        for port, desc in ports:
            self.port_combo.addItem(f"{port} - {desc}", port)

    def on_connect(self):
        """Connect to serial port"""
        if self.port_combo.count() == 0:
            return

        port = self.port_combo.currentData()
        if not port:
            port = self.port_combo.currentText().split(' ')[0]

        if self.serial.connect(port):
            self.btn_connect.setEnabled(False)
            self.btn_disconnect.setEnabled(True)

    def on_disconnect(self):
        """Disconnect from serial port"""
        self.serial.disconnect()
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)

    def on_read_id(self):
        """Read load cell ID"""
        self.clear_displays(['id'])
        cmd = LoadCellProtocol.create_id_read_command()
        self.show_tx_data(cmd)
        self.serial.send_command(cmd)

    def on_read_param(self):
        """Read parameters"""
        self.clear_displays(['param'])
        cmd = LoadCellProtocol.create_param_read_command()
        self.show_tx_data(cmd)
        self.serial.send_command(cmd)

    def on_zero_set(self):
        """Set zero point"""
        cmd = LoadCellProtocol.create_zero_set_command()
        self.show_tx_data(cmd)
        self.serial.send_command(cmd)

    def on_read_weight(self):
        """Read weight"""
        self.clear_displays(['weight'])
        cmd = LoadCellProtocol.create_weight_read_command()
        self.show_tx_data(cmd)
        self.serial.send_command(cmd)

    def on_address_change(self):
        """Change load cell address"""
        new_addr = int(self.addr_combo.currentText())
        self.clear_displays(['address'])
        cmd = LoadCellProtocol.create_address_change_command(new_addr)
        self.show_tx_data(cmd)
        self.serial.send_command(cmd)

    def on_param_write(self):
        """Write parameters"""
        max_weight_idx = self.combo_max_weight.currentIndex()
        division_idx = self.combo_division.currentIndex()
        zero_range_idx = self.combo_zero_range.currentIndex()
        down_range_idx = self.combo_down_range.currentIndex()
        kind_idx = self.combo_kind.currentIndex()

        self.clear_displays(['param'])
        cmd = LoadCellProtocol.create_param_write_command(
            max_weight_idx, division_idx, zero_range_idx,
            down_range_idx, kind_idx
        )
        self.show_tx_data(cmd)
        self.serial.send_command(cmd)

    def clear_displays(self, display_types):
        """Clear specified display fields"""
        if 'id' in display_types:
            self.label_id0.setText("xx")
            self.label_id1.setText("xx")
            self.label_id2.setText("xx")
            self.label_id3.setText("xx")

        if 'address' in display_types:
            self.label_address.setText("xx")

        if 'weight' in display_types:
            self.weight_display.clear()
            self.label_division.setText("xx")
            self.label_ad_value.setText("xx")

        if 'param' in display_types:
            self.label_max_weight.setText("xx")
            self.label_division.setText("xx")
            self.label_zero_range.setText("xx")
            self.label_down_zero.setText("xx")
            self.label_kind.setText("xx")

        self.tx_display.clear()
        self.rx_display.clear()

    def on_serial_data(self, data):
        """Callback when serial data is received"""
        # Emit signal for thread-safe GUI update
        self.data_received_signal.emit(data)

    def on_connection_changed(self, connected):
        """Callback when connection status changes"""
        self.connection_changed_signal.emit(connected)

    def update_rx_display(self, data):
        """Update RX display with received data"""
        hex_str = ' '.join([f'{b:02X}' for b in data])
        self.rx_display.append(hex_str + ' ')

        # Parse received data
        rx_buffer = self.serial.get_rx_buffer()

        # Try to parse as ID response
        id_data = LoadCellProtocol.parse_id_response(rx_buffer)
        if id_data:
            self.label_id0.setText(f"{id_data['id0']:02X}")
            self.label_id1.setText(f"{id_data['id1']:02X}")
            self.label_id2.setText(f"{id_data['id2']:02X}")
            self.label_id3.setText(f"{id_data['id3']:02X}")
            self.label_address.setText(f"{id_data['address']:02X}")

        # Try to parse as weight response
        weight_data = LoadCellProtocol.parse_weight_response(rx_buffer)
        if weight_data:
            self.weight_display.setText(f"{weight_data['weight']:.1f}")
            self.label_division.setText(f"{weight_data['division']:X}")
            self.label_ad_value.setText(f"{weight_data['raw_weight']:X}")

            # Update status
            status_flags = LoadCellProtocol.parse_status_flags(weight_data['status'])
            self.status_ok.setChecked(not any(status_flags.values()))
            self.status_error.setChecked(status_flags['error'])
            self.status_overload.setChecked(status_flags['overload'])
            self.status_zero_adjusted.setChecked(status_flags['zero_adjusted'])
            self.status_cal_needed.setChecked(status_flags['calibration_needed'])

        # Try to parse as parameter response
        param_data = LoadCellProtocol.parse_param_response(rx_buffer)
        if param_data:
            self.label_max_weight.setText(f"{param_data['max_weight']:.1f}")
            self.label_division.setText(f"{param_data['resolution']}")
            self.label_zero_range.setText(f"{param_data['zero_range']}")
            self.label_down_zero.setText(f"{param_data['down_range']}")
            self.label_kind.setText(param_data['kind_name'])

    def update_connection_status(self, connected):
        """Update GUI based on connection status"""
        # This can be used to update status bar or indicators
        pass

    def on_timer(self):
        """Periodic timer callback"""
        # Can be used for periodic weight reading if needed
        pass

    def show_tx_data(self, data):
        """Display transmitted data"""
        hex_str = ' '.join([f'{b:02X}' for b in data])
        self.tx_display.setText(hex_str)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = LoadCellGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
