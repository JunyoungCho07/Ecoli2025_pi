import cv2
import numpy as np
from ultralytics import YOLO
from collections import deque

# --- 설정 ---
# 학습된 YOLO 모델 경로 (.pt 또는 .onnx)
MODEL_PATH = '/home/admin/Desktop/best.onnx' 
# 입력 이미지 크기
IMG_SIZE = 1024
# 객체 탐지 최소 신뢰도
CONF_THRESHOLD = 0.25
# 클래스별 시각화 색상 (BGR 순서)
# data.yaml에 따르면 0: 'Colony', 1: 'InhibitionZone'
CLASS_COLORS = {
    0: (0, 255, 0),  # Colony: 초록색
    1: (255, 0, 0)   # InhibitionZone: 파란색
}
# 평균 계산을 위한 프레임 수
AVG_FRAME_COUNT = 5

# --- 모델 및 비디오 로드 ---
try:
    # YOLO 모델 로드
    model = YOLO(MODEL_PATH, task='detect')
    print("[INFO] YOLO 모델을 성공적으로 로드했습니다.")
except Exception as e:
    print(f"[ERROR] 모델 로드에 실패했습니다: {e}")
    exit()

# 웹캠 열기 (0은 기본 카메라)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[ERROR] 카메라를 열 수 없습니다.")
    exit()

print("[INFO] CPU에서 실시간 탐지를 시작합니다. 종료하려면 'q' 또는 ESC 키를 누르세요.")

# 최근 탐지된 '콜로니' 개수를 저장하기 위한 deque 생성
detection_counts = deque(maxlen=AVG_FRAME_COUNT)

# --- 메인 루프 ---
while True:
    # 프레임 읽기
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] 프레임을 받아오지 못했습니다.")
        break

    # --- 이미지 전처리 ---
    # 프레임 중앙을 정사각형으로 자르고 1024x1024로 리사이즈
    h, w, _ = frame.shape
    if h != IMG_SIZE or w != IMG_SIZE:
        min_dim = min(h, w)
        start_x = (w - min_dim) // 2
        start_y = (h - min_dim) // 2
        
        cropped_frame = frame[start_y:start_y + min_dim, start_x:start_x + min_dim]
        resized_frame = cv2.resize(cropped_frame, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_AREA)
    else:
        resized_frame = frame

    # YOLO 입력 형식에 맞게 BGR을 RGB로 변환
    img_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

    # --- 객체 탐지 ---
    # CPU를 사용하여 예측 수행
    results = model.predict(source=img_rgb, save=False, imgsz=IMG_SIZE, conf=CONF_THRESHOLD, device='cpu')
    result = results[0] # 첫 번째 결과 사용

    # 예측 데이터 추출
    boxes = result.boxes.xyxy.cpu().numpy()
    classes = result.boxes.cls.cpu().numpy().astype(int)
    confs = result.boxes.conf.cpu().numpy()
    
    # 현재 프레임의 콜로니 개수를 세기 위한 변수
    colony_count_this_frame = 0

    # --- 결과 시각화 및 콜로니 카운팅 ---
    # 탐지된 객체들에 대한 반복
    for box, class_id, conf in zip(boxes, classes, confs):
        x1, y1, x2, y2 = map(int, box)
        
        # 클래스에 맞는 색상 가져오기 (없으면 흰색)
        color = CLASS_COLORS.get(class_id, (255, 255, 255))
        
        class_name = model.names[class_id]
        
        # 클래스가 'Colony'인 경우 카운트 증가
        if class_name == 'Colony':
            colony_count_this_frame += 1
            
        label = f"{class_name} {conf:.2f}"

        # 억제 구역의 넓이 계산
        if class_name == 'InhibitionZone':
            bbox_w = x2 - x1
            bbox_h = y2 - y1
            # 경계 상자에 내접하는 원의 반지름 및 넓이 계산
            radius = min(bbox_w, bbox_h) / 2
            area = np.pi * (radius ** 2)
            label += f" Area: {area:.0f}"

        # 경계 상자 그리기
        cv2.rectangle(resized_frame, (x1, y1), (x2, y2), color, 2)
        
        # 레이블 텍스트 배경 그리기
        (label_width, label_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(resized_frame, (x1, y1 - label_height - 10), (x1 + label_width, y1), color, -1)
        
        # 레이블 텍스트 그리기
        cv2.putText(resized_frame, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # 현재 프레임의 'Colony' 탐지 개수를 deque에 추가
    detection_counts.append(colony_count_this_frame)


    # --- 콜로니 개수 안정성 검사 및 평균 예측 데이터 표시 ---
    avg_text = "Calculating..."
    avg_color = (0, 165, 255)  # 주황색: 계산 중

    # 최근 5개 프레임 데이터가 모두 모였을 때만 안정성 검사
    if len(detection_counts) == AVG_FRAME_COUNT:
        avg_count = np.mean(detection_counts)
        
        # 평균값이 0보다 클 때만 편차 계산
        if avg_count > 0:
            # 평균값 대비 각 측정값의 최대 편차 비율 계산
            max_deviation = max(abs(count - avg_count) for count in detection_counts)
            max_deviation_ratio = max_deviation / avg_count
            
            # 최대 편차가 10% 이내이면 신뢰성 있는 결과로 판단
            if max_deviation_ratio <= 0.1:
                avg_text = f"Stable Colony Count: {avg_count:.2f}"
                avg_color = (0, 255, 0)  # 초록색: 안정
            else:
                avg_text = f"Unstable Colony Count: {avg_count:.2f}"
                avg_color = (0, 0, 255)  # 빨간색: 불안정
        else:  # avg_count가 0이면 모든 값이 0이므로 안정 상태
            avg_text = f"Stable Colony Count: 0.00"
            avg_color = (0, 255, 0)  # 초록색: 안정

    cv2.putText(resized_frame, avg_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, avg_color, 2)

    # 결과 화면 출력
    cv2.imshow("E.coli Colony Counter (CPU)", resized_frame)

    # 'q' 또는 ESC 키를 누르면 종료
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        print("[INFO] 종료합니다.")
        break

# --- 자원 해제 ---
cap.release()
cv2.destroyAllWindows()

