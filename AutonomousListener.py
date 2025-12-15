'''
RC Defensive Soccer Robot, connected to Bluetooth joystick
ME 35 Final: Football
Written by Natalie Dell'Immagine
Sample code from Professor Milan Dahal
'''

import network
import time
import ssl
#import secrets
import neopixel
import json
#import servo
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
    global json_buffer, last_button, servo_angle, driveState, speed

    print("Callback free:", gc.mem_free())
    
    try:
        button_press = data[0]
        if button_press != last_button:
            if servo_angle == 30:
                fly1.stop()
                fly2.stop()
                fly1.start(0, 70)
                fly2.start(0, 70)
                servo_angle = 70
            else:
                fly1.stop()
                fly2.stop()
                fly1.start(0, 70)
                fly2.start(0, 70)
                servo_angle = 30
            boot
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
            
        if data[3] == 1:
            speed = 70
        else:
            speed = 40

    except Exception as e:
        print("Callback error:", e)
        
def peripheral(name): 
    global speed
    try:
        print("Before BLE connect:", gc.mem_free())
        p = Listen(name, verbose = True)
        if p.connect_up():
            print("After connect:", gc.mem_free())
            p.callback = callback
            print('Connected')
            time.sleep(1)
            while p.is_connected:
                motor_update(speed)
                if time.ticks_ms() % 500 == 0:
                    print("Loop free:", gc.mem_free())# <-- ALWAYS RUNS
                time.sleep(0.01)
        print('lost connection')
    except Exception as e:
        print('Error: ',e)
    finally:
        p.disconnect()
        print('closing up')

def motor_update(speed):
    global driveState

    if driveState == 4:
        #left
        leftM.start(0, speed)
        rightM.start(1, speed)
    elif driveState == 3:
        #right
        leftM.start(1, speed)
        rightM.start(0, speed)
    elif driveState == 1:
        #forwards
        leftM.start(1, speed)
        rightM.start(1, speed)
    elif driveState == 2:
        #backwards
        leftM.start(0, speed)
        rightM.start(0, speed)
    else:
        #stop
        leftM.stop()
        rightM.stop()

import gc
print("Boot free:", gc.mem_free())

#initializing motor 1 and 2
leftM = Motor(33,32)
rightM = Motor(21,22)
fly1 = Motor(14,27)
fly2 = Motor(12,13)
#gateM = servo.Servo(4)

last_button = False
driveState = 0 # 0 = stop, 1 = forward, 2 = reverse, 3 = right, 4 = left
json_buffer = ""
speed = 80
servo_angle = 30

peripheral('Natalie')
