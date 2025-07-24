import tkinter as tk
import board, neopixel

# NeoPixel configuration
NUM_PIXELS = 64          # Number of LEDs
PIXEL_PIN = board.D18    # Pin (10, 12, 18, or 21)
ORDER = neopixel.GRB      # Pixel color order

# Initialize NeoPixel strip
pixels = neopixel.NeoPixel(
    PIXEL_PIN,
    NUM_PIXELS,
    brightness=0.3,
    auto_write=False,
    pixel_order=ORDER
)

# Function to update NeoPixel color based on slider values
def update_color(event=None):
    r = red_slider.get()
    g = green_slider.get()
    b = blue_slider.get()
    pixels.fill((r, g, b))
    pixels.show()

# Create main window
root = tk.Tk()
root.title("NeoPixel RGB Controller")

# Red slider
red_slider = tk.Scale(
    root,
    from_=0,
    to=255,
    orient=tk.HORIZONTAL,
    label="Red",
    command=update_color
)
red_slider.pack(fill=tk.X, padx=10, pady=5)

# Green slider
green_slider = tk.Scale(
    root,
    from_=0,
    to=255,
    orient=tk.HORIZONTAL,
    label="Green",
    command=update_color
)
green_slider.pack(fill=tk.X, padx=10, pady=5)

# Blue slider
blue_slider = tk.Scale(
    root,
    from_=0,
    to=255,
    orient=tk.HORIZONTAL,
    label="Blue",
    command=update_color
)
blue_slider.pack(fill=tk.X, padx=10, pady=5)

# Start the GUI loop
root.mainloop()
