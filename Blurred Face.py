import cv2

# Load the pre-trained Haar Cascade face detector
cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Open webcam (0 = default camera)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    original_frame = frame.copy()
    
    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    gray_frame = frame.copy()

    # Detect faces
    faces = cascade.detectMultiScale(
    gray,
    scaleFactor=1.05,   # smaller step between scales
    minNeighbors=4,     # fewer required neighbors
    minSize=(30, 30)    # detect smaller faces
)


    for (x, y, w, h) in faces:
        # Extract the face region
        face_region = frame[y:y+h, x:x+w]

        # Apply blur to the face region
        blurred_face = cv2.medianBlur(face_region, 35)

        # Replace the original face with blurred one
        frame[y:y+h, x:x+w] = blurred_face

        # Optional: draw rectangle around face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Show the result
    cv2.imshow('Unblurred', original_frame)
    cv2.imshow('Grayscale', gray_frame)
    cv2.imshow('Face Blurred', frame)

    # Exit with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release and close
cap.release()
cv2.destroyAllWindows()
