from machine import Pin
import neopixel
from encoder import Motor
import math
import time
from machine import Pin, PWM, Timer, SoftI2C
import ustruct
from veml6040 import VEML6040

# initializing variables
color = 0
c_input = [0, 0, 0, 0]

#initializing motor 1 and 2
m1 = Motor(12,13, 33, 32)
m2 = Motor(14,27, 32, 39)

#initializing neopixel
np = neopixel.NeoPixel(Pin(15), 2)

# drives car straight for given time at given speed
def goStraight(timer, speed = 20): #percentage
    m1.setSpeed(1, speed) 
    m2.setSpeed(1, speed)
    time.sleep(timer)
    m1.stop()
    m2.stop()
    
# turns car right for given time at given speed
def turnRight(timer, speed = 20):
    m1.setSpeed(0, speed)
    m2.setSpeed(1, speed)
    time.sleep(timer)
    m1.stop()
    m2.stop()

# turns car left for given time at given speed
def turnLeft(timer, speed = 20):
    m1.setSpeed(1, speed)
    m2.setSpeed(0, speed)
    time.sleep(timer)
    m1.stop()
    m2.stop()

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
    
# Change sensor integration time to 40ms
IT_40MS = (0b000 << 4) # 40 ms
sensor.set_integration_time(IT_40MS)

# reads color sensor data and prints
def color_sensor():
    try:
        global color
        global c_input
        sensor.trigger_measurement()
        red, green, blue, white = sensor.read_rgbw()
        c_input[1] = red
        c_input[2] = green
        c_input[3] = blue
        c_input[0] = white
        print(f"Red: {red}, Green: {green}, Blue: {blue}, White: {white}")
        
        if white < 360:
            color = 1 # color is black
            print("black")
        else:
            color = 2 # color is white
            print("white")
        return color
    
    except OSError as e:
        if e.args[0] == 19: # errno 19 is ENODEV (No such device)
            print("I2C Error: VEML6040 not responding. Check wiring.")
        else:
            print(f"I2C Read Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# checks the color of the line and decides whether to go straight or turn left/right to refind the line
# turns right 5 times for 0.1 seconds each. if it still doesn't see the line, it turns left 10 times for 0.1 seconds each
def checkColor():
    counter = 0
    current_color = color_sensor()
    found_line = False
    closest_color = 0
    
    if current_color == 1:
        closet_color = which_color()
        if closest_color == 3:
            goStraight(0.5, 20)
            print("go straight!")
        else:
            goStraight(0.5, 20)
            print("go straight!")
            np[0] = (255, 0, 0)
            np[1] = (0, 0, 255)
            time.sleep(1)
            np[0] = (0, 0, 0)
            np[1] = (0, 0, 0)
            
    else:
        if current_color == 2:
            #if counter == 1:
            for i in range(7):
                print("turn right")
                turnRight(0.2, 20)
                current_color = color_sensor()
                time.sleep(0.1)
                if current_color != 2 and counter == 0:
                    turnRight(0.2, 20)
                    current_color = color_sensor()
                    time.sleep(0.1)
                    counter += 1
                if current_color != 2 and counter > 0:
                    found_line = True
                    break
                
            if found_line == False:
                for i in range(14):
                    print("turn Left")
                    turnLeft(0.2, 20)
                    current_color = color_sensor()
                    time.sleep(0.1)
                    if current_color != 2 and counter == 0:
                        turnLeft(0.2, 20)
                        current_color = color_sensor()
                        time.sleep(0.1)
                        counter += 1
                    if current_color != 2 and counter > 0:
                        break

# if the color is determined to be black, it checks if it is actually red, green, or blue using KNN logic
def which_color():
    global c_input 
    
    print(c_input)
    
    red = [383.375, 190.6, 143.95, 72.925]
    blue = [363.5, 165.75, 151.0125, 83.875]
    green = [371.625, 174.5125, 162.425, 72.6875]
    black = [304.4375, 134.125, 117.75, 59.5375]
    
    r_distance = math.sqrt( ((c_input[0] - red[0]) ** 2) + ((c_input[1] - red[1]) ** 2) + ((c_input[2] - red[2]) ** 2) + ((c_input[3] - red[3]) ** 2))
    b_distance = math.sqrt( ((c_input[0] - blue[0]) ** 2) + ((c_input[1] - blue[1]) ** 2) + ((c_input[2] - blue[2]) ** 2) + ((c_input[3] - blue[3]) ** 2))
    g_distance = math.sqrt( ((c_input[0] - green[0]) ** 2) + ((c_input[1] - green[1]) ** 2) + ((c_input[2] - green[2]) ** 2) + ((c_input[3] - green[3]) ** 2))
    bl_distance = math.sqrt( ((c_input[0] - black[0]) ** 2) + ((c_input[1] - black[1]) ** 2) + ((c_input[2] - black[2]) ** 2) + ((c_input[3] - black[3]) ** 2))
    
    distance = [r_distance, b_distance, g_distance, bl_distance]
    
    print(distance)
    
    rgb = min(distance)
    rgb_index = distance.index(rgb)
    
    return rgb_index

while True:
     checkColor()
     time.sleep(0.1)
     
     
     
     

