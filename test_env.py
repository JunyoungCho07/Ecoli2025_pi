# test_env.py
from PIL import Image, ImageTk
from picamera2 import Picamera2
import board, neopixel

print("Pillow:", Image.__version__)
print("Camera:", Picamera2.version)
pixels = neopixel.NeoPixel(board.D18, 8, auto_write=False)
pixels.fill((0, 50, 0)); pixels.show()
print("NeoPixel OK")
