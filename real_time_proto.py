import cv2
import numpy as np
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
from ultralytics import YOLO
import random

# YOLO 모델 로드
model_path = '/home/ecoli3/Desktop/best.onnx'
model = YOLO(model_path, task='detect')

# TK 인터페이스 구성
root = tk.Tk()
root.title("YOLOv11 실시간 예측 GUI")

# 영상 출력 라벨
video_label = Label(root)
video_label.pack()

# 종료 버튼
def close_window():
    global running
    running = False
    cap.release()
    root.destroy()

exit_button = Button(root, text="종료", command=close_window)
exit_button.pack(pady=10)

# 카메라 초기화
cap = cv2.VideoCapture(0)
running = True

def process_frame():
    global running
    if not running:
        return

    ret, frame = cap.read()
    if not ret:
        return

    h, w = frame.shape[:2]
    if not (h == 1024 and w == 1024):
        min_dim = min(h, w)
        start_x = (w - min_dim) // 2
        start_y = (h - min_dim) // 2
        frame = frame[start_y:start_y+min_dim, start_x:start_x+min_dim]
        frame = cv2.resize(frame, (1024, 1024), interpolation=cv2.INTER_AREA)

    # RGB 변환
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 예측
    results = model.predict(source=img_rgb, save=False, imgsz=1024, conf=0.25, device='cpu')
    result = results[0]

    boxes = result.boxes.xyxy.cpu().numpy() if result.boxes else []
    classes = result.boxes.cls.cpu().numpy() if result.boxes else []
    confs = result.boxes.conf.cpu().numpy() if result.boxes else []

    # 시각화
    for i, (box, cls_id, conf) in enumerate(zip(boxes, classes, confs)):
        x1, y1, x2, y2 = map(int, box)
        color = [random.randint(100, 255) for _ in range(3)]
        label = f"Colony {conf:.2f}"

        cv2.rectangle(img_rgb, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img_rgb, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Tkinter용 이미지 변환
    img_pil = Image.fromarray(img_rgb)
    imgtk = ImageTk.PhotoImage(image=img_pil)

    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    # 다음 프레임 예약
    root.after(10, process_frame)

# 루프 시작
process_frame()
root.mainloop()
