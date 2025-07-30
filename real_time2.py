import cv2
import numpy as np
from ultralytics import YOLO

# 1. YOLOv11 모델 로드
model_path = '/home/ecoli3/Desktop/best.onnx'  # .pt도 가능
model = YOLO(model_path, task='detect')

# 2. 카메라 연결
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[오류] 카메라를 열 수 없습니다.")
    exit()

print("[실행] 실시간 예측 시작... (종료: q 또는 ESC)")

# 3. 고정 색상 (녹색)
box_color = (0, 255, 0)  # Green

while True:
    ret, frame = cap.read()
    if not ret:
        print("[오류] 프레임을 읽을 수 없습니다.")
        break

    # 4. 중앙 정사각형 crop + 1024x1024 resize
    h, w = frame.shape[:2]
    if not (h == 1024 and w == 1024):
        min_dim = min(h, w)
        start_x = (w - min_dim) // 2
        start_y = (h - min_dim) // 2
        frame = frame[start_y:start_y+min_dim, start_x:start_x+min_dim]
        frame = cv2.resize(frame, (1024, 1024), interpolation=cv2.INTER_AREA)

    # 5. BGR → RGB 변환
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 6. 예측 수행 (CPU 또는 GPU 선택 가능)
    results = model.predict(source=img_rgb, save=False, imgsz=1024, conf=0.25, device='cpu')  # 또는 'cuda:0'
    result = results[0]

    boxes = result.boxes.xyxy.cpu().numpy() if result.boxes else []
    classes = result.boxes.cls.cpu().numpy() if result.boxes else []
    confs = result.boxes.conf.cpu().numpy() if result.boxes else []

    # 7. 바운딩 박스 + 라벨 시각화
    for box, cls_id, conf in zip(boxes, classes, confs):
        x1, y1, x2, y2 = map(int, box)
        label = f"Colony {conf:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

    # 8. 화면 출력
    cv2.imshow("YOLOv11 실시간 탐지", frame)

    # 9. 종료 조건 (ESC 또는 'q')
    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord('q'):
        break

# 10. 종료
cap.release()
cv2.destroyAllWindows()
