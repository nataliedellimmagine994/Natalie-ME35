from machine import Pin, PWM
import neopixel
from encoder import Motor
import math
import time



motor = Motor(12, 13, 32, 39)


motor.setSpeed(0,100)
time.sleep(1)
motor.stop()
