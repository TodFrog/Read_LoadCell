#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test new nonlinear correction formula with updated calibration data
"""

def apply_correction(measured):
    """Apply 2nd order polynomial correction"""
    a = 0.002174112
    b = 0.381139
    c = 26.526635
    return a * (measured ** 2) + b * measured + c


def main():
    print("="*70)
    print("새로운 로드셀 보정 테스트")
    print("="*70)
    print()

    # New calibration data (excluding area-sensitive objects)
    test_data = [
        (67, 74.2, "67g 물체"),
        (643, 446.6, "643g 물체"),
        (126, 129.8, "126g 물체"),
        (482, 384.8, "482g 물체"),
        (271, 268.9, "271g 물체"),
        (29, 35.5, "29g 물체"),
        (139, 140.6, "139g 물체"),
    ]

    print("보정 공식: actual = 0.002174112 * measured^2 + 0.381139 * measured + 26.526635")
    print()
    print("-"*70)
    print(f"{'설명':<15} {'실제(g)':>10} {'센서(g)':>10} {'보정후(g)':>12} {'오차(g)':>10}")
    print("-"*70)

    errors = []
    for actual, measured, desc in test_data:
        corrected = apply_correction(measured)
        error = corrected - actual
        errors.append(error)

        print(f"{desc:<15} {actual:>10.1f} {measured:>10.1f} {corrected:>12.1f} {error:>+10.1f}")

    print("-"*70)

    # Calculate statistics
    import math
    rms_error = math.sqrt(sum(e**2 for e in errors) / len(errors))
    max_error = max(abs(e) for e in errors)
    avg_error = sum(errors) / len(errors)

    print()
    print("통계:")
    print(f"  RMS 오차:     {rms_error:.2f}g")
    print(f"  최대 절대오차: {max_error:.2f}g")
    print(f"  평균 오차:     {avg_error:+.2f}g")
    print()

    # Test zero calibration scenario
    print("="*70)
    print("영점 조절 시나리오 테스트")
    print("="*70)
    print()

    # Simulate: start at -1.4g raw reading
    print("1. 시작 상태 (빈 판):")
    raw_empty = -1.4
    corrected_empty = apply_correction(raw_empty)
    print(f"   센서 원본값: {raw_empty:.1f}g")
    print(f"   보정된 값: {corrected_empty:.1f}g")
    print()

    # User clicks "zero calibration"
    print("2. '영점 조절' 클릭:")
    zero_offset = corrected_empty
    print(f"   영점 저장: {zero_offset:.1f}g")
    print(f"   표시값: {corrected_empty - zero_offset:.1f}g (0g이 되어야 함)")
    print()

    # Place 17g object
    print("3. 17g 물체 올림:")
    raw_17g = 17.0  # Assuming sensor reads correctly at this point
    corrected_17g = apply_correction(raw_17g)
    displayed_17g = corrected_17g - zero_offset
    print(f"   센서 원본값: {raw_17g:.1f}g")
    print(f"   보정된 값: {corrected_17g:.1f}g")
    print(f"   영점 차감: {corrected_17g:.1f}g - {zero_offset:.1f}g")
    print(f"   표시값: {displayed_17g:.1f}g (17g에 가까워야 함)")
    print()

    print("="*70)


if __name__ == '__main__':
    main()
