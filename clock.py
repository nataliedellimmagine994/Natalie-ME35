import servo
import time
import machine
import urequests
import secrets
import network

servo1= servo.Servo(machine.Pin(4))

button = machine.Pin(34, machine.Pin.IN, machine.Pin.PULL_UP)

mode = 0

def wifi_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(secrets.SSID, secrets.PWD)
        while not sta_if.isconnected():
            time.sleep(1)
    print('network config:', sta_if.ifconfig())

wifi_connect()


def handle_button(pin):
    global mode
    if mode == 0:
        mode = 1
        time.sleep(0.1)
    else:
        mode = 0
        time.sleep(0.1)
        
    #print(mode)
    
button.irq(trigger=machine.Pin.IRQ_FALLING, handler=handle_button)

while True:
    if mode == 0:
        now = time.localtime()
        angle = 180 - (3*(now[5]+1))
        servo1.write_angle(angle)
        print("Second: ", now[5]+1) 
        time.sleep(1)
    else:
        print("api here")
        url = "https://www.meteosource.com/api/v1/free/point?place_id=postal-us-02155&sections=current&language=en&units=auto&key=ounlo9e0d9ugrjd1ylahu6xhfl1ksvau7qj3t6hi"

        response = urequests.get(url)

        if response.status_code == 200:
            data = response.json()
            wind = data["current"]["wind"]["speed"]
            angle_wind = int(180 - (12*wind))
            servo1.write_angle(angle_wind)
        else:
            print("Error:", response.status_code)
            print(response.text)

        response.close()
    
