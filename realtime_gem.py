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

print("[INFO] CPU에서 실시간 탐지를 시작합니다.")
print("[INFO] 'm' 키를 눌러 모드를 전환하세요 (Colony <-> InhibitionZone).")
print("[INFO] 종료하려면 'q' 또는 ESC 키를 누르세요.")

# 최근 탐지된 '콜로니' 개수를 저장하기 위한 deque 생성
detection_counts = deque(maxlen=AVG_FRAME_COUNT)
# 탐지 모드 변수 ('colony' 또는 'inhibition_zone')
detection_mode = 'colony'

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
    results = model.predict(source=img_rgb, save=False, imgsz=IMG_SIZE, conf=CONF_THRESHOLD, device='cpu', verbose=False)
    result = results[0] # 첫 번째 결과 사용

    # 예측 데이터 추출
    boxes = result.boxes.xyxy.cpu().numpy()
    classes = result.boxes.cls.cpu().numpy().astype(int)
    confs = result.boxes.conf.cpu().numpy()
    
    # 현재 프레임의 콜로니 개수를 세기 위한 변수
    colony_count_this_frame = 0

    # --- 결과 시각화 및 카운팅 (모드에 따라 분리) ---
    for box, class_id, conf in zip(boxes, classes, confs):
        class_name = model.names[class_id]
        
        # 'colony' 모드일 때 'Colony'만 처리
        if detection_mode == 'colony' and class_name == 'Colony':
            colony_count_this_frame += 1
            x1, y1, x2, y2 = map(int, box)
            color = CLASS_COLORS.get(class_id, (255, 255, 255))
            label = f"{class_name} {conf:.2f}"
            
            # 경계 상자 및 레이블 그리기
            cv2.rectangle(resized_frame, (x1, y1), (x2, y2), color, 2)
            (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(resized_frame, (x1, y1 - label_height - 10), (x1 + label_width, y1), color, -1)
            cv2.putText(resized_frame, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # 'inhibition_zone' 모드일 때 'InhibitionZone'만 처리
        elif detection_mode == 'inhibition_zone' and class_name == 'InhibitionZone':
            x1, y1, x2, y2 = map(int, box)
            color = CLASS_COLORS.get(class_id, (255, 255, 255))
            
            # 억제 구역 넓이 계산
            bbox_w = x2 - x1
            bbox_h = y2 - y1
            radius = min(bbox_w, bbox_h) / 2
            area = np.pi * (radius ** 2)
            label = f"{class_name} Area: {area:.0f}"
            
            # 경계 상자 및 레이블 그리기
            cv2.rectangle(resized_frame, (x1, y1), (x2, y2), color, 2)
            (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(resized_frame, (x1, y1 - label_height - 10), (x1 + label_width, y1), color, -1)
            cv2.putText(resized_frame, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # --- UI 텍스트 표시 ---
    # 현재 탐지 모드 표시
    mode_text = f"Mode: {detection_mode.upper()}"
    cv2.putText(resized_frame, mode_text, (IMG_SIZE - 250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

    # 'colony' 모드에서만 콜로니 개수 안정성 검사 및 표시
    if detection_mode == 'colony':
        detection_counts.append(colony_count_this_frame)
        avg_text = "Calculating..."
        avg_color = (0, 165, 255)  # 주황색: 계산 중

        if len(detection_counts) == AVG_FRAME_COUNT:
            avg_count = np.mean(detection_counts)
            if avg_count > 0:
                max_deviation = max(abs(count - avg_count) for count in detection_counts)
                max_deviation_ratio = max_deviation / avg_count
                if max_deviation_ratio <= 0.1:
                    avg_text = f"Stable Colony Count: {avg_count:.2f}"
                    avg_color = (0, 255, 0)  # 초록색: 안정
                else:
                    avg_text = f"Unstable Colony Count: {avg_count:.2f}"
                    avg_color = (0, 0, 255)  # 빨간색: 불안정
            else:
                avg_text = f"Stable Colony Count: 0.00"
                avg_color = (0, 255, 0)
        cv2.putText(resized_frame, avg_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, avg_color, 2)

    # 결과 화면 출력
    cv2.imshow("E.coli Colony Counter (CPU)", resized_frame)

    # --- 키 입력 처리 ---
    key = cv2.waitKey(1) & 0xFF
    # 'q' 또는 ESC 키를 누르면 종료
    if key == ord('q') or key == 27:
        print("[INFO] 종료합니다.")
        break
    # 'm' 키를 누르면 모드 전환
    elif key == ord('m'):
        if detection_mode == 'colony':
            detection_mode = 'inhibition_zone'
            print("[INFO] 모드 변경: InhibitionZone Detection")
        else:
            detection_mode = 'colony'
            print("[INFO] 모드 변경: Colony Counting")
        # 모드 변경 시 카운트 리스트 초기화
        detection_counts.clear()

# --- 자원 해제 ---
cap.release()
cv2.destroyAllWindows()

