from ultralytics import YOLO
import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import random

# 1. 모델 불러오기
model_path = '/home/ecoli3/Desktop/best.onnx'  # ONNX or PT 가능
model = YOLO(model_path, task='detect')

# 2. 이미지 폴더 설정
folder_path = '/home/ecoli3/R&E/Picture/images'
valid_exts = ('.jpg', '.jpeg', '.png')

# 3. 이미지 반복 처리
for filename in os.listdir(folder_path):
    if filename.lower().endswith(valid_exts):
        image_path = os.path.join(folder_path, filename)
        img_bgr = cv2.imread(image_path)

        if img_bgr is None:
            print(f"[오류] 이미지 로드 실패: {filename}")
            continue

        h, w = img_bgr.shape[:2]

        # 4. 중앙 정사각형 자르기 (1034x1024인 경우는 그대로 사용)
        if not (h == 1024 and w == 1024):
            min_dim = min(h, w)
            start_x = (w - min_dim) // 2
            start_y = (h - min_dim) // 2
            img_bgr = img_bgr[start_y:start_y+min_dim, start_x:start_x+min_dim]

            # 5. 1024x1024로 리사이즈
            img_bgr = cv2.resize(img_bgr, (1024, 1024), interpolation=cv2.INTER_AREA)

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        # 6. 예측 수행
        results = model.predict(source=img_rgb, save=False, imgsz=1024, conf=0.25, device='cpu')
        result = results[0]

        # 7. 결과 추출
        boxes = result.boxes.xyxy.cpu().numpy() if result.boxes else []
        classes = result.boxes.cls.cpu().numpy() if result.boxes else []
        confs = result.boxes.conf.cpu().numpy() if result.boxes else []

        img_vis = img_rgb.copy()

        # 8. 시각화
        for i, (box, cls_id, conf) in enumerate(zip(boxes, classes, confs)):
            x1, y1, x2, y2 = map(int, box)
            color = [random.randint(100, 255) for _ in range(3)]
            label = f"Colony {conf:.2f}"  # 클래스 하나일 경우

            cv2.rectangle(img_vis, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img_vis, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # 9. 출력
        plt.figure(figsize=(10, 10))
        plt.imshow(img_vis)
        plt.title(f"Prediction: {filename}")
        plt.axis('off')
        plt.show()
