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
    
    # Subtract green and blue from red channel (Method 3)
    red_filtered = cv2.subtract(r, g)
    red_filtered = cv2.subtract(red_filtered, b)
    
    # Threshold to create binary mask
    _, red_mask = cv2.threshold(red_filtered, 50, 255, cv2.THRESH_BINARY)
    
   
    kernel = np.ones((5, 5), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
    
    # Find contours (outlines of red objects)
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create a copy of frame to draw on
    result = frame.copy()
    
    # Find the biggest contour
    if len(contours) > 0:
        # Get the contour with maximum area
        biggest_contour = max(contours, key=cv2.contourArea)
        
        # Get area of biggest contour
        area = cv2.contourArea(biggest_contour)
        
        # Only process if area is significant (filter out noise)
        if area > 500:  # Adjust this minimum area as needed
            # Draw the biggest contour
            cv2.drawContours(result, [biggest_contour], -1, (0, 255, 0), 3)
            
            # Get bounding box of biggest red object
            x, y, w, h = cv2.boundingRect(biggest_contour)
            cv2.rectangle(result, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            # Get center of the biggest object
            M = cv2.moments(biggest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(result, (cx, cy), 7, (255, 255, 255), -1)
                
                # Display info
                cv2.putText(result, f"Area: {int(area)}", (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(result, f"Center: ({cx}, {cy})", (x, y + h + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    # Show results
    cv2.imshow("Original Camera", frame)
    cv2.imshow("Red Mask", red_mask)
    cv2.imshow("Biggest Red Object", result)
    
    # Press 'q' to quit and save
    if cv2.waitKey(1) & 0xFF == ord('q'):
        #cv2.imwrite('/Users/mdahal01/Downloads/test_original.jpg', frame)
        #cv2.imwrite('/Users/mdahal01/Downloads/test_red_mask.jpg', red_mask)
        #cv2.imwrite('/Users/mdahal01/Downloads/test_biggest_red.jpg', result)
        print("Images saved!")
        break

# Release everything when done
cam.release()
cv2.destroyAllWindows()
