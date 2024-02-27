#######################################################
# Thermal camera Plotter with AMG8833 Infrared Array
# --- with interpolation routines for smoothing image
# 
# based on :
# 2021 Maker Portal LLC by Joshua Hrisko
# 2021 ladyada for Adafruit Industries
# 
# Modification to use faster colour based plotting 
# instead of matplotlib, using colours approach per 
# Adafruit implementation
# Draws to a JPEG image instead of using pygame to 
# output to a screen. This image can be streamer with 
# mjpeg-streamer
#######################################################
#
import time,sys
import math
# load AMG8833 module
import amg8833_i2c
import numpy as np
from scipy.interpolate import griddata
from colour import Color
from PIL import Image, ImageDraw

# low range of the sensor (this will be blue on the screen)
MINTEMP = 22.0

# high range of the sensor (this will be red on the screen)
MAXTEMP = 32.0

# how many color values we can have
COLOURDEPTH = 1024

# pylint: disable=invalid-slice-index
# points length = 64
points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
# grid_x, grid_y size = 1024
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
# pylint: enable=invalid-slice-index

# Use 20x20 for each pixel on the output image
pixel_width = 20
pixel_height = 20
# Image size
image_width = pixel_width * 32
image_height = pixel_height * 32

# the list of colors we can choose from
blue = Color("indigo")
# list of colours
colours = list(blue.range_to(Color("red"), COLOURDEPTH))

# create the array of color tuples in RGB format
colours = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colours]

# some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Initialization of Sensor
t0 = time.time()
sensor = []
while (time.time()-t0)<1: # wait 1sec for sensor to start
    try:
        # AD0 = GND, addr = 0x68 | AD0 = 5V, addr = 0x69
        sensor = amg8833_i2c.AMG8833(addr=0x69) # start AMG8833
    except:
        sensor = amg8833_i2c.AMG8833(addr=0x68)
    finally:
        pass
time.sleep(0.1) # wait for sensor to settle

# If no device is found, exit the script
if sensor==[]:
    print("No AMG8833 Found - Check Your Wiring")
    sys.exit(); # exit the app if AMG88xx is not found 

while True:
    # read the pixels
    pixels_in = []
    status, pixels_in = sensor.read_temp(64) # read pixels with status
    if status: # if error in pixel, re-enter loop and try again
        continue

    # Read thermistor
    therm = sensor.read_thermistor()
    
    #print(*pixels_in)
    # Get the min and max values for printing as text
    min_temp = min(pixels_in)
    max_temp = max(pixels_in)
    # list of length = 64 (8x8)
    pixels_in = [map_value(p, MINTEMP, MAXTEMP, 0, COLOURDEPTH - 1) for p in pixels_in]
    #print(*pixels_in)

    # perform interpolation - size = 1024 (32x32)
    bicubic = griddata(points, pixels_in, (grid_x, grid_y), method="cubic")

    # draw the interpolated pixels (each pixel 20x20 - final image size 640x660)
    img = Image.new('RGB', (image_width, image_height + 20)) # extra 20 height for text
    draw = ImageDraw.Draw(img)

    # draw everything
    for ix, row in enumerate(bicubic):
        for jx, pixel in enumerate(row):
            # Draw a square starting at position 20*x 20*y and finishing at position 20*x+20 20*y+20, filled with colour
            draw.rectangle((pixel_width * jx, pixel_height * ix, (pixel_width * jx) + pixel_width, (pixel_height * ix) + pixel_height), 
                           fill=colours[constrain(int(pixel), 0, COLOURDEPTH - 1)], outline=None)
    
    # Text in the empty space at the bottom
    draw.text(xy=(5, image_height + 5), text=f"Min {min_temp} Max {max_temp} Thermistor {therm}", fill=(255, 255, 255))
    
    img.save("/run/shm/stream/amg8833.jpg")

    
