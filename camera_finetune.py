#노출 조정
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# ─ 자동 노출 끄고 수동으로 전환 ───────────────
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)     # 1(또는 0.25) = Manual, 3(또는 0.75) = Auto
cap.set(cv2.CAP_PROP_EXPOSURE, 150)        # 값 범위·단위는 카메라마다 다름
                                            #  → 숫자를 낮추면 더 어둡게, 높이면 밝게

# 필요 시 게인·밝기도 같이 조정
cap.set(cv2.CAP_PROP_GAIN,  4)             # ISO 비슷한 개념
cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.4)      # 0.0 ~ 1.0 (미지원이면 무시됨)



# 노출을 수동으로 전환하고 100 단위로 고정
v4l2-ctl -d /dev/video0 -c exposure_auto=1 -c exposure_absolute=100

#####################
#초점 조정

#지원 여부 확인
v4l2-ctl --list-ctrls | grep focus


# 오토포커스 켜기
cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)   # 1 = ON, 0 = OFF

# 수동 모드로 바꾸고 값을 지정
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FOCUS,  20)     # 0~255 범위(예시)

# 수동 초점(0)으로 전환 후 30 단계로 설정
v4l2-ctl -c focus_auto=0 -c focus_absolute=30



##########
#프로그램에 바로 넣는 예시
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# 1) 수동 노출
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
cap.set(cv2.CAP_PROP_EXPOSURE, 120)     # 밝기 조절

# 2) 오토포커스로 한 번 맞춘 뒤 잠그기
cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
time.sleep(1)                           # 1초 정도 AF 동작 대기
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)      # 잠금
# 필요하면 cap.set(cv2.CAP_PROP_FOCUS, 원하는값)

# 이후 캡처 루프…

