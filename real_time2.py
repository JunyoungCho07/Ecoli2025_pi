import cv2
import numpy as np
from ultralytics import YOLO

# Load YOLO model (.onnx or .pt)
model_path = '/home/admin/Desktop/best.onnx'
model = YOLO(model_path, task='detect')

# Open webcam (0 is default)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[ERROR] Cannot open camera.")
    exit()

print("[INFO] Running on CPU. Press 'q' or ESC to quit.")

# Use a consistent color for all boxes
box_color = (0, 255, 0)  # Green

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Failed to grab frame.")
        break

    # Crop center square and resize to 1024x1024
    h, w = frame.shape[:2]
    if h != 1024 or w != 1024:
        min_dim = min(h, w)
        start_x = (w - min_dim) // 2
        start_y = (h - min_dim) // 2
        frame = frame[start_y:start_y + min_dim, start_x:start_x + min_dim]
        frame = cv2.resize(frame, (1024, 1024), interpolation=cv2.INTER_AREA)

    # Convert to RGB for YOLO input
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Predict on CPU
    results = model.predict(source=img_rgb, save=False, imgsz=1024, conf=0.25, device='cpu')
    result = results[0]

    # Extract prediction data
    boxes = result.boxes.xyxy.cpu().numpy() if result.boxes else []
    classes = result.boxes.cls.cpu().numpy() if result.boxes else []
    confs = result.boxes.conf.cpu().numpy() if result.boxes else []

    # Draw boxes and labels
    for box, class_id, conf in zip(boxes, classes, confs):
        x1, y1, x2, y2 = map(int, box)
        label = f"Object {conf:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
        cv2.putText(frame, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

    # Display the result
    cv2.imshow("YOLOv11 Real-Time Detection (CPU)", frame)

    # Exit on 'q' or ESC
    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord('q'):
        print("[INFO] Quitting.")
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
