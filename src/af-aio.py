import os
import time
import ssl
import binascii
import mycamera
import wifi
import socketpool
import adafruit_requests
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError

print("CircuitPython OV5640 Camera")

aio_username = os.getenv("ADAFRUIT_AIO_USERNAME")
aio_key = os.getenv("ADAFRUIT_AIO_KEY")

if not aio_username or not aio_key:
    raise RuntimeError("Missing Adafruit IO credentials")

print(f"Connecting to {os.getenv('CIRCUITPY_WIFI_SSID')}")
wifi.radio.connect(
    os.getenv("CIRCUITPY_WIFI_SSID"),
    os.getenv("CIRCUITPY_WIFI_PASSWORD"),
)
print("Connected")

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

io = IO_HTTP(aio_username, aio_key, requests)

try:
    feed_camera = io.get_feed("camera")
except AdafruitIO_RequestError:
    feed_camera = io.create_new_feed("camera")

pycam = mycamera.MyCamera()
pycam.resolution = 3
pycam.autofocus()
print("AF Status:", pycam.autofocus_status)

def capture_send_image():
    pycam.autofocus()
    jpeg = pycam.capture_into_jpeg()
    print("Captured image")
    if jpeg is None:
        print("JPEG capture failed")
        return
    encoded_data = binascii.b2a_base64(jpeg).strip().decode("ascii")
    io.send_data(feed_camera["key"], encoded_data)
    print("Sent image")

while True:
    capture_send_image()
    time.sleep(15)
