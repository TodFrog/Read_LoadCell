#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Load Cell Protocol
Run this to verify protocol implementation
"""

import sys
import io

# Fix for Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from loadcell_protocol import LoadCellProtocol


def test_checksum():
    """Test checksum calculation"""
    print("Testing checksum calculation...")
    data = [0x00, 0x05, 0x05, 0x05]
    checksum = LoadCellProtocol.calculate_checksum(data)
    print(f"  Data: {[hex(b) for b in data]}")
    print(f"  Checksum: {hex(checksum)}")
    assert checksum == 0x0F, f"Expected 0x0F, got {hex(checksum)}"
    print("  ✓ Checksum test passed")


def test_id_read_command():
    """Test ID read command creation"""
    print("\nTesting ID read command...")
    cmd = LoadCellProtocol.create_id_read_command()
    print(f"  Command: {' '.join([f'{b:02X}' for b in cmd])}")
    expected = bytes([0x00, 0x05, 0x05, 0x05, 0x0F])
    assert cmd == expected, f"Expected {expected.hex()}, got {cmd.hex()}"
    print("  ✓ ID read command test passed")


def test_weight_read_command():
    """Test weight read command creation"""
    print("\nTesting weight read command...")
    cmd = LoadCellProtocol.create_weight_read_command()
    print(f"  Command: {' '.join([f'{b:02X}' for b in cmd])}")
    expected = bytes([0x00, 0x05, 0x02, 0x05, 0x0C])
    assert cmd == expected, f"Expected {expected.hex()}, got {cmd.hex()}"
    print("  ✓ Weight read command test passed")


def test_address_change_command():
    """Test address change command creation"""
    print("\nTesting address change command...")
    cmd = LoadCellProtocol.create_address_change_command(5)
    print(f"  Command (address=5): {' '.join([f'{b:02X}' for b in cmd])}")
    expected = bytes([0x00, 0x63, 0x10, 0x05, 0x78])
    assert cmd == expected, f"Expected {expected.hex()}, got {cmd.hex()}"
    print("  ✓ Address change command test passed")


def test_zero_set_command():
    """Test zero set command creation"""
    print("\nTesting zero set command...")
    cmd = LoadCellProtocol.create_zero_set_command()
    print(f"  Command: {' '.join([f'{b:02X}' for b in cmd])}")
    expected = bytes([0x00, 0x63, 0x06, 0x03, 0x6C])
    assert cmd == expected, f"Expected {expected.hex()}, got {cmd.hex()}"
    print("  ✓ Zero set command test passed")


def test_parse_id_response():
    """Test parsing ID response"""
    print("\nTesting ID response parsing...")
    # Simulated response: address=1, func=5, reg=5, data..., id0=0x12, id1=0x34, id2=0x56, id3=0x78
    response = bytes([0x01, 0x05, 0x05, 0x00, 0x00, 0x00, 0x00, 0x12, 0x34, 0x56, 0x78])
    result = LoadCellProtocol.parse_id_response(response)
    print(f"  Response: {' '.join([f'{b:02X}' for b in response])}")
    print(f"  Parsed: {result}")
    assert result is not None, "Failed to parse response"
    assert result['address'] == 0x01
    assert result['id0'] == 0x12
    assert result['id1'] == 0x34
    assert result['id2'] == 0x56
    assert result['id3'] == 0x78
    print("  ✓ ID response parsing test passed")


def test_parse_weight_response():
    """Test parsing weight response"""
    print("\nTesting weight response parsing...")
    # Simulated response: addr=1, func=5, reg=2, status=0, division=9(100g), weight bytes: 01 02 03
    # raw_weight = 0x01*0x100 + 0x02*0x10 + 0x03 = 256 + 32 + 3 = 291
    # Expected weight: 100g * 291 = 29100g
    response = bytes([0x01, 0x05, 0x02, 0x00, 0x09, 0x01, 0x02, 0x03])
    result = LoadCellProtocol.parse_weight_response(response)
    print(f"  Response: {' '.join([f'{b:02X}' for b in response])}")
    print(f"  Parsed: {result}")
    assert result is not None, "Failed to parse response"
    assert result['division'] == 9
    assert result['resolution'] == 100  # Index 9 in resolution table is 100g
    assert result['raw_weight'] == 291
    assert result['weight'] == 29100  # 100 * 291
    print("  ✓ Weight response parsing test passed")


def test_parse_status_flags():
    """Test status flag parsing"""
    print("\nTesting status flag parsing...")
    # Status with zero_error and overload flags set
    status = 0x05  # binary: 00000101
    flags = LoadCellProtocol.parse_status_flags(status)
    print(f"  Status byte: {hex(status)} ({bin(status)})")
    print(f"  Flags: {flags}")
    assert flags['zero_error'] == True
    assert flags['error'] == False
    assert flags['overload'] == True
    assert flags['zero_adjusted'] == False
    assert flags['calibration_needed'] == False
    print("  ✓ Status flag parsing test passed")


def test_resolution_table():
    """Test resolution table access"""
    print("\nTesting resolution table...")
    print(f"  Resolution table has {len(LoadCellProtocol.RESOLUTION_TABLE)} entries")
    assert len(LoadCellProtocol.RESOLUTION_TABLE) == 15
    assert LoadCellProtocol.RESOLUTION_TABLE[0] == 0.1
    assert LoadCellProtocol.RESOLUTION_TABLE[9] == 100
    assert LoadCellProtocol.RESOLUTION_TABLE[14] == 5000
    print(f"  Sample resolutions: {LoadCellProtocol.RESOLUTION_TABLE[:5]}")
    print("  ✓ Resolution table test passed")


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("Load Cell Protocol Test Suite")
    print("="*60)

    try:
        test_checksum()
        test_id_read_command()
        test_weight_read_command()
        test_address_change_command()
        test_zero_set_command()
        test_parse_id_response()
        test_parse_weight_response()
        test_parse_status_flags()
        test_resolution_table()

        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60)
        return True

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
