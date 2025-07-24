import cv2

# 카메라 열기 (0번 디바이스)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("카메라를 열 수 없습니다.")

# 최대 줌 배율(예: 4배)
MAX_ZOOM = 4

# 트랙바 콜백(아무 동작 안 함)
def on_trackbar(val):
    pass

# 윈도우 생성 및 트랙바 추가
cv2.namedWindow('ZoomCam')
cv2.createTrackbar('Zoom', 'ZoomCam', 10, MAX_ZOOM*10, on_trackbar)
# 트랙바 값 범위: 10 ~ MAX_ZOOM*10 (즉 줌 1.0 ~ MAX_ZOOM 단계, 소수점 단위까지)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]
    # 트랙바 값 받아오기
    zoom_level = cv2.getTrackbarPos('Zoom', 'ZoomCam') / 10.0
    if zoom_level < 1.0:
        zoom_level = 1.0

    # 잘라낼 영역 크기
    new_w = int(w / zoom_level)
    new_h = int(h / zoom_level)
    x1 = (w - new_w) // 2
    y1 = (h - new_h) // 2

    # ROI(Region of Interest) 잘라내기
    roi = frame[y1:y1+new_h, x1:x1+new_w]

    # 원래 크기로 리사이즈(Interpolation: 선형)
    zoomed = cv2.resize(roi, (w, h), interpolation=cv2.INTER_LINEAR)

    cv2.imshow('ZoomCam', zoomed)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC 키 눌러 종료
        break

cap.release()
cv2.destroyAllWindows()
