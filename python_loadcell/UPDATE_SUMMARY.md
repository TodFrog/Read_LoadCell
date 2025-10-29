# 업데이트 요약 (Update Summary)

## 주요 수정 사항 (Key Changes)

### 1. 9바이트 응답 형식 지원
**파일**: `loadcell_protocol.py`

- **이전**: 8바이트 응답만 처리 (2바이트 BCD 무게)
- **현재**: 9바이트 응답 처리 추가 (3바이트 HEX 무게)

**3바이트 HEX 무게 계산**:
```python
# Bytes 5, 6, 7 = 3바이트 HEX 값
raw_hex_value = (byte5 << 16) + (byte6 << 8) + byte7

# 무게 변환: ~5654 hex units = 1g (경험적 보정 계수)
weight = raw_hex_value / 565.4
```

**예시**:
- 12g: `00 C5 1A` = 50458 → 50458 / 565.4 ≈ 12g
- 15g: `01 07 5B` = 67419 → 67419 / 565.4 ≈ 15g
- 차이: 16961 (약 3g) → 3g당 ~5654 units

### 2. 고정값 문제 해결
**파일**: `simple_realtime.py`

- **이전**: 누적 오프셋 로직으로 인해 센서를 눌렀을 때 값이 고정됨
- **현재**: 누적 로직 제거, 직접 센서 읽기만 사용

**변경된 계산 방식**:
```python
# 이전 (문제 있음):
adjusted_raw = self.raw_weight + self.cumulative_offset

# 현재 (정상):
self.current_weight = (self.raw_weight - self.zero_offset) * self.calibration_factor
```

### 3. 듀얼 로드셀 디버깅 강화
**파일**: `dual_loadcell.py`

**주소 업데이트**:
```python
self.loadcell1_address = 0x03  # Load Cell #1
self.loadcell2_address = 0x4A  # Load Cell #2 (0x04에서 0x4A로 변경)
```

**강화된 디버그 메시지**:
```python
print(f"[DEBUG] Addr=0x{address:02X}, raw_val={raw_value}, weight={raw_weight:.1f}g")

if address == self.loadcell1_address:
    print(f"[DEBUG] -> Load Cell #1")
elif address == self.loadcell2_address:
    print(f"[DEBUG] -> Load Cell #2")
else:
    print(f"[DEBUG] Unknown address: 0x{address:02X}")
```

### 4. 체크섬 검증 임시 비활성화
**이유**: 9바이트 응답 형식 디버깅을 위해

**현재 상태**:
```python
# 체크섬 검증 TEMPORARILY DISABLED FOR DEBUGGING
# if len(rx_buffer) >= 8:
#     expected_checksum = sum(rx_buffer[:7]) & 0xFF
#     ...
```

**향후 계획**: 9바이트 응답이 정상 작동 확인 후 재활성화
```python
if len(rx_buffer) >= 9:
    expected_checksum = sum(rx_buffer[:8]) & 0xFF
    actual_checksum = rx_buffer[8]
```

## 테스트 방법 (How to Test)

### 단일 로드셀 테스트
```bash
cd python_loadcell
python simple_realtime.py
```

**확인 사항**:
1. 무게가 12g → 15g로 정상적으로 증가하는지
2. 센서를 눌렀다 떼면 값이 0으로 돌아가는지 (고정 안 됨)
3. 콘솔에 디버그 메시지 확인:
   ```
   [DEBUG] Full RX buffer (9 bytes): 03 06 02 42 00 00 C5 1A XX
   [DEBUG] Weight data: raw=50458, div=0, res=0.1g, status=0x42
   ```

### 듀얼 로드셀 테스트
```bash
cd python_loadcell
python dual_loadcell.py
```

**확인 사항**:
1. 콘솔에서 어떤 주소가 감지되는지 확인:
   ```
   [DEBUG] Addr=0x03, raw_val=50458, weight=12.0g
   [DEBUG] -> Load Cell #1

   [DEBUG] Addr=0x4A, raw_val=67419, weight=15.0g
   [DEBUG] -> Load Cell #2
   ```

2. 만약 "Unknown address" 메시지가 나오면:
   ```
   [DEBUG] Unknown address: 0x05 (expected 0x03 or 0x4A)
   ```
   → 실제 주소를 확인하고 코드 수정 필요

3. 좌우 패널에 각각의 로드셀 무게가 표시되는지 확인

## 예상되는 디버그 출력 (Expected Debug Output)

### 정상 동작 시:
```
[DEBUG] Full RX buffer (9 bytes): 03 06 02 42 00 00 C5 1A 2D
[DEBUG] Weight data: raw=50458, div=0, res=0.1g, status=0x42
[DEBUG] Addr=0x03, raw_val=50458, weight=89.3g
[DEBUG] -> Load Cell #1
```

### 비정상 동작 시:
```
[DEBUG] Full RX buffer (8 bytes): 03 06 02 42 00 00 C5 1A
[DEBUG] Incomplete buffer: 8 bytes - ...
```
→ 이 경우 8바이트 응답으로 처리됨 (BCD 방식)

## 주소 변경 방법 (How to Change Addresses)

만약 실제 로드셀 주소가 다르면:

**dual_loadcell.py** 수정 (45-50줄):
```python
# Load Cell 1 data (Address 3)
self.loadcell1_address = 0x??  # 실제 주소로 변경

# Load Cell 2 data (Address 4A)
self.loadcell2_address = 0x??  # 실제 주소로 변경
```

## 다음 단계 (Next Steps)

1. **테스트 실행**: `simple_realtime.py` 또는 `dual_loadcell.py` 실행
2. **디버그 출력 확인**: 콘솔에 나오는 메시지 확인
3. **결과 보고**:
   - 9바이트 응답이 맞는지?
   - 무게가 정상적으로 증가하는지? (12g → 15g)
   - 고정값 문제가 해결되었는지?
   - 듀얼 로드셀에서 어떤 주소가 감지되는지?

4. **체크섬 재활성화**: 모든 것이 정상 작동하면 체크섬 검증 다시 활성화

## 문제 해결 (Troubleshooting)

### Q: 여전히 12g → 10g로 떨어진다
A: 9바이트 응답이 아니거나 보정 계수(565.4)가 맞지 않을 수 있음
→ 디버그 출력에서 실제 raw_hex_value 변화 확인

### Q: 한쪽 로드셀만 표시된다
A: 주소가 코드와 다를 수 있음
→ 디버그 출력에서 "Unknown address" 확인 후 코드 수정

### Q: 값이 여전히 고정된다
A: 캐시된 .pyc 파일 문제일 수 있음
→ `rm -rf __pycache__` 실행 후 재시작
