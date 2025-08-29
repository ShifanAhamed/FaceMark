"""
Simple Webcam Access Script using OpenCV
This script opens the default camera, displays live video, and allows safe exit with 'q' key
"""

import cv2

def main():
    """
    Main function to handle webcam access and display
    """
    
    # Initialize the default camera (camera index 0)
    # cv2.VideoCapture(0) opens the first available camera
    camera = cv2.VideoCapture(0)
    
    # Check if camera was opened successfully
    if not camera.isOpened():
        print("Error: Could not open camera")
        print("Please check if camera is connected and not being used by another application")
        return
    
    print("Camera opened successfully!")
    print("Press 'q' to quit the application")
    
    # Main loop to capture and display video frames
    while True:
        # Capture frame-by-frame from the camera
        # ret is a boolean indicating if frame was captured successfully
        # frame contains the actual image data
        ret, frame = camera.read()
        
        # Check if frame was captured successfully
        if not ret:
            print("Error: Failed to capture frame from camera")
            break
        
        # Display the captured frame in a window
        # 'Live Camera Feed' is the window title
        cv2.imshow('Live Camera Feed', frame)
        
        # Wait for key press (1ms timeout)
        # cv2.waitKey(1) returns the ASCII value of the pressed key
        # & 0xFF ensures we get only the last 8 bits (handles 64-bit systems)
        key = cv2.waitKey(1) & 0xFF
        
        # Check if 'q' key was pressed to quit
        if key == ord('q'):
            print("Quit key pressed. Exiting...")
            break
    
    # Clean up and release resources
    print("Releasing camera and closing windows...")
    
    # Release the camera object to free up the camera for other applications
    camera.release()
    
    # Close all OpenCV windows
    cv2.destroyAllWindows()
    
    print("Camera released and windows closed successfully!")

# Entry point of the script
if __name__ == "__main__":
    main()