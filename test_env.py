# test_env.py
from PIL import Image, ImageTk
# import picamera2
from picamera2 import Picamera2
import board, neopixel

print("Pillow:", Image.__version__)
# print("Camera:", picamera2.__version__) #dosen't work
pixels = neopixel.NeoPixel(board.D18, 8, auto_write=False)
pixels.fill((0, 50, 0)); pixels.show()
print("NeoPixel OK")
