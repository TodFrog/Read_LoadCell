# Load Cell Reader - Python Version

Python 기반 로드셀 데이터 리더 애플리케이션 (Ubuntu 18.04 호환)

## 개요

이 애플리케이션은 Windows VB.NET 버전을 Python으로 재구현한 것으로, Ubuntu 18.04 및 기타 Linux 배포판에서 실행 가능합니다.

## 주요 기능

- 시리얼 통신을 통한 로드셀 데이터 읽기 (115200 baud)
- GUI 기반 실시간 중량 표시 (20 FPS)
- **2차 곡선 보정** - 비선형 센서 특성 자동 보정 (RMS 오차 1.34g)
- 영점 조정 기능 (소프트웨어 영점)
- 로드셀 파라미터 설정 및 조회
- 로드셀 주소 변경
- 고유 ID 읽기
- TX/RX 데이터 모니터링

## 시스템 요구사항

- Ubuntu 18.04 LTS 이상 (또는 호환 Linux 배포판)
- Python 3.6 이상
- USB 시리얼 어댑터 (로드셀 연결용)

## 설치 방법

### 1. 시스템 패키지 설치 (Ubuntu 18.04)

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
sudo apt-get install python3-pyqt5
```

### 2. Python 가상환경 생성 (선택사항)

```bash
cd python_loadcell
python3 -m venv venv
source venv/bin/activate
```

### 3. Python 의존성 설치

```bash
pip install -r requirements.txt
```

또는 직접 설치:

```bash
pip install pyserial PyQt5
```

### 4. 시리얼 포트 권한 설정

시리얼 포트에 접근하려면 사용자를 `dialout` 그룹에 추가해야 합니다:

```bash
sudo usermod -a -G dialout $USER
```

변경사항을 적용하려면 로그아웃 후 다시 로그인하세요.

또는 임시로 권한을 부여:

```bash
sudo chmod 666 /dev/ttyUSB0
```

## 실행 방법

### 실시간 모니터링 (권장)
```bash
python3 simple_realtime.py
```
- 20 FPS 연속 측정
- 2차 곡선 보정 자동 적용
- 영점 조절 기능

### 테스트/디버그 GUI
```bash
python3 loadcell_gui.py
```
- 버튼 클릭 방식 측정
- TX/RX 데이터 모니터링
- 프로토콜 테스트용

## 파일 구조

```
python_loadcell/
├── loadcell_gui.py         # 메인 GUI 애플리케이션
├── loadcell_serial.py      # 시리얼 통신 관리
├── loadcell_protocol.py    # 로드셀 프로토콜 구현
├── requirements.txt        # Python 의존성
└── README.md              # 이 문서
```

## 사용 방법

### 1. 연결

1. 로드셀을 USB 시리얼 어댑터를 통해 컴퓨터에 연결
2. 애플리케이션 실행
3. "통신포트" 드롭다운에서 적절한 포트 선택 (예: /dev/ttyUSB0)
4. "열기" 버튼 클릭

### 2. 로드셀 ID 읽기

1. "id읽기" 버튼 클릭
2. 고유 ID와 주소가 표시됨

### 3. 중량 측정

1. "중량읽기" 버튼 클릭
2. 현재 중량이 큰 숫자로 표시됨
3. 분해도와 AD값도 함께 표시됨

### 4. 영점 조정

1. 로드셀에 아무것도 올려놓지 않은 상태로 유지
2. "영점조정" 버튼 클릭
3. 영점이 설정됨

### 5. 파라미터 설정

1. "파라미터 변경" 그룹에서 원하는 값 선택:
   - 최대중량값: 5-100kg
   - 분해도: 0.0001-5.0
   - 영점범위: 0-9%
   - 안착영점범위: 1-10%
   - 저울종류: 쾌속/보통/crane/대형 crane 측정
2. "변경" 버튼 클릭
3. "param읽기"로 변경 확인

### 6. 주소 변경

1. 상단 드롭다운에서 새 주소 선택 (1-10)
2. "주소변경" 버튼 클릭
3. ID 읽기로 변경 확인

## 통신 프로토콜

### 시리얼 설정
- Baud rate: 115200
- Data bits: 8
- Parity: None
- Stop bits: 1

### 명령 구조
```
[주소] [기능코드] [레지스터] [데이터/상수] [체크섬]
```

### 주요 기능 코드
- 0x05: 읽기
- 0x63: 쓰기

### 주요 레지스터
- 0x05: ID 읽기
- 0x02: 중량 읽기
- 0x23: 파라미터 읽기/쓰기
- 0x10: 주소 쓰기
- 0x06: 영점 설정

## 트러블슈팅

### 시리얼 포트가 보이지 않음
```bash
# 연결된 시리얼 장치 확인
ls /dev/ttyUSB* /dev/ttyACM*
dmesg | grep tty
```

### Permission Denied 오류
```bash
# dialout 그룹 확인
groups

# 그룹에 없다면 추가
sudo usermod -a -G dialout $USER
# 로그아웃 후 재로그인
```

### 데이터 수신 안됨
- 케이블 연결 확인
- 로드셀 전원 확인
- 올바른 포트 선택 확인
- TX/RX 데이터 모니터 확인

## 개발자 정보

### 모듈 설명

**loadcell_protocol.py**
- 로드셀 통신 프로토콜 정의
- 명령 생성 및 응답 파싱
- 체크섬 계산

**loadcell_serial.py**
- 시리얼 포트 관리
- 비동기 데이터 수신 (쓰레드 기반)
- 명령 송신

**loadcell_gui.py**
- PyQt5 기반 GUI
- 사용자 인터페이스
- 이벤트 처리

## 라이선스

이 프로젝트는 원본 VB.NET 구현을 기반으로 Python으로 재작성되었습니다.
