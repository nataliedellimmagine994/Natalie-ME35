'''
start in train mode, with a blue light
    have initial values of data hard coded
    add in more data points -- print that each one has been added, w a button press
when you press other button, switch to play mode, w a red light
    as you tilt the accelerometer side to side, motor should follow
'''
# [accelerometer, motor position, position]

from machine import Pin
import neopixel
import lis3dh
import encoder
import math
import time
from machine import Pin, PWM

# Initializes the motor and turns it off
pwm_motor = PWM(Pin(12))
pwm_motor.freq(1000)
pwm_motor.duty_u16(0)

#initializes the direction of the motor
dir_pin = Pin(13, Pin.OUT)

# Initializes the state
STATE = True # train mode; false = playback mode
print("IN TRAINING MODE")

#data =[]
count = 1
data = [[-120,600,1],[-85,700,1], [-91,650,1],[-92,500,1],[98,-200,2], [102,-287,2],[111,-157,2],[89,-318,2]]

# Initialize motor, accelerometer, and LED
motor = encoder.Motor(27, 14, 32,39)
h3lis331dl = lis3dh.H3LIS331DL(sda_pin=21, scl_pin=22)
np = neopixel.NeoPixel(Pin(15), 2)

#Initialize buttons, one to change state, one to train motor
button_Train =  Pin(35, Pin.IN, Pin.PULL_UP)
button_Play = Pin(34, Pin.IN, Pin.PULL_UP)

debounce_filter = 100
last_entered_time = 0

# function for the training button
# 
def trainButton(p):
    global data, last_entered_time, count
    entered_time = time.ticks_ms()
    if (time.ticks_ms() - last_entered_time) < debounce_filter:
        return
    last_entered_time = entered_time
    data.append([
        h3lis331dl.read_accl_g()['x'],
        motor.pos(), (count % 2)
    ])
    print("added data point to group")
    count += 1
    
    
def modeButton(p):
    global STATE
    if STATE == False:
        STATE = True
        print("IN PLAYBACK MODE")
    else:
        STATE = False
        print("IN TRAINING MODE")
    print(data)

    
button_Train.irq(trigger=Pin.IRQ_RISING, handler=trainButton)
button_Play.irq(trigger=Pin.IRQ_RISING, handler=modeButton)


#for K = 1
def nearest_neighbor(x,y):
    dist_min = 100000
    for index, d in enumerate(data):
        dist = math.sqrt((x-d[0])**2 + (y-d[1])**2)
        if(dist < dist_min):
            dist_min = dist
            col = d[2]
        
    return col


# for KNN
def k_nearest_neighbor(x, y, k=1):
    distances = []
    for index, d in enumerate(data):
        dist = math.sqrt((x - d[0])**2 + (y - d[1])**2)
        distances.append([dist, index])
    
    distances.sort()
    distances = distances[:k]  # get k nearest
    
    classes = [data[dist[1]][2] for dist in distances]
    print("k classes", classes)

    # Compute the most common class manually
    counts = {}
    for c in classes:
        counts[c] = counts.get(c, 0) + 1
    
    # Find the class with the maximum count
    max_count = -1
    col = classes[0]
    for c, count in counts.items():
        if count > max_count:
            max_count = count
            col = c

    return col

def move_motor_to(target_pos, direction, duty_cycle=0.25, tolerance=2):
    """
    Move motor to target position at a fixed duty cycle with direction control.
    """
    pwm_val = int(duty_cycle * 65535)
    
    while True:
        current_pos = motor.pos()
        error = target_pos - current_pos
        
        if abs(error) <= tolerance:
            pwm_motor.duty_u16(0)  # stop motor
            break
        
        dir_pin.value(direction)
        pwm_motor.duty_u16(pwm_val)
        time.sleep(0.01)
        pwm_motor.duty_u16(0)
        print("Motor moved")
        print(target_pos)
        print(current_pos)


while True:
    if STATE == True: #train mode
        np[0]=(255,0,0)
        np.write()
        
    else: #playback mode
        np[0]=(0,255,0)
        np.write()
        #do something else
        accl_g = h3lis331dl.read_accl_g()['x']
        motor_position = motor.pos()
         
        what_position = k_nearest_neighbor(accl_g, motor_position, 3)
        print("Accel:", accl_g, "Motor:", motor_position, "Pred:", what_position)
        
        if what_position == 1:
            move_motor_to(600)
        else:
            move_motor_to(-200)
        
        
        time.sleep(0.1)