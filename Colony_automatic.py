import tkinter as tk
import subprocess
from threading import Thread
import time
from datetime import datetime
from picamera2 import Picamera2
from PIL import Image, ImageTk
import os

# ── 1. 기본 설정 ───────────────────────────────────
SAVE_DIR = "/home/ecoli3/R&E/Picture/automatic"
os.makedirs(SAVE_DIR, exist_ok=True)

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())

running = False

# ── 2. 캡처 스레드 ─────────────────────────────────
def capture_loop():
    global running
    while running:
        now = datetime.now()
        filename = now.strftime("%Y.%m.%d_%H:%M:%S") + ".png"
        filepath = os.path.join(SAVE_DIR, filename)

        picam2.start();  time.sleep(2)
        picam2.capture_file(filepath)
        picam2.stop()

        print(f"Saved ➜ {filepath}")
        time.sleep(20 * 60)           # 20 분 간격

def START():
    global running
    if not running:
        running = True
        Thread(target=capture_loop, daemon=True).start()
        status_label.config(text="Processing...")

def STOP():
    global running
    running = False
    status_label.config(text="PAUSED")

# ── 3. 메인 GUI ────────────────────────────────────
root = tk.Tk()
root.title("Raspberry Pi App")
root.geometry("360x480")

# 3-1 버튼 영역
tk.Button(root, text="START",  height=2, width=25, bg="#77AE60",
          command=START).pack(pady=6)
tk.Button(root, text="PAUSE",  height=2, width=25, bg="#CB7777",
          command=STOP ).pack(pady=6)
tk.Button(root, text="Browse Gallery", height=1, width=15,
          command=lambda: toggle_gallery(True)).pack(pady=6)

status_label = tk.Label(root, text="Waiting...")
status_label.pack(pady=10)

# 3-2 갤러리 영역(처음엔 숨김)
gallery_frame = tk.Frame(root, bg="#fff0f5")
gallery_frame.pack(fill="both", expand=True, padx=8, pady=8)
gallery_frame.pack_forget()          # <-- 숨겨 두기

img_label  = tk.Label(gallery_frame, bg="#fff0f5")
btn_prev   = tk.Button(gallery_frame, text="◀")
btn_next   = tk.Button(gallery_frame, text="▶")

for w in (btn_prev, img_label, btn_next):
    w.pack(side="left", expand=True, padx=4, pady=4)

# ── 4. 갤러리 로직 ─────────────────────────────────
image_paths, index = [], 0           # 전역처럼 쓰기 위해 목록과 위치 저장

def load_image_paths():
    """SAVE_DIR에 있는 이미지 파일 목록을 갱신"""
    global image_paths, index
    image_paths = sorted(
        f for f in (os.path.join(SAVE_DIR, n) for n in os.listdir(SAVE_DIR))
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    )
    index = 0

def show_image():
    if not image_paths:
        img_label.config(text="No images", image="", compound="center")
        return
    path = image_paths[index]
    img = Image.open(path).resize((240, 180))
    photo = ImageTk.PhotoImage(img)
    img_label.config(image=photo);  img_label.image = photo

def prev_img():
    global index
    index = (index - 1) % len(image_paths)
    show_image()

def next_img():
    global index
    index = (index + 1) % len(image_paths)
    show_image()

btn_prev.config(command=prev_img)
btn_next.config(command=next_img)

def toggle_gallery(force_show=False):
    """갤러리 Frame 보이기/숨기기 토글"""
    if not force_show and gallery_frame.winfo_manager():
        gallery_frame.pack_forget()
    else:
        load_image_paths()
        show_image()
        gallery_frame.pack(fill="both", expand=True, padx=8, pady=8)

root.mainloop()