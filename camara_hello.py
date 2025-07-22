import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time

class CameraApp:
    def __init__(self, window):
        self.window = window
        self.window.title("USB 카메라 캡처")

        # OpenCV 카메라 초기화
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("카메라를 열 수 없습니다.")

        # 화면 구성
        self.label = ttk.Label(window)
        self.label.pack()

        self.capture_btn = ttk.Button(window, text="📸 캡처", command=self.capture)
        self.capture_btn.pack(pady=10)

        # 실시간 영상 업데이트
        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.last_frame = frame.copy()  # 마지막 프레임 저장
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)
        self.window.after(10, self.update_frame)  # 10ms마다 업데이트

    def capture(self):
        if hasattr(self, 'last_frame'):
            filename = f"image_{int(time.time())}.jpg"
            cv2.imwrite(filename, self.last_frame)
            print(f"{filename} 저장됨")

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

# 실행
if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
