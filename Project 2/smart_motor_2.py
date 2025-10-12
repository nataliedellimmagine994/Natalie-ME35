# Smart Motor Project
# [accelerometer, motor position, label]

from machine import Pin, PWM
import neopixel
import lis3dh
import encoder
import math
import time

# ------------------ Motor Setup ------------------
pwm_motor = PWM(Pin(12))
pwm_motor.freq(1000)
pwm_motor.duty_u16(0)

dir_pin = Pin(13, Pin.OUT)   # motor direction pin

# ------------------ System State ------------------
STATE = True  # True = training mode, False = playback mode
print("IN TRAINING MODE")

# Empty training data
data = []

# ------------------ Hardware Setup ------------------
motor = encoder.Motor(27, 14, 32, 39)
h3lis331dl = lis3dh.H3LIS331DL(sda_pin=21, scl_pin=22)
np = neopixel.NeoPixel(Pin(15), 2)

# Buttons
button_Train = Pin(35, Pin.IN, Pin.PULL_UP)
button_Play = Pin(34, Pin.IN, Pin.PULL_UP)

debounce_filter = 200
last_entered_time = 0

position1 = 0
position2 = 0

# Training step control
train_step = 0   # 0 = idle, 1 = collecting pos1 done, waiting for button, 2 = collecting pos2 done

# ------------------ Data Collection ------------------
def collect_training_data(label, duration=10):
    """Collect accelerometer + motor data for a given label over a time window."""
    global position1
    global position2
    print(f"Collecting data for label {label} for {duration} seconds...")
    start_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start_time) < duration * 1000:
        accl_val = int(h3lis331dl.read_accl_g()['x'] * 100)
        motor_pos = motor.pos()
        data.append([accl_val, motor_pos, label])
        print("Sample:", [accl_val, motor_pos, label])
        time.sleep(0.5)  # collect ~10 samples per second
    if label == 1:
        position1 = data[-1][1]
    else:
        position2 = data[-1][1]
    print(f"Finished collecting data for label {label}")


# ------------------ Global Flags ------------------
train_step = 0      # 0 = idle, 1 = collect pos1, 2 = wait for button, 3 = collect pos2
start_collection = False  # flag set by button

def trainButton(p):
    """Interrupt only sets the flag"""
    global start_collection, last_entered_time
    entered_time = time.ticks_ms()
    if time.ticks_diff(entered_time, last_entered_time) < debounce_filter:
        return
    last_entered_time = entered_time
    start_collection = True  # main loop will handle data collection


def modeButton(p):
    """Toggle between training and playback modes"""
    global STATE
    STATE = not STATE
    if STATE:
        print("IN TRAINING MODE")
    else:
        print("IN PLAYBACK MODE")
    print("Current dataset size:", len(data))


button_Train.irq(trigger=Pin.IRQ_RISING, handler=trainButton)
button_Play.irq(trigger=Pin.IRQ_RISING, handler=modeButton)

# ------------------ KNN Classifier ------------------
def k_nearest_neighbor(x, y, k=1):
    if not data:
        print("No training data yet!")
        return None

    distances = []
    for index, d in enumerate(data):
        dist = math.sqrt((x - d[0])**2 + (y - d[1])**2)
        distances.append([dist, index])

    distances.sort()
    distances = distances[:k]

    classes = [data[dist[1]][2] for dist in distances]

    # Majority vote
    counts = {}
    for c in classes:
        counts[c] = counts.get(c, 0) + 1

    col, max_count = classes[0], -1
    for c, count in counts.items():
        if count > max_count:
            max_count = count
            col = c
    return col

# ------------------ Motor Control ------------------
def move_motor_to(target_pos, duty_cycle=0.25, tolerance=2):
    pwm_val = int(duty_cycle * 65535)
    while True:
        current_pos = motor.pos()
        error = target_pos - current_pos

        if abs(error) <= tolerance:
            pwm_motor.duty_u16(0)
            break

        dir_pin.value(1 if error > 0 else 0)
        pwm_motor.duty_u16(pwm_val)
        time.sleep(0.01)

    print("Motor reached", target_pos, "current:", current_pos)
    

# ------------------ Main Loop ------------------
while True:
    if STATE:  # Training mode
        np[0] = (255, 0, 0)
        np.write()

        if start_collection:
            start_collection = False  # reset flag

            if train_step == 0:
                print("Collecting position 1 for 10s...")
                collect_training_data(label=1, duration=10)
                train_step = 1
                print("Done with pos1. Press button for pos2.")

            elif train_step == 1:
                print("Collecting position 2 for 10s...")
                collect_training_data(label=2, duration=10)
                train_step = 2
                print("Training finished!")
                
    else:
        np[0] = (0, 255, 0)  # Green
        np.write()

        accl_g = int(h3lis331dl.read_accl_g()['x'] * 100)
        motor_position = motor.pos()

        # Determine target position based on KNN
        pred = k_nearest_neighbor(accl_g, motor_position, 3)
        if pred is not None:
            print("Accel:", accl_g, "Motor:", motor_position, "Pred:", pred)

            # Choose target motor position
            if pred == 1:
                target = position1
            elif pred == 2:
                target = position2
            else:
                target = motor_position  # stay put if unknown

            # Move motor to target (blocking until reached)
            move_motor_to(target)
            
        time.sleep(1)

