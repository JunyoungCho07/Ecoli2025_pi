import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time
import board, neopixel, time

NUM_PIXELS   = 64          # LED 개수
PIXEL_PIN    = board.D18   # 10·12·18·21 중 선택
ORDER        = neopixel.GRB

pixels = neopixel.NeoPixel(
    PIXEL_PIN, NUM_PIXELS,
    brightness=0.3, auto_write=False, pixel_order=ORDER
)

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
        self.capture_btn = ttk.Button(window, text="Capture", command=self.capture)
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
            filename = f"/home/admin/Desktop/captured/image_{int(time.time())}.png" # have to change save path
            resized_frame = cv2.resize(self.last_frame,(1024,1024))
            cv2.imwrite(filename, resized_frame)
            print(f"{filename} saved.")

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

# Main program
if __name__ == "__main__":
    on = (255,255,255)
    pixels.fill(on)
    pixels.show()
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
