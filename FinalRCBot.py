import network
import time
from umqtt.simple import MQTTClient
import ssl
import secrets
import neopixel
import json
from machine import Pin, PWM


class Motor():
    def __init__(self,m1,m2):
        self.M1 = PWM(m1, freq=100, duty_u16=0)
        self.M2 = PWM(m2, freq=100, duty_u16=0)
        self.stop()          
            
    def stop(self):
        self.M1.duty_u16(0) 
        self.M2.duty_u16(0) 

    def start(self, direction = 0, speed = 99):
        print("starting")
        if direction:
            self.M1.duty_u16(int(speed*65535/100)) 
            self.M2.duty_u16(0)
        else:
            self.M1.duty_u16(0)
            self.M2.duty_u16(int(speed*65535/100))

class MQTTDevice:
    def __init__(self):
        self.SSID = secrets.SSID
        self.PASSWORD = secrets.PWD
        
        #Left motor initialize
        self.leftM = Motor(14,27, 33, 32)
        self.leftM.stop()
        
        #Right motor initalize
        self.rightM = Motor(12,13, 32, 39)
        self.rightM.stop()
        
        #Servo initialize
        self.gate = PWM(Pin(4))
        self.gate.freq(40)
        self.current_angle = 10
        servo_angle(self.current_angle, self.servo)

        #Neopixel intialize
        self.np = neopixel.NeoPixel(Pin(15), 2)
        self.np[0] = [0,0,0]
        self.np.write()

        self.entered_time = 0
        # MQTT settings
        self.MQTT_BROKER = secrets.mqtt_url 
        self.MQTT_PORT = 8883
        self.MQTT_USERNAME = secrets.mqtt_username 
        self.MQTT_PASSWORD = secrets.mqtt_password 
        self.CLIENT_ID = "Robot"
        self.TOPIC_PUB = "/P6"

        
        self.button = Pin(35, Pin.IN, Pin.PULL_UP)
        self.button.irq(trigger = Pin.IRQ_RISING, handler = self.button_pressed)
    
    def button_pressed(self, p):
        #how do you add debounce?
        #uncomment the following - try to understand what's happening 
        now_time = time.ticks_ms()
        if(now_time - self.entered_time < 200):
            return
        self.entered_time = now_time
            
        self.client.publish(self.TOPIC_PUB, "{\"color\":[120,0,300]}")
        print("Button was pressed")
        
    def connect_wifi(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        if not self.wlan.isconnected():
            print("Connecting to WiFi...")
            print(self.SSID, self.PASSWORD)
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
        
    def subscribe(self, topic):
        self.client.subscribe(topic)
        
    def sub_cb(self, topic, msg):
        json_str = json.loads(msg)
        print(f"Received message on topic '{topic.decode()}' : '{msg.decode()}'")

        # update fan state
        if json_str["gate"] == True:
            #SERVO CODE HERE-- open the gate
            print("servo if")
        else:
            #MORE SERVO CODE HERE -- close the gate
            print("serve else")
        
        # drive/turn
        if json_str["drive"] == 1:
            print("driving forward")
            self.leftM.start(0, 20)
            self.rightM.start(0, 20)
            time.sleep(.1)
            self.leftM.stop()
            self.rightM.stop()
            
        elif json_str["drive"] == -1:
            print("driving backward")
            self.leftM.start(1, 20)
            self.rightM.start(1, 20)
            time.sleep(.1)
            self.leftM.stop()
            self.rightM.stop()
        
        if json_str["turn"] == 1:
            print("turning right")
            self.leftM.start(0, 20)
            self.rightM.start(1, 20)
            time.sleep(.1)
            self.leftM.stop()
            self.rightM.stop()
            
        elif json_str["turn"] == -1:
            print("turning left")
            self.leftM.start(1, 20)
            self.rightM.start(0, 20)
            time.sleep(.1)
            self.leftM.stop()
            self.rightM.stop()
                   

    def mqtt_connect(self):
        try:
            self.client = MQTTClient(
                client_id = self.CLIENT_ID,
                server = self.MQTT_BROKER,
                port = self.MQTT_PORT,
                user = self.MQTT_USERNAME,
                password = self.MQTT_PASSWORD,
                ssl = True,  # Enable SSL
                ssl_params = {'server_hostname': self.MQTT_BROKER}  # Important for certificate validation
            )
            self.client.set_callback(self.sub_cb)
            self.client.connect()
            
            print("MQTT Connected successfully!")
            return self.client
        except OSError as e:
            print(f"MQTT Connection failed: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

'''mqtt_obj = MQTTDevice()

if mqtt_obj.connect_wifi():
    client = mqtt_obj.mqtt_connect()
    mqtt_obj.subscribe("/Controller")'''


'''while True:
    try:
        client.check_msg()
        time.sleep(.05)
    except Exception as e:
        time.sleep(.1)
        print(f"Checking message failed: {e}")'''
            
