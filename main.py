import WIFI_CONFIG
from network_manager import NetworkManager
import time
import uasyncio
import urequests as requests
import ujson
from urllib import urequest
from picographics import PicoGraphics, DISPLAY_INKY_PACK
import ntptime
import machine
import json
import gc

rtc = machine.RTC()


url = 'https://polite-ground-030dc3103.4.azurestaticapps.net/api/v1/event/6424-f827'
tz_offset = 10

wifi_index = 0

info_count = 0
info_error = 0
info_retry = 0

graphics = PicoGraphics(DISPLAY_INKY_PACK)
WIDTH, HEIGHT = graphics.get_bounds()

# Display
graphics = PicoGraphics(DISPLAY_INKY_PACK)
WIDTH, HEIGHT = graphics.get_bounds()
graphics.set_update_speed(3)
graphics.set_font("sans")
graphics.set_thickness(2)


def status_handler(mode, status, ip):
    graphics.set_update_speed(2)
    graphics.set_pen(15)
    graphics.clear()
    graphics.set_pen(0)
    graphics.text("SSID: {}".format(WIFI_CONFIG.SSID[wifi_index]), 2, 20, scale=1)
    status_text = "Connecting..."
    if status is not None:
        if status:
            status_text = "Connected!"
        else:
            status_text = "Not connected!"

    graphics.text(status_text, 2, 50, scale=1)
    graphics.text("{}".format(ip), 2, 80, scale=1)
    graphics.update()
    
    
def draw_clock():
    gc.collect()
    hms = "{:02}:{:02}".format(hour, minute)
    ymd = "{:04}/{:02}/{:02}".format(year, month, day)
    info = f'I({info_count}) R({info_retry}) E({info_error})'

    hms_width = graphics.measure_text(hms, 1.8)
    hms_offset = int((WIDTH / 2) - (hms_width / 2))

    ymd_width = graphics.measure_text(ymd, 1.0)
    ymd_offset = int((WIDTH / 2) - (ymd_width / 2))
    
    info_width = ymd_width = graphics.measure_text(info, 0.6)
    info_offset = int((WIDTH / 2) - (info_width / 2))

    graphics.set_pen(15)
    graphics.clear()
    graphics.set_pen(0)
    graphics.set_thickness(2)
    
    graphics.text(hms, hms_offset, 30, scale=1.8)
    graphics.text(ymd, ymd_offset, 70, scale=1.0)
    graphics.text(info, info_offset, 104, scale=0.6)
    
    if network_manager.isconnected:
        graphics.text('+', WIDTH-20, 6, scale=0.8)
    else:
        graphics.text('-', WIDTH-20, 6, scale=0.8)

    graphics.update()
        
        
def set_time():
    sec = ntptime.time()
    timezone_hour = tz_offset
    timezone_sec = timezone_hour * 3600
    sec = int(sec + timezone_sec)
    (year, month, day, hours, minutes, seconds, weekday, yearday) = time.localtime(sec)
    rtc.datetime((year, month, day, 0, hours, minutes, seconds, 0))
    

def get_event_info():
    global info_error, info_count, info_retry
    if not network_manager.isconnected:
        return
    
    retry = 0
    while retry < 3:
        retry += 1
        try:
            gc.collect()
            info_count += 1
            response = requests.get(url, timeout=10)
            break
        except OSError as error:
            # [Errno 110] ETIMEDOUT 110
            info_retry += 1
        except Exception as exc:
            info_error += 1
            break
        
def network_connect():
    global wifi_index
    while True:
        try:
            uasyncio.get_event_loop().run_until_complete(network_manager.client(WIFI_CONFIG.SSID[wifi_index], WIFI_CONFIG.PSK[wifi_index]))
            if network_manager.isconnected:
                break
        except Exception:
            wifi_index += 1
            wifi_index = wifi_index % len(WIFI_CONFIG.SSID)


network_manager = NetworkManager(WIFI_CONFIG.COUNTRY, status_handler=status_handler, client_timeout=15)

network_connect()   

set_time()

graphics.set_update_speed(2)

# Define the time intervals for each function
interval_info = 1
interval_show = 1

year, month, day, wd, hour, minute, second, _ = rtc.datetime()
#draw_clock()

# Start time
start_time = time.time()

while True:
    current_time = time.time() - start_time

    if current_time >= interval_info:
        get_event_info()
        interval_info += 2
        
    if current_time >= interval_show:
        year, month, day, wd, hour, minute, second, _ = rtc.datetime()
        draw_clock()
        interval_show += 60

    # Sleep for a short duration to avoid high CPU usage
    time.sleep(1)

