# # CircuitPython 호환 계층(Blinka) + NeoPixel 드라이버 + DMA 라이브러리
# sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
# sudo python3 -m pip install --force-reinstall adafruit-blinka
# ``` :contentReference[oaicite:5]{index=5}  

# > **루트 권한 필수**: DMA · PWM 자원을 직접 쓰기 때문에 `sudo python3 …` 로 실행해야 합니다. :contentReference[oaicite:6]{index=6}  

# ---

# ### 4단계 – 첫 구동 테스트  
# ```python
import board, neopixel, time

NUM_PIXELS   = 64          # LED 개수
PIXEL_PIN    = board.D18   # 10·12·18·21 중 선택
ORDER        = neopixel.GRB

pixels = neopixel.NeoPixel(
    PIXEL_PIN, NUM_PIXELS,
    brightness=0.3, auto_write=False, pixel_order=ORDER
)

# while True:
#     # 빨간색 → 초록 → 파랑 → 레인보우 순환
#     for color in [(255,0,0), (0,255,0), (0,0,255)]:
#         pixels.fill(color); pixels.show(); time.sleep(1)

#     for j in range(256):
#         for i in range(NUM_PIXELS):
#             rc_index = (i*256//NUM_PIXELS)+j
#             pixels[i] = (
#                 rc_index & 255,
#                 255 - (rc_index & 255),
#                 (rc_index*3) & 255
#             )
#         pixels.show()
#         time.sleep(0.002)
while True:
    # 빨간색 → 초록 → 파랑 → 레인보우 순환
    on = (255,255,255)
    pixels.fill(on)
    pixels.show()
    time.sleep(1)
    off = (0,0,0)
    pixels.fill(off)
    pixels.show()
    time.sleep(1)


    # for j in range(256):
    #     for i in range(NUM_PIXELS):
    #         rc_index = (i*256//NUM_PIXELS)+j
    #         pixels[i] = (
    #             rc_index & 255,
    #             255 - (rc_index & 255),
    #             (rc_index*3) & 255
    #         )
    #     pixels.show()
    #     time.sleep(0.002)
# ``` :contentReference[oaicite:7]{index=7}  

# *파일 저장 후*  
# ```bash
# sudo python3 neopixel_test.py
