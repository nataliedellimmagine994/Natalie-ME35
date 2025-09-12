import urequests
import secrets
import network
import time

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

url = "https://www.meteosource.com/api/v1/free/point?place_id=postal-us-02155&sections=current&language=en&units=auto&key=ounlo9e0d9ugrjd1ylahu6xhfl1ksvau7qj3t6hi"

response = urequests.get(url)

if response.status_code == 200:
    data = response.json()
    wind = data["current"]["wind"]["speed"]
    print(wind)
else:
    print("Error:", response.status_code)
    print(response.text)

response.close()