# 변경 사항 요약

## 주요 변경 (2025-10-29)

### 1. ✅ raw_val을 직접 무게로 사용
**문제**:
- 이전에는 `weight = raw_val / 565.4` 로 복잡한 변환
- 분해능(resolution)이 너무 크게 나옴

**해결**:
- **사용자 피드백**: "raw_val 자체가 일반 무게랑 똑같더라고"
- 변경: `weight = raw_val` (직접 사용!)
- 영점 조절과 무게 교정 기능은 그대로 유지

**변경된 파일**:
- [loadcell_protocol.py:185-226](loadcell_protocol.py#L185-L226)

```python
# 이전
weight = raw_weight / 565.4  # 복잡한 변환

# 현재
weight = raw_weight  # 직접 사용!
```

### 2. ✅ 주소 스캔 도구 추가
**문제**:
- "dual 모드에서 로드셀 #2가 나오지 않아"
- "주소 설정이 잘못된 것 같은데, 주소를 찾을 수 있는 코드"
- "전체 로그를 볼 수 있게 해서 내가 주소를 찾을 수 있는 코드"

**해결**:
- **새 파일**: `address_scanner.py`
- 모든 로드셀 주소를 자동으로 감지
- 전체 RX 버퍼를 HEX 덤프로 표시
- 각 주소별 수신 횟수 카운트
- 체크섬 검증 결과 표시

**사용법**:
```bash
python address_scanner.py
```

**출력 예시**:
```
[RX] (9 bytes) 03 06 02 42 00 00 00 0C 5D
  └─ [9B] 03 06 02 42 00 00 00 0C 5D
     Address: 0x03, Func: 0x06, Reg: 0x02
     ✓ Checksum OK
     Weight: 12.0g (raw=12)

감지된 주소:
  0x03 (  3)  -   125회
  0x4A ( 74)  -    98회
```

### 3. ✅ 자동 듀얼 로드셀 모니터
**문제**:
- 기존 `dual_loadcell.py`는 주소가 하드코딩됨 (0x03, 0x04)
- 실제 주소가 다르면 (예: 0x4A) 수동으로 코드 수정 필요

**해결**:
- **새 파일**: `dual_loadcell_auto.py`
- 주소를 자동으로 감지
- 감지된 로드셀 수만큼 패널 동적 생성
- 각각 독립적인 영점 조절/무게 교정
- 내장 디버그 로그
- raw 값 직접 사용

**사용법**:
```bash
python dual_loadcell_auto.py
```

**기능**:
- ✓ 자동 주소 감지 (코드 수정 불필요!)
- ✓ 동적 패널 생성 (2개든 3개든 자동)
- ✓ 각각 독립 교정
- ✓ [0] 키로 모든 로드셀 동시 영점
- ✓ 디버그 로그 내장

## 테스트 방법

### Step 1: 주소 확인
```bash
cd python_loadcell
python address_scanner.py
```
→ "감지된 주소" 섹션에서 실제 주소 확인

### Step 2: 자동 듀얼 모니터 사용 (추천!)
```bash
python dual_loadcell_auto.py
```
→ 자동으로 모든 로드셀 감지하고 패널 생성

### Step 3: 단일 로드셀
```bash
python simple_realtime.py
```

## 기술적 세부사항

### 프로토콜 변경
**9바이트 응답 처리**:
```
[Addr] [Func] [Reg] [Status] [Div] [W1] [W2] [W3] [Checksum]
  0      1      2       3       4     5    6    7       8

Weight = (W1 << 16) + (W2 << 8) + W3
```

**이전**:
- `weight = ((W1 << 16) + (W2 << 8) + W3) / 565.4`

**현재**:
- `weight = (W1 << 16) + (W2 << 8) + W3`
- 영점 조절: `adjusted = weight - zero_offset`
- 무게 교정: `final = adjusted * calibration_factor`

### 주소 필터링
**address_scanner.py**:
- 모든 응답을 캡처하고 주소별로 분류
- 체크섬 검증: `sum(bytes[0:8]) & 0xFF == bytes[8]`
- 중복 제거 및 카운팅

**dual_loadcell_auto.py**:
- 새 주소 감지 시 자동으로 `address_data{}` 딕셔너리에 추가
- 각 주소별 독립적인 zero/factor 관리
- 동적 UI 패널 생성

## 파일 목록

### 새로 추가된 파일
- ✅ `address_scanner.py` - 주소 스캔 도구
- ✅ `dual_loadcell_auto.py` - 자동 듀얼 모니터 (**추천**)
- ✅ `TEST_GUIDE.md` - 테스트 가이드
- ✅ `CHANGES.md` - 이 파일

### 수정된 파일
- ✅ `loadcell_protocol.py` - raw 값 직접 사용

### 기존 파일 (변경 없음)
- `simple_realtime.py` - 단일 로드셀 모니터
- `dual_loadcell.py` - 수동 듀얼 모니터 (주소 고정)
- `loadcell_gui.py` - 테스트/디버그 GUI
- `loadcell_serial.py` - 시리얼 통신 관리
- `test_protocol.py` - 프로토콜 단위 테스트

## 권장 워크플로우

```
1. 처음 설정 시:
   python address_scanner.py
   → 주소 확인 (예: 0x03, 0x4A)

2. 일반 사용:
   python dual_loadcell_auto.py
   → 자동 감지, 자동 패널 생성
   → 영점 조절, 무게 교정

3. 디버깅:
   python address_scanner.py
   → 전체 로그 확인
   → 체크섬 오류 확인
```

## 해결된 문제

| 문제 | 상태 | 해결 방법 |
|------|------|----------|
| raw_val이 실제 무게와 다름 | ✅ | raw 값 직접 사용 (변환 제거) |
| 로드셀 #2가 표시 안 됨 | ✅ | 자동 주소 감지 |
| 주소를 찾을 수 없음 | ✅ | address_scanner.py |
| 전체 로그를 볼 수 없음 | ✅ | 내장 로그 뷰어 |
| 주소마다 코드 수정 필요 | ✅ | 동적 패널 생성 |
| 교정 기능 유지 | ✅ | 영점/무게 교정 그대로 |

## 다음 단계 (선택사항)

- [ ] 체크섬 검증 재활성화 (현재 디버깅 위해 비활성화)
- [ ] 8바이트 응답(BCD) 모드 테스트
- [ ] 3개 이상 로드셀 테스트
- [ ] 장기 안정성 테스트

## 질문이나 문제가 있으면

1. `address_scanner.py` 실행 → 로그 캡처
2. 어떤 주소가 감지되는지 확인
3. 체크섬 오류가 있는지 확인
4. raw 값이 실제 무게와 같은지 확인
