import tkinter as tk
import subprocess
from threading import Thread
import time
from datetime import datetime
from picamera2 import Picamera2
import os

SAVE_DIR = "/home/ecoli3/R&E/Picture/passivity"
os.makedirs(SAVE_DIR, exist_ok=True)

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())

def capture_once():
    """버튼을 클릭할 시 사진을 1장 촬영하는 코드"""
    now = datetime.now()
    filename = now.strftime("%Y.%m.%d_%H:%M:%S") + ".png"
    filepath = os.path.join(SAVE_DIR, filename)

    status_label.config(text="Processing...")
    picam2.start()
    time.sleep(2)              # 센서 워밍업
    picam2.capture_file(filepath)
    picam2.stop()

    print(f"Saved: {filepath}")
    status_label.config(text="Complete!")

def START():
    # 별도 스레드에서 한 장만 촬영
    Thread(target=capture_once, daemon=True).start()

def OPEN():
    subprocess.Popen(["xdg-open", SAVE_DIR])

root = tk.Tk()
root.title("Raspberry Pi Camera")
root.geometry("300x220")

start_button = tk.Button(root, text="Take Picture", command=START,
                         height=3, width=30, bg="#77AE60")
start_button.pack(pady=8)

view_button = tk.Button(root, text="Open Galary", command=OPEN,
                        height=3, width=30, bg="#9A9A9A")
view_button.pack(pady=8)

status_label = tk.Label(root, text="Waiting...")
status_label.pack(pady=8)

root.mainloop()
