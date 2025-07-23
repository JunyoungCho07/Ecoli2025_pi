#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Raspberry Pi + USB 카메라 자동 캡처 GUI
 • START  : 5 초 간격으로 사진 저장 (SAVE_DIR)
 • PAUSE  : 캡처 중지
 • Browse : 갤러리(썸네일) on/off
 • NeoPixel 64 개를 촬영 직전 1 초간 켜고 촬영 후 소등
"""

# ── 1. 기본 설정 ───────────────────────────────────
import os, time, cv2, tkinter as tk
from threading  import Thread
from datetime   import datetime
from PIL        import Image, ImageTk
import board, neopixel                # ⇦ NeoPixel 제어

SAVE_DIR   = "/home/admin/Desktop/captured/auto"
os.makedirs(SAVE_DIR, exist_ok=True)

# ── 1‑A. NeoPixel -----------------------------------------------------------
NUM_PIXELS   = 64          # LED 개수
PIXEL_PIN    = board.D18   # 18·21 등 PWM 가능 핀
ORDER        = neopixel.GRB

pixels = neopixel.NeoPixel(
    PIXEL_PIN, NUM_PIXELS,
    brightness=0.3, auto_write=False, pixel_order=ORDER
)
ON  = (10, 10, 10)         # 희미하게 흰색
OFF = (0, 0, 0)

# ── 1‑B. 전역 상태 ----------------------------------------------------------
running   = False          # 캡처 루프 flag
cap       = None           # cv2.VideoCapture 객체
last_err  = ""             # 상태표시용 에러 메시지

# ── 2. 캡처 스레드 ─────────────────────────────────
def capture_loop():
    """running 이 True 인 동안 5 초 주기로 USB 카메라 프레임을 저장"""
    global cap, running, last_err

    # 2‑A. 카메라 초기화(한 번만)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)   # V4L2 backend 사용 권장
    if not cap.isOpened():
        last_err = "❌  USB camera open 실패"
        running = False
        return

    # (원하는 해상도로 고정하려면 예: 1920x1080)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1024)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1024)

    time.sleep(2)  # 카메라 워밍업

    while running:
        now       = datetime.now()
        filename  = now.strftime("%Y.%m.%d_%H:%M:%S") + ".png"
        filepath  = os.path.join(SAVE_DIR, filename)

        # 2‑B. NeoPixel ON → 촬영 → OFF
        pixels.fill(ON);  pixels.show()
        time.sleep(1)

        ret, frame = cap.read()
        
        time.sleep(1)
        pixels.fill(OFF); pixels.show()

        if ret:
            resized_frame = cv2.resize(frame,(1024,1024))
            cv2.imwrite(filepath, resized_frame)
            # cv2.imwrite(filepath, frame)
            print(f"Saved ➜ {filepath}")
        else:
            print("⚠️  frame capture 실패")
        time.sleep(5)      # ← 캡처 간격(초) (20분이면 1200초)

    cap.release()
    cap = None

# ── 3. GUI ────────────────────────────────────────
root = tk.Tk()
root.title("Raspberry Pi USB‑CAM App")
root.geometry("360x480")

def START():
    global running, last_err
    if running:
        return
    last_err = ""
    running  = True
    Thread(target=capture_loop, daemon=True).start()
    status_label.config(text="Processing...")

def STOP():
    global running
    running = False
    status_label.config(text="PAUSED")

# 3‑A. 버튼 영역
tk.Button(root, text="START",  height=2, width=25, bg="#77AE60",
          command=START).pack(pady=6)
tk.Button(root, text="PAUSE",  height=2, width=25, bg="#CB7777",
          command=STOP ).pack(pady=6)
tk.Button(root, text="Browse Gallery", height=1, width=15,
          command=lambda: toggle_gallery(True)).pack(pady=6)

status_label = tk.Label(root, text="Waiting...")
status_label.pack(pady=10)

# 3‑B. 갤러리 Frame(초기 숨김)
gallery_frame = tk.Frame(root, bg="#fff0f5")
gallery_frame.pack(fill="both", expand=True, padx=8, pady=8)
gallery_frame.pack_forget()

img_label  = tk.Label(gallery_frame, bg="#fff0f5")
btn_prev   = tk.Button(gallery_frame, text="◀")
btn_next   = tk.Button(gallery_frame, text="▶")

for w in (btn_prev, img_label, btn_next):
    w.pack(side="left", expand=True, padx=4, pady=4)

# ── 4. 갤러리 로직 ─────────────────────────────────
image_paths, index = [], 0

def load_image_paths():
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
    path  = image_paths[index]
    img   = Image.open(path).resize((240, 180))
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
    if not force_show and gallery_frame.winfo_manager():
        gallery_frame.pack_forget()
    else:
        load_image_paths(); show_image()
        gallery_frame.pack(fill="both", expand=True, padx=8, pady=8)

# ── 5. 상태 업데이트(에러 표시) ─────────────────────
def heartbeat():
    if last_err:
        status_label.config(text=last_err)
    root.after(500, heartbeat)
heartbeat()

root.mainloop()
