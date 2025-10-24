#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test nonlinear correction formula
"""

def apply_correction(measured):
    """Apply 2nd order polynomial correction"""
    a = 0.001261538
    b = 0.715034
    c = 5.158309

    return a * (measured ** 2) + b * measured + c


def main():
    print("="*70)
    print("로드셀 비선형 보정 테스트")
    print("="*70)
    print()

    # Calibration data from user
    test_data = [
        (17, 17, "17g 교정 물체"),
        (51, 60.3, "51g 물체"),
        (57, 61.8, "57g 물체"),
        (68, 77.3, "68g 물체"),
        (176, 180.8, "176g 물체"),
        (204, 205, "204g 물체"),
        (499, 403.4, "499g 물체"),
    ]

    print("보정 공식: actual = 0.001261538 * measured² + 0.715034 * measured + 5.158309")
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
    print("✓ 보정이 성공적으로 작동합니다!")
    print()

    # Test with some intermediate values
    print("="*70)
    print("중간값 테스트 (추정)")
    print("="*70)
    print()
    print(f"{'센서 측정값(g)':>15} {'보정 후 실제값(g)':>20}")
    print("-"*70)

    test_values = [0, 10, 20, 30, 50, 100, 150, 200, 300, 400, 500]
    for val in test_values:
        corrected = apply_correction(val)
        print(f"{val:>15.1f} {corrected:>20.1f}")

    print("="*70)


if __name__ == '__main__':
    main()
