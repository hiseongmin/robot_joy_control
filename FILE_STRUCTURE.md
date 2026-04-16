# 📂 Robot Joy Control - 파일 구조 설명

## 🏠 홈 디렉토리 (`/home/ye/`)
실행 스크립트들 - **이것만 실행하면 됨!**

```
/home/ye/
├── 1_roscore.sh            # 터미널 1: ROS 마스터 (고정)
├── 2_eye_modules.sh        # 터미널 2: 아이모듈 (고정)
├── 3_joystick.sh           # 터미널 3: 조이스틱 (로봇명 지정)
├── 4_robot_control.sh      # 터미널 4: 로봇 제어 (로봇명 지정)
│
├── safe_smooth_control.sh  # 안전 모드 실행 (백업용)
├── monitor_passive.py      # 네트워크 모니터링
└── robot_menu.sh           # 로봇 선택 메뉴
```

## 📦 ROS 패키지 (`~/catkin_ws/src/robot_joy_control/`)
실제 코드와 설정 - **수정할 때만 접근**

```
robot_joy_control/
├── robots/                 # 로봇별 설정 파일
│   └── nextage.yaml       # NEXTAGE 로봇 설정
│
├── scripts/                # Python 제어 스크립트
│   ├── joy_head_nextage.py     # 기본 헤드 제어
│   ├── joy_head_safe.py        # 안전 모드 (명령 겹침 방지)
│   ├── joy_head_smooth.py      # 부드러운 움직임
│   ├── joy_head_asymmetric.py  # 비대칭 제한 (상/하 다른 각도)
│   └── network_monitor.py      # 네트워크 진단
│
└── launch/                 # ROS launch 파일
    └── (여러 launch 파일)
```

---

## 🚀 사용 방법 (간단!)

### 기본 사용 (NEXTAGE)
```bash
# 터미널 1
./1_roscore.sh

# 터미널 2
./2_eye_modules.sh

# 터미널 3
./3_joystick.sh nextage

# 터미널 4
./4_robot_control.sh nextage
```

### 다른 로봇 추가하려면
1. `robots/` 폴더에 `새로봇.yaml` 추가
2. 실행할 때 로봇 이름 지정:
```bash
./3_joystick.sh 새로봇
./4_robot_control.sh 새로봇
```

---

## 💡 핵심 이해

### 왜 이렇게 나눴나?

1. **홈 디렉토리** = 실행 전용
   - 자주 쓰는 스크립트
   - 터미널에서 바로 실행

2. **ROS 패키지** = 코드 저장소
   - Git으로 관리
   - 실제 로직이 있는 곳

### 터미널별 역할

| 터미널 | 무엇을? | 로봇 지정? |
|--------|---------|------------|
| 1 | ROS 마스터 | ❌ 항상 같음 |
| 2 | 아이모듈 | ❌ 항상 같음 |
| 3 | 조이스틱 | ✅ 로봇별로 |
| 4 | 로봇 제어 | ✅ 로봇별로 |

### 로봇 설정 (nextage.yaml)
```yaml
# 네트워크 설정
ros_master_uri: "http://133.11.216.57:11311"  # 로봇 IP
local_ip: "133.11.216.68"                     # 내 컴퓨터 IP

# 제어 파라미터
max_angle: 0.523        # 최대 각도 (30도)
move_duration: 0.15     # 움직임 시간
rate: 10.0              # 업데이트 주기
```

---

## 🔧 문제 해결

### 로봇이 안 움직일 때
1. `python monitor_passive.py` 실행해서 상태 확인
2. 조이스틱 메시지 확인: `rostopic echo /joy`
3. 네트워크 확인: `ping 133.11.216.57`

### 우르르 현상이 생길 때
- `safe_smooth_control.sh` 사용 (안전 모드)
- 또는 `nextage.yaml`에서 rate 줄이기

### 새 로봇 추가하고 싶을 때
1. `robots/새로봇.yaml` 만들기 (nextage.yaml 복사해서 수정)
2. IP 주소와 파라미터 수정
3. 바로 사용 가능!