import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time

class CameraApp:
    def __init__(self, window):
        self.window = window
        self.window.title("USB Camera Capture")

        # Initialize OpenCV camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Unable to open the camera.")

        # Create video display area
        self.label = ttk.Label(window)
        self.label.pack()

        # Create capture button
        self.capture_btn = ttk.Button(window, text="📸 Capture", command=self.capture)
        self.capture_btn.pack(pady=10)

        # Start updating live video feed
        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.last_frame = frame.copy()  # Save the last frame
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)
        self.window.after(10, self.update_frame)  # Refresh every 10ms

    def capture(self):
        if hasattr(self, 'last_frame'):
            filename = f"image_{int(time.time())}.jpg"
            cv2.imwrite(filename, self.last_frame)
            print(f"{filename} saved.")

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

# Main program
if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
