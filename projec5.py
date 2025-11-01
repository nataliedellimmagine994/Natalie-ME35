import network
import time
from umqtt.simple import MQTTClient
import ssl
import secrets
import json
from machine import Pin
class MQTTDevice:
    def __init__(self):
        self.SSID = secrets.SSID
        self.PASSWORD = secrets.PWD
        self.entered_time = 0
        self.entered_time_btn2 = 0
        self.entered_time_btn3 = 0
        # MQTT settings
        self.MQTT_BROKER = secrets.mqtt_url
        self.MQTT_PORT = 8883
        self.MQTT_USERNAME = secrets.mqtt_username
        self.MQTT_PASSWORD = secrets.mqtt_password
        self.CLIENT_ID = "esp32_sender"  # Different client ID!
        self.TOPIC_PUB = "/ME35/bot"
        # Three buttons
        self.button = Pin(35, Pin.IN, Pin.PULL_UP)
        self.button.irq(trigger = Pin.IRQ_RISING, handler = self.button_pressed)
        self.button2 = Pin(34, Pin.IN, Pin.PULL_UP)  # Change to your button 2 pin
        self.button2.irq(trigger = Pin.IRQ_RISING, handler = self.button2_pressed)
        self.button3 = Pin(21, Pin.IN, Pin.PULL_UP)  # Change to your button 3 pin
        self.button3.irq(trigger = Pin.IRQ_RISING, handler = self.button3_pressed)
    def button_pressed(self, p):
        now_time = time.ticks_ms()
        if(now_time - self.entered_time < 200):
            return
        self.entered_time = now_time
        self.client.publish(self.TOPIC_PUB, b'{"color":[160,32,240], "note":392}')  # Purple, C note
        print("Button 1 was pressed - Purple, C note")
    def button2_pressed(self, p):
        now_time = time.ticks_ms()
        if(now_time - self.entered_time_btn2 < 200):
            return
        self.entered_time_btn2 = now_time
        self.client.publish(self.TOPIC_PUB, b'{"color":[255,0,0], "note":440}')  # Red, E note
        print("Button 2 was pressed - Red, E note")
    def button3_pressed(self, p):
        now_time = time.ticks_ms()
        if(now_time - self.entered_time_btn3 < 200):
            return
        self.entered_time_btn3 = now_time
        self.client.publish(self.TOPIC_PUB, b'{"color":[0,255,0], "note":494}')  # Green, G note
        print("Button 3 was pressed - Green, G note")
    def connect_wifi(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        if not self.wlan.isconnected():
            print("Connecting to WiFi...")
            self.wlan.connect(self.SSID, self.PASSWORD)
            timeout = 10
            while not self.wlan.isconnected() and timeout > 0:
                time.sleep(1)
                timeout -= 1
        if self.wlan.isconnected():
            print("WiFi Connected! IP:", self.wlan.ifconfig()[0])
            return True
        else:
            print("WiFi connection failed!")
            return False
    def publish(self, topic, msg):
        self.client.publish(topic, msg)
        print(f"Published message to topic '{topic}' : '{msg}'")
    def mqtt_connect(self):
        try:
            self.client = MQTTClient(
                client_id = self.CLIENT_ID,
                server = self.MQTT_BROKER,
                port = self.MQTT_PORT,
                user = self.MQTT_USERNAME,
                password = self.MQTT_PASSWORD,
                ssl = True,
                ssl_params = {'server_hostname': self.MQTT_BROKER}
            )
            self.client.connect()
            print("MQTT Connected successfully!")
            return self.client
        except OSError as e:
            print(f"MQTT Connection failed: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
mqtt_obj = MQTTDevice()
if mqtt_obj.connect_wifi():
    client = mqtt_obj.mqtt_connect()
while True:
    time.sleep(0.01)  # Much faster loop - 10ms instead of 1000ms