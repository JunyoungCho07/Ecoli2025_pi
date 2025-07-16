# from ultralytics import YOLO
# import cv2
# import matplotlib.pyplot as plt
# import os

# # 모델 로드
# model_path = 'C:/Users/cho-j/OneDrive/바탕 화면/Ecoli_2025/runs/exp_seg_colab3/weights/best.pt'  # 경로 확인
# model = YOLO(model_path)

# # 예측할 이미지 경로
# image_path = 'C:/Users/cho-j/OneDrive/바탕 화면/Ecoli_2025/test_images/test (5).png'  # 예측 대상 이미지

# # 이미지 로드
# img = cv2.imread(image_path)
# img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# # 예측
# results = model.predict(source=img_rgb, save=False, conf=0.25, show=False, imgsz=512, device='cpu')

# # 시각화
# result = results[0]

# # Segmentation 마스크 시각화
# masks = result.masks.data.cpu().numpy()  # [n, h, w]
# boxes = result.boxes.xyxy.cpu().numpy()
# cls = result.boxes.cls.cpu().numpy()

# # 원본 이미지 복사
# img_vis = img_rgb.copy()

# # 색상 랜덤 설정
# import random
# colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(masks))]

# for i, mask in enumerate(masks):
#     color = colors[i]
#     mask_binary = (mask > 0.5).astype('uint8') * 255
#     contours, _ = cv2.findContours(mask_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     cv2.drawContours(img_vis, contours, -1, color, thickness=2)
#     # 박스와 클래스 표시
#     x1, y1, x2, y2 = map(int, boxes[i])
#     class_id = int(cls[i])
#     cv2.rectangle(img_vis, (x1, y1), (x2, y2), color, 2)
#     cv2.putText(img_vis, f"Colony", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

# # 결과 출력
# plt.figure(figsize=(10, 10))
# plt.imshow(img_vis)
# plt.axis('off')
# plt.title("YOLOv8 Segmentation Prediction")
# plt.show()



from ultralytics import YOLO
import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import random

# 모델 불러오기
model_path = '/home/ecoli3/Desktop/best.onnx'
model = YOLO(model_path, task='segment')

# 이미지 폴더 설정
folder_path = '/home/ecoli3/R&E/Picture/images'

# 이미지 확장자 필터
valid_exts = ('.jpg', '.jpeg', '.png')

# 이미지 반복 처리
for filename in os.listdir(folder_path):
    if filename.lower().endswith(valid_exts):
        image_path = os.path.join(folder_path, filename)
        img_bgr = cv2.imread(image_path)

        if img_bgr is None:
            print(f"이미지 로드 실패: {filename}")
            continue

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        #  예측 수행
        results = model.predict(source=img_rgb, save=False, conf=0.25, imgsz=256, device='cpu') # change image size

        result = results[0]

        #  결과 가져오기
        masks = result.masks.data.cpu().numpy() if result.masks else []
        boxes = result.boxes.xyxy.cpu().numpy() if result.boxes else []
        classes = result.boxes.cls.cpu().numpy() if result.boxes else []

        img_vis = img_rgb.copy()
        height, width = img_vis.shape[:2]

        #  마스크 색상 미리 지정
        colors = [[random.randint(100, 255) for _ in range(3)] for _ in range(len(masks))]

        #  마스크 및 바운딩 박스 그리기
        for i, mask in enumerate(masks):
            color = colors[i]
            mask_resized = (mask > 0.5).astype(np.uint8) * 255
            contours, _ = cv2.findContours(mask_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(img_vis, contours, -1, color, thickness=2)

            # 박스와 클래스명 표시
            x1, y1, x2, y2 = map(int, boxes[i])
            class_id = int(classes[i])
            label = f"Colony"  # 클래스가 하나뿐이라면 고정

            cv2.rectangle(img_vis, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img_vis, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        #  시각화
        plt.figure(figsize=(10, 10))
        plt.imshow(img_vis)
        plt.title(f"Prediction: {filename}")
        plt.axis('off')
        plt.show()
