import tkinter as tk
import numpy as np
import cv2
from PIL import ImageGrab

def show_frame():
    global running, circle, stop_flag#, #detection_confirmed, detection_time
    
    # Capture frame-by-frame
    captured_frame = np.array(ImageGrab.grab(bbox=(0, 30, width // 2, height)))
    captured_frame = cv2.cvtColor(src=captured_frame, code=cv2.COLOR_BGR2RGB)
    output_frame = captured_frame.copy()
    #output_frame = captured_frame
    
    # Convert original image to BGR, since Lab is only available from BGR
    captured_frame_bgr = cv2.cvtColor(captured_frame, cv2.COLOR_BGRA2BGR)
    # First blur to reduce noise prior to color space conversion
    captured_frame_bgr = cv2.medianBlur(captured_frame_bgr, 3)
    # Convert to Lab color space, we only need to check one channel (a-channel) for red here
    captured_frame_lab = cv2.cvtColor(captured_frame_bgr, cv2.COLOR_BGR2Lab)
    # Threshold the Lab image, keep only the red pixels
    captured_frame_lab_red = cv2.inRange(captured_frame_lab, np.array([20, 150, 150]), np.array([190, 255, 255]))
    # Second blur to reduce more noise, easier circle detection
    captured_frame_lab_red = cv2.GaussianBlur(captured_frame_lab_red, (5, 5), 2, 2)
    # Use the Hough transform to detect circles in the image
    circles = cv2.HoughCircles(captured_frame_lab_red, cv2.HOUGH_GRADIENT, 1, captured_frame_lab_red.shape[0] / 8, param1=100, param2=18, minRadius=5, maxRadius=60)
    
    # If we have extracted a circle, draw an outline
    # We only need to detect one circle here, since there will only be one reference object
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        #if detection_confirmed and (cv2.getTickCount() - detection_time) / cv2.getTickFrequency() >= 3:
        cv2.circle(output_frame, center=(circles[0, 0], circles[0, 1]), radius=circles[0, 2], color=(0, 255, 0), thickness=2)
        #else:
            # Circle detected, but less than 3 seconds have passed since confirmation
            # Reset the detection confirmation
            #detection_confirmed = False
            #detection_time = 0
            
    cv2.imshow('frame', output_frame)
    cv2.moveWindow('frame', width // 2, 0)  # Move it to the right half of the screen

    # Display the resulting frame, quit with q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        root.destroy()
        stop_flag = True

    if not stop_flag:
        root.after(33, show_frame)  # Schedule the next frame update


def motion(event):
    x, y = event.x + 3, event.y + 7  # The addition is just to center the oval around the mouse
    # Remove the +3 and +7 if you want to center it around the point of the mouse

    global circle
    global canvas
    global running
    #global detection_confirmed
    #global detection_time

    canvas.delete(circle)  # To refresh the circle each motion

    radius = 20  # Change this for the size of your circle

    x_max = x + radius
    x_min = x - radius
    y_max = y + radius
    y_min = y - radius

    circle = canvas.create_oval(x_max, y_max, x_min, y_min, outline="black", fill="red")

    #detection_confirmed = True
    #detection_time = cv2.getTickCount()

def quit_app(event=None):
    root.destroy()
    cv2.destroyAllWindows()

root = tk.Tk()

# Get screen width and height
width = root.winfo_screenwidth()
height = root.winfo_screenheight()

# Set the root window size to half the screen width and full screen height
root.geometry(f"{width // 2}x{height}+0+0")

canvas = tk.Canvas(root, width=width // 2, height=height, bg="white")
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
canvas.bind("<Motion>", motion)

circle = None
detection_confirmed = False
detection_time = 0

# Bind the 'q' key to quit the application
root.bind("q", quit_app)

# Schedule the first frame update
stop_flag = False
root.after(33, show_frame)

root.mainloop()
