"""
Load Cell Serial Communication Protocol Module
Based on the original VB.NET implementation
"""

class LoadCellProtocol:
    """Handles load cell serial communication protocol"""

    # Function codes
    FUNC_READ = 0x05
    FUNC_WRITE = 0x63

    # Registers
    REG_ID_READ = 0x05
    REG_WEIGHT_READ = 0x02
    REG_PARAM = 0x23
    REG_ADDRESS = 0x10
    REG_ZERO_SET = 0x06

    # Constants
    BROADCAST_ADDR = 0x00
    CONST_VALUE = 0x05
    ZERO_SET_VALUE = 0x03

    # Resolution table (in grams)
    RESOLUTION_TABLE = [
        0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50,
        100, 200, 500, 1000, 2000, 5000
    ]

    # Max weight table (in kg)
    MAX_WEIGHT_TABLE = [
        5, 10, 15, 20, 25, 30, 35, 40, 45, 50,
        55, 60, 65, 70, 75, 80, 85, 90, 95, 100
    ]

    # Scale type names
    SCALE_TYPES = [
        "쾌속측정",      # Quick measurement
        "보통측정",      # Normal measurement
        "crane 측정",    # Crane measurement
        "대형 crane 측정" # Large crane measurement
    ]

    @staticmethod
    def calculate_checksum(data):
        """Calculate checksum as sum of all bytes & 0xFF"""
        return sum(data) & 0xFF

    @staticmethod
    def create_id_read_command():
        """Create command to read load cell ID"""
        cmd = [
            LoadCellProtocol.BROADCAST_ADDR,
            LoadCellProtocol.FUNC_READ,
            LoadCellProtocol.REG_ID_READ,
            LoadCellProtocol.CONST_VALUE
        ]
        cmd.append(LoadCellProtocol.calculate_checksum(cmd))
        return bytes(cmd)

    @staticmethod
    def create_weight_read_command():
        """Create command to read weight"""
        cmd = [
            LoadCellProtocol.BROADCAST_ADDR,
            LoadCellProtocol.FUNC_READ,
            LoadCellProtocol.REG_WEIGHT_READ,
            LoadCellProtocol.CONST_VALUE
        ]
        cmd.append(LoadCellProtocol.calculate_checksum(cmd))
        return bytes(cmd)

    @staticmethod
    def create_param_read_command():
        """Create command to read parameters"""
        cmd = [
            LoadCellProtocol.BROADCAST_ADDR,
            LoadCellProtocol.FUNC_READ,
            LoadCellProtocol.REG_PARAM,
            LoadCellProtocol.CONST_VALUE
        ]
        cmd.append(LoadCellProtocol.calculate_checksum(cmd))
        return bytes(cmd)

    @staticmethod
    def create_address_change_command(new_address):
        """Create command to change load cell address (1-10)"""
        cmd = [
            LoadCellProtocol.BROADCAST_ADDR,
            LoadCellProtocol.FUNC_WRITE,
            LoadCellProtocol.REG_ADDRESS,
            new_address
        ]
        cmd.append(LoadCellProtocol.calculate_checksum(cmd))
        return bytes(cmd)

    @staticmethod
    def create_zero_set_command():
        """Create command to set zero"""
        cmd = [
            LoadCellProtocol.BROADCAST_ADDR,
            LoadCellProtocol.FUNC_WRITE,
            LoadCellProtocol.REG_ZERO_SET,
            LoadCellProtocol.ZERO_SET_VALUE
        ]
        cmd.append(LoadCellProtocol.calculate_checksum(cmd))
        return bytes(cmd)

    @staticmethod
    def create_param_write_command(max_weight_idx, division_idx, zero_range_idx,
                                   down_range_idx, kind_idx):
        """
        Create command to write parameters

        Args:
            max_weight_idx: Index in MAX_WEIGHT_TABLE (0-14)
            division_idx: Index in RESOLUTION_TABLE (0-14)
            zero_range_idx: Zero range 0-9
            down_range_idx: Settling zero range 1-10
            kind_idx: Scale type index (0-3)
        """
        cmd = [
            LoadCellProtocol.BROADCAST_ADDR,
            LoadCellProtocol.FUNC_WRITE,
            LoadCellProtocol.REG_PARAM,
            max_weight_idx,
            division_idx,
            zero_range_idx,
            down_range_idx,
            kind_idx
        ]
        cmd.append(LoadCellProtocol.calculate_checksum(cmd))
        return bytes(cmd)

    @staticmethod
    def parse_id_response(data):
        """
        Parse ID read response

        Returns:
            dict with 'address', 'id0', 'id1', 'id2', 'id3' or None if invalid
        """
        if len(data) < 11 or data[2] != LoadCellProtocol.REG_ID_READ:
            return None

        return {
            'address': data[0],
            'id0': data[7],
            'id1': data[8],
            'id2': data[9],
            'id3': data[10]
        }

    @staticmethod
    def parse_weight_response(data):
        """
        Parse weight read response

        Returns:
            dict with 'status', 'division', 'raw_weight', 'weight' or None if invalid
        """
        if len(data) < 8 or data[2] != LoadCellProtocol.REG_WEIGHT_READ:
            return None

        status = data[3]
        division = data[4] & 0x0F

        # Raw weight is 3 bytes in format: [high] [mid] [low]
        # Each byte is in hex format (0x00-0xFF)
        raw_weight = (data[5] * 0x100) + (data[6] * 0x10) + data[7]

        # Get resolution from table
        if division < len(LoadCellProtocol.RESOLUTION_TABLE):
            resolution = LoadCellProtocol.RESOLUTION_TABLE[division]
        else:
            resolution = 1

        # Calculate actual weight
        weight = resolution * raw_weight

        # Check sign bit (bit 7 of data[4])
        # if data[4] & 0x80:
        #     weight = -weight

        return {
            'status': status,
            'division': division,
            'raw_weight': raw_weight,
            'weight': weight,
            'resolution': resolution
        }

    @staticmethod
    def parse_param_response(data):
        """
        Parse parameter read response

        Returns:
            dict with parameter information or None if invalid
        """
        if len(data) < 8 or data[2] != LoadCellProtocol.REG_PARAM:
            return None

        division_idx = (data[3] & 0xF0) >> 4
        kind_idx = data[3] & 0x0F
        zero_range = (data[4] & 0xF0) >> 4
        down_range = data[4] & 0x0F

        # Max weight is 3 bytes
        max_weight_raw = (data[5] * 0x10000) + (data[6] * 0x100) + data[7]

        if division_idx < len(LoadCellProtocol.RESOLUTION_TABLE):
            resolution = LoadCellProtocol.RESOLUTION_TABLE[division_idx]
            max_weight = max_weight_raw * resolution
        else:
            resolution = 1
            max_weight = max_weight_raw

        if kind_idx < len(LoadCellProtocol.SCALE_TYPES):
            kind_name = LoadCellProtocol.SCALE_TYPES[kind_idx]
        else:
            kind_name = "Unknown"

        return {
            'division_idx': division_idx,
            'resolution': resolution,
            'zero_range': zero_range,
            'down_range': down_range,
            'kind_idx': kind_idx,
            'kind_name': kind_name,
            'max_weight': max_weight
        }

    @staticmethod
    def parse_status_flags(status):
        """
        Parse status byte into individual flags

        Returns:
            dict with boolean flags
        """
        return {
            'zero_error': bool(status & 0x01),
            'error': bool(status & 0x02),
            'overload': bool(status & 0x04),
            'zero_adjusted': bool(status & 0x08),
            'calibration_needed': bool(status & 0x10)
        }
