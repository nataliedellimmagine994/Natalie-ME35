import cv2
import numpy as np

cam = cv2.VideoCapture(1)

# Check if camera opened successfully
if not cam.isOpened():
    print("Error: Could not open camera")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cam.read()
    
    if not ret:
        print("Error: Failed to capture frame")
        break
    
    # Split into BGR channels
    b, g, r = cv2.split(frame)
    
    red_filtered = cv2.subtract(r, g)
    red_filtered = cv2.subtract(red_filtered, b)
    
    # Threshold to create binary mask
    _, red_mask = cv2.threshold(red_filtered, 50, 255, cv2.THRESH_BINARY)
    

    # Apply mask to show only red parts
    red_only = cv2.bitwise_and(frame, frame, mask=red_mask)
    
    # Show original and red detection side by side
    cv2.imshow("Original Camera", frame)
    cv2.imshow("Red Mask", red_mask)
    cv2.imshow("Red Parts Only", red_only)
    
    # Press 'q' to quit and save
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.imwrite('/Users/mdahal01/Downloads/test_original.jpg', frame)
        cv2.imwrite('/Users/mdahal01/Downloads/test_red_mask.jpg', red_mask)
        cv2.imwrite('/Users/mdahal01/Downloads/test_red_only.jpg', red_only)
        print("Images saved!")
        break

# Release everything when done
cam.release()
cv2.destroyAllWindows()
