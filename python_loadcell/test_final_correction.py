#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test final linear correction formula
Based on 499g calibration data
"""

def apply_correction(measured):
    """Apply linear correction"""
    slope = 0.990527
    intercept = -2.990644
    return slope * measured + intercept


def main():
    print("="*70)
    print("최종 선형 보정 테스트 (499g 교정 기준)")
    print("="*70)
    print()

    # Calibration data (after 499g calibration)
    test_data = [
        (139, 150.5, "139g 물체"),
        (126, 136.1, "126g 물체"),
        (68, 66, "68g 물체"),
        (176, 204.1, "176g 물체"),
        (51, 43.3, "51g 물체"),
        (77, 72.2, "77g 물체"),
        (483, 478.4, "483g 물체"),
        (537, 546.4, "537g 물체"),
    ]

    print("보정 공식: actual = 0.990527 * measured + (-2.990644)")
    print()
    print("-"*70)
    print(f"{'설명':<15} {'실제(g)':>10} {'측정(g)':>10} {'보정후(g)':>12} {'오차(g)':>10}")
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

    # Test negative values
    print("="*70)
    print("음수 값 테스트 (20g 미만 물체)")
    print("="*70)
    print()
    print(f"{'측정값(g)':>12} {'보정후(g)':>15}")
    print("-"*70)

    test_small = [-5, -2, 0, 1, 5, 10, 15, 20]
    for val in test_small:
        corrected = apply_correction(val)
        print(f"{val:>12.1f} {corrected:>15.1f}")

    print()
    print("-> 음수 값이 정상적으로 표시됩니다!")
    print()

    # Test zero calibration scenario
    print("="*70)
    print("영점 조절 시나리오")
    print("="*70)
    print()

    print("1. 빈 상태 (센서 읽음: -1.5g):")
    raw_empty = -1.5
    print(f"   영점 저장: {raw_empty:.1f}g")
    print()

    print("2. 51g 물체 올림 (센서 읽음: 43.3g, 교정 전):")
    raw_51g = 43.3
    zeroed_51g = raw_51g - raw_empty
    corrected_51g = apply_correction(zeroed_51g)
    print(f"   센서 raw: {raw_51g:.1f}g")
    print(f"   영점 차감: {zeroed_51g:.1f}g")
    print(f"   보정 후: {corrected_51g:.1f}g")
    print()

    print("3. 무게 교정 (51g 입력):")
    calibration_factor = 51.0 / corrected_51g
    print(f"   교정 계수: {calibration_factor:.4f}")
    final_51g = corrected_51g * calibration_factor
    print(f"   최종 표시: {final_51g:.1f}g (51g이어야 함)")
    print()

    print("4. 537g 물체 테스트:")
    raw_537g = 546.4
    zeroed_537g = raw_537g - raw_empty
    corrected_537g = apply_correction(zeroed_537g)
    final_537g = corrected_537g * calibration_factor
    print(f"   센서 raw: {raw_537g:.1f}g")
    print(f"   영점 차감: {zeroed_537g:.1f}g")
    print(f"   보정 후: {corrected_537g:.1f}g")
    print(f"   교정 적용: {final_537g:.1f}g")
    print(f"   실제: 537g (오차: {final_537g - 537:.1f}g)")
    print()

    print("="*70)


if __name__ == '__main__':
    main()
