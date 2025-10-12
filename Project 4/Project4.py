# -----------------------------------------------------------------------------
# MicroPython Script for 2-DOF Arm Drawing (IK)
# Goal: Trace a triangle shape using Inverse Kinematics (IK)
# Bonus: DC Motors (M1, M2) act as Angle Indicators for Servo 1 and Servo 2
# -----------------------------------------------------------------------------

import math
import time
import machine
# Importing the necessary classes from the external encoder.py file
from encoder import Count, Motor 

# -----------------------------------------------------------------------------
# 1. Constants and Calibration
# -----------------------------------------------------------------------------

# Arm Physical Dimensions (UPDATED)
ARM_LENGTH_1 = 61.3 # Length of the first link
ARM_LENGTH_2 = 70.0  # Length of the second link
# Max reach R_max = 131.3, Min reach R_min = 8.7

# Servo PWM settings for hobby servos: 50Hz frequency.
SERVO_FREQ = 50

# PWM 16-bit Calibration (Duty cycle range 0 to 65535)
MIN_DUTY_16BIT = 1500  # Duty cycle for 0 degrees (approx 0.5ms pulse)
MAX_DUTY_16BIT = 8000  # Duty cycle for 180 degrees (approx 2.5ms pulse)

# DC Motor Indicator Calibration (0-180 degree angle to 0-65535 PWM duty)
# This sets the intensity of the DC motor to represent the angle.
INDICATOR_MAX_DUTY = 30000 

# Triangle Path Generation
STEPS_PER_SEGMENT = 100
PATH_DELAY_MS = 0.015 # Time to wait between each point for smooth motion (15ms)

# Drawing Offset/Translation (Ensures the drawing is far from origin)
X_OFFSET = 50.0  # Global offset applied to all X coordinates
Y_OFFSET = 50.0  # Global offset applied to all Y coordinates

# Triangle Vertices (UPDATED to be smaller and avoid arm crossover)
# The new 36x18 triangle is scaled down further for stability.
TRIANGLE_VERTICES = [
    (0.0, 0.0),    # V1: Relative origin point
    (36.0, 0.0),   # V2: Moves along the X-axis (Base of the triangle)
    (36.0, 18.0)   # V3: Moves up the Y-axis (Vertical side)
]


# -----------------------------------------------------------------------------
# 2. Control Functions
# -----------------------------------------------------------------------------

def set_servo_angle(pwm_obj, angle):
    """Converts angle (0-180 degrees) to PWM duty cycle (0-65535 range) and sets it."""
    # Clamp angle to safe operational limits (0 to 180 degrees)
    angle = max(0, min(180, angle))
    
    # Linear mapping: maps angle 0-180 to duty cycle MIN_DUTY-MAX_DUTY
    duty_16bit = int(MIN_DUTY_16BIT + (MAX_DUTY_16BIT - MIN_DUTY_16BIT) * angle / 180)
    
    pwm_obj.duty_u16(duty_16bit)
    return angle # Return the clamped angle

def set_motor_indicator(motor_obj, angle):
    """Sets the DC motor speed proportional to the joint angle (0-180 degrees)."""
    duty = int(INDICATOR_MAX_DUTY * angle / 180)
    motor_obj.M1.duty_u16(duty)
    motor_obj.M2.duty_u16(0)
    
    print(motor1.pos())
    print(motor2.pos())


def inverse_kinematics(x, y, l1, l2):
    """
    Calculates the two joint angles (theta1, theta2) for a given (x, y) target.
    Returns (theta1_deg, theta2_deg) or None if the point is unreachable.
    Uses the 'elbow-down' solution.
    """
    try:
        r2 = x**2 + y**2
        
        # Calculate theta2 (Elbow angle, relative to L1) using Law of Cosines
        cos_theta2 = (r2 - l1**2 - l2**2) / (2 * l1 * l2)
        
        # Check reachability (must be between -1 and 1)
        if cos_theta2 > 1.0 or cos_theta2 < -1.0:
            return None, None 

        # We take the elbow-down solution (positive arccos)
        theta2_rad = math.acos(cos_theta2) 
        
        # Calculate theta1 (Base angle)
        alpha = math.atan2(y, x) 
        beta = math.atan2(l2 * math.sin(theta2_rad), l1 + l2 * math.cos(theta2_rad))
        
        theta1_rad = alpha - beta
        
        # Convert to degrees
        theta1_deg = math.degrees(theta1_rad)
        theta2_deg = math.degrees(theta2_rad)
        
        # Clamp theta1 to positive angle (0-180 range assumed for arm base)
        if theta1_deg < 0:
            theta1_deg += 180 
        
        return theta1_deg, theta2_deg

    except ValueError:
        return None, None
    except Exception as e:
        print(f"IK Error: {e}")
        return None, None

def generate_path(vertices, steps_per_segment, x_offset, y_offset):
    """Generates a dense list of (x, y) points along the triangle segments with an offset."""
    path = []
    
    # Apply offset to the vertices for the calculation loop
    offset_vertices = []
    for x, y in vertices:
        offset_vertices.append((x + x_offset, y + y_offset))
        
    # Iterate through segments (V1->V2, V2->V3, V3->V1)
    for i in range(len(offset_vertices)):
        start_x, start_y = offset_vertices[i]
        end_x, end_y = offset_vertices[(i + 1) % len(offset_vertices)] # Wrap around to start
        
        for step in range(steps_per_segment):
            t = step / steps_per_segment # Interpolation factor (0 to 1)
            
            # Linear interpolation (LERP)
            x = start_x + t * (end_x - start_x)
            y = start_y + t * (end_y - start_y)
            path.append((x, y))
            
    return path

# -----------------------------------------------------------------------------
# 3. Hardware Initialization
# -----------------------------------------------------------------------------

# Servo PWM setup
pwm1 = machine.PWM(machine.Pin(19), freq=SERVO_FREQ) # Base joint PWM (Servo 1)
pwm2 = machine.PWM(machine.Pin(5), freq=SERVO_FREQ)  # Elbow joint PWM (Servo 2)

# DC Motor/Encoder setup
# Motor 1: Encoder (32, 33), Motor PWM (12, 13) -> Indicator for Servo 1 Angle
# Motor 2: Encoder (39, 32), Motor PWM (14, 27) -> Indicator for Servo 2 Angle
motor1 = Motor(12, 13, 32, 33) 
motor2 = Motor(14, 27, 39, 32) 

# Generate the full triangle path (now passes the offset values)
triangle_path = generate_path(TRIANGLE_VERTICES, STEPS_PER_SEGMENT, X_OFFSET, Y_OFFSET)

# -----------------------------------------------------------------------------
# 4. Drawing Control Loop
# -----------------------------------------------------------------------------

print("--- 2-DOF Arm Drawing: Triangle Path ---")
print(f"Arm Specs: L1={ARM_LENGTH_1} | L2={ARM_LENGTH_2}")
print(f"Drawing Offset: X={X_OFFSET} | Y={Y_OFFSET}")
print(f"Path Length: {len(triangle_path)} points.")

# --- Homing Step: Move to the first point before starting the loop ---
if triangle_path:
    start_x, start_y = triangle_path[0]
    theta1_start, theta2_start = inverse_kinematics(start_x, start_y, ARM_LENGTH_1, ARM_LENGTH_2)
    
    if theta1_start is not None and theta2_start is not None:
        print(f"Homing arm to start point: ({start_x:.1f}, {start_y:.1f})")
        set_servo_angle(pwm1, theta1_start)
        set_servo_angle(pwm2, theta2_start)
        set_motor_indicator(motor1, theta1_start)
        set_motor_indicator(motor2, theta2_start)
        time.sleep(1.0) # Wait 1 second for arm to settle
    else:
        print("Warning: First point of path is unreachable. Cannot home. Starting from current position.")

print("Starting drawing loop. Use long exposure camera now!")
print("Ctrl+C to stop.")

try:
    for x_target, y_target in triangle_path:
        
        # 1. Inverse Kinematics: Calculate required angles
        theta1_deg, theta2_deg = inverse_kinematics(x_target, y_target, ARM_LENGTH_1, ARM_LENGTH_2)
        
        if theta1_deg is None or theta2_deg is None:
            # If the point is unreachable (or IK failed), skip this step and continue
            continue
        
        # 2. Servo Control: Move the arm to the new position
        clamped_angle_1 = set_servo_angle(pwm1, theta1_deg)
        clamped_angle_2 = set_servo_angle(pwm2, theta2_deg)
        
        # 3. BONUS: Update DC Motor Angle Indicators
        set_motor_indicator(motor1, clamped_angle_1)
        set_motor_indicator(motor2, clamped_angle_2)
        
        # Optional: Print position
        # print(f"Target ({x_target:.1f}, {y_target:.1f}) -> A1: {clamped_angle_1:.1f}°, A2: {clamped_angle_2:.1f}°")

        time.sleep(PATH_DELAY_MS) # Wait for movement

    print("\nDrawing complete! Path traced once.")
    
    motor1.stop()
    motor2.stop()
    
except KeyboardInterrupt:
    print("\nScript terminated by user. Deinitializing PWM.")

finally:
    # Ensure all PWM outputs are turned off
    pwm1.deinit() 
    pwm2.deinit()
    # Also stop DC motors
    motor1.stop()
    motor2.stop()
