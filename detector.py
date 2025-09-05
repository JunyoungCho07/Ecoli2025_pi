import cv2
import numpy as np
from ultralytics import YOLO
from collections import deque
import time

# --- 라즈베리파이 GPIO 및 네오픽셀 설정 ---
# 라즈베리파이가 아닌 환경에서 실행될 경우를 대비한 예외 처리
try:
    import board
    import neopixel
    NEOPIXEL_ENABLED = True
except (ImportError, NotImplementedError):
    print("[WARNING] Neopixel library not found. LED control will be disabled.")
    NEOPIXEL_ENABLED = False

# --- 설정 ---
# 학습된 YOLO 모델 경로 (.pt 또는 .onnx)
MODEL_PATH = '/home/admin/Desktop/best.onnx' 
# 입력 이미지 크기 (픽셀)
IMG_SIZE = 1024
# 이미지에 해당하는 실제 길이 (mm)
REAL_WORLD_MM = 118.0
# 픽셀-밀리미터 변환 계수
MM_PER_PIXEL = REAL_WORLD_MM / IMG_SIZE
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

# 네오픽셀 설정
if NEOPIXEL_ENABLED:
    NUM_PIXELS = 64      # LED 개수
    PIXEL_PIN = board.D18  # GPIO 18번 핀
    ORDER = neopixel.GRB
    pixels = neopixel.NeoPixel(
        PIXEL_PIN, NUM_PIXELS,
        brightness=0.3, auto_write=False, pixel_order=ORDER
    )

# --- 모델 및 비디오 로드 ---
try:
    # YOLO 모델 로드
    model = YOLO(MODEL_PATH, task='detect')
    print("[INFO] YOLO model loaded successfully.")
except Exception as e:
    print(f"[ERROR] Failed to load model: {e}")
    exit()

# 웹캠 열기 (0은 기본 카메라)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[ERROR] Cannot open camera.")
    exit()

print("[INFO] Starting real-time detection on CPU.")
print("[INFO] Press 'm' to switch mode (Colony <-> InhibitionZone).")
print("[INFO] Press 'q' or ESC to quit.")

# 최근 탐지된 '콜로니' 개수를 저장하기 위한 deque 생성
detection_counts = deque(maxlen=AVG_FRAME_COUNT)
# 탐지 모드 변수 ('colony' 또는 'inhibition_zone')
detection_mode = 'colony'

# --- 메인 로직 (try...finally로 감싸서 종료 시 항상 자원 해제) ---
try:
    # 네오픽셀 켜기
    if NEOPIXEL_ENABLED:
        print("[INFO] Turning on Neopixel LED.")
        pixels.fill((5, 5, 5))
        pixels.show()

    # --- 메인 루프 ---
    while True:
        # 프레임 읽기
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
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
                
                # 억제 구역 넓이 계산 (픽셀 -> mm 변환)
                bbox_w_px = x2 - x1
                bbox_h_px = y2 - y1
                diameter_px = min(bbox_w_px, bbox_h_px)

                # 실제 길이 계산
                diameter_mm = diameter_px * MM_PER_PIXEL
                radius_mm = diameter_mm / 2
                area_mm2 = np.pi * (radius_mm ** 2)
                
                label = f"Dia:{diameter_mm:.1f}mm Area:{area_mm2:.1f}mm2"
                
                # 경계 상자 및 레이블 그리기
                cv2.rectangle(resized_frame, (x1, y1), (x2, y2), color, 2)
                (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(resized_frame, (x1, y1 - label_height - 10), (x1 + label_width, y1), color, -1)
                cv2.putText(resized_frame, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # --- UI 텍스트 표시 ---
        mode_text = f"Mode: {detection_mode.upper()}"
        cv2.putText(resized_frame, mode_text, (IMG_SIZE - 250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

        if detection_mode == 'colony':
            detection_counts.append(colony_count_this_frame)
            avg_text = "Calculating..."
            avg_color = (0, 165, 255)

            if len(detection_counts) == AVG_FRAME_COUNT:
                avg_count = np.mean(detection_counts)
                if avg_count > 0:
                    max_deviation = max(abs(count - avg_count) for count in detection_counts)
                    max_deviation_ratio = max_deviation / avg_count
                    if max_deviation_ratio <= 0.1:
                        avg_text = f"Stable Colony Count: {avg_count:.2f}"
                        avg_color = (0, 255, 0)
                    else:
                        avg_text = f"Unstable Colony Count: {avg_count:.2f}"
                        avg_color = (0, 0, 255)
                else:
                    avg_text = f"Stable Colony Count: 0.00"
                    avg_color = (0, 255, 0)
            cv2.putText(resized_frame, avg_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, avg_color, 2)

        cv2.imshow("E.coli Colony Counter (CPU)", resized_frame)

        # --- 키 입력 처리 ---
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            print("[INFO] Quitting.")
            break
        elif key == ord('m'):
            detection_mode = 'inhibition_zone' if detection_mode == 'colony' else 'colony'
            print(f"[INFO] Mode changed: {detection_mode.replace('_', ' ').title()}")
            detection_counts.clear()

finally:
    # --- 자원 해제 ---
    print("[INFO] Releasing resources.")
    cap.release()
    cv2.destroyAllWindows()
    # 네오픽셀 끄기
    if NEOPIXEL_ENABLED:
        print("[INFO] Turning off Neopixel LED.")
        pixels.fill((0, 0, 0))
        pixels.show()

