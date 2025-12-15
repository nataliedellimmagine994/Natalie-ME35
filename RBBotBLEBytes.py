'''
RC Defensive Soccer Robot, connected to Bluetooth joystick
ME 35 Final: Football
Written by Natalie Dell'Immagine
Sample code from Professor Milan Dahal
'''

import network
import time
import ssl
import secrets
import neopixel
import json
import servo
from encoder import Motor, Count
from machine import Pin, PWM
from BLE_CEEO import Yell, Listen

            
def stop():
    leftM.stop()
    rightM.stop()

# drives forward or backwards for given time at given speed
def drive(speed = 20, forward = True): #percentage
    if forward:
        leftM.start(1, speed)
        rightM.start(1, speed)
    else:
        leftM.start(0, speed)
        rightM.start(0, speed)
    
# turns car right for given time at given speed
def turnRight(speed = 20):
    leftM.start(0, speed)
    rightM.start(1, speed)

# turns car left for given time at given speed
def turnLeft(speed = 20):
    leftM.start(1, speed)
    rightM.start(0, speed)

def callback(data):
    global json_buffer, last_button, servo_angle, driveState

    try:


        button_press = data[0]
        if button_press != last_button:
            if servo_angle == 0:
                gateM.write_angle(180)
                servo_angle = 180
            else:
                gateM.write_angle(0)
                servo_angle = 0
            last_button = button_press

        if data[2] == 1:
            driveState = 1
        elif data[2] == 2:
            driveState = 2
        elif data[1] == 1:
            driveState = 3
        elif data[1] == 2:
            driveState = 4
        else:
            driveState = 0

    except Exception as e:
        print("Callback error:", e)
        
def peripheral(name): 
    try:
        p = Listen(name, verbose = True)
        if p.connect_up():
            p.callback = callback
            print('Connected')
            time.sleep(1)
            while p.is_connected:
                motor_update()   # <-- ALWAYS RUNS
                time.sleep(0.01)
        print('lost connection')
    except Exception as e:
        print('Error: ',e)
    finally:
        p.disconnect()
        print('closing up')

def motor_update():
    global driveState

    # Example speed
    speed = 35  

    if driveState == 3:
        leftM.start(0, speed)
        rightM.start(1, speed)
    elif driveState == 4:
        leftM.start(1, speed)
        rightM.start(0, speed)
    elif driveState == 1:
        leftM.start(1, speed)
        rightM.start(1, speed)
    elif driveState == 2:
        leftM.start(0, speed)
        rightM.start(0, speed)
    else:
        leftM.stop()
        rightM.stop()

#initializing motor 1 and 2
leftM = Motor(12,13, 33, 32)
rightM = Motor(14,27, 32, 39)
gateM = servo.Servo(4)

last_button = False
servo_angle = 0
driveState = 0 # 0 = stop, 1 = forward, 2 = reverse, 3 = right, 4 = left
json_buffer = ""
            
peripheral('Natalie')