from machine import Pin
import neopixel
import encoder
import math
import time
from machine import Pin, PWM, Timer, SoftI2C
import ustruct
from veml6040 import VEML6040

# initialize motors
pin_m1 = Pin(12, Pin.OUT)
pin_m1.value(0)
m1 = PWM(pin_m1)
m1.freq(1000)
m1.duty_u16(0)

pin_m2 = Pin(14, Pin.OUT)
pin_m2.value(0)
m2 = PWM(pin_m2)
m2.freq(1000)
m2.duty_u16(0)

def stop(M1, M2):
    M1.duty_u16(0) 
    M2.duty_u16(0) 
 
def setSpeed(M1, M2,direction = 0, speed = 100): #percentage
    if direction:
        M1.duty_u16(int(speed*65535/100)) 
        M2.duty_u16(int(speed*65535/100))
    else:
        M1.duty_u16(int(speed*65535/100))
        M2.duty_u16(int(speed*65535/100))

# initialize encoder and led
#motor = encoder.Motor(27, 14, 32,39)
#motor = encoder.Motor(27, 14, 32,39)
#np = neopixel.NeoPixel(Pin(15), 2)

# connect to I2C and color sensor
try:
    i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000) #Check for I2C pins from pinouts
    print("I2C initialized successfully.")
except Exception as e:
    print(f"Error initializing I2C: {e}")
    exit()


try:
    sensor = VEML6040(i2c)
    print("VEML6040 sensor object created.")
except Exception as e:
    print(f"Error creating VEML6040 object: {e}")
    exit()

# reads color sensor data and prints
def color_sensor():
    try:
        sensor.trigger_measurement()
        red, green, blue, white = sensor.read_rgbw()
        print(f"Red: {red}, Green: {green}, Blue: {blue}, White: {white}")
    except OSError as e:
        if e.args[0] == 19: # errno 19 is ENODEV (No such device)
            print("I2C Error: VEML6040 not responding. Check wiring.")
        else:
            print(f"I2C Read Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
while True:
    
    setSpeed(m1, m2, 1, 60)
    time.sleep(3)
    setSpeed(m1, m2, 1, 0)
    time.sleep(1)




