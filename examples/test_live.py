import cv2
import mycamcap

import time

# Define the video capture object (use 0 for the default camera or specify a different camera index)
cap = mycamcap.CameraCapture()

# Define the codec for MP4 (H.264)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'mp4v' for H.264 codec
out = cv2.VideoWriter('output_async.mp4', fourcc, 20.0, (640, 480))  # Specify filename, codec, frames per second, and frame size

cap.Live_start()
count = 0
while True:
    # Read the current frame from the camera
    ret, frame = cap.Live_read()

    if not ret:
        break

    # Display the frame (optional)
    # cv2.imshow('Frame', frame)

    # Write the frame to the output video file
    out.write(frame)

    # Exit the loop if a key is pressed (e.g., press 'q' to exit)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
    count += 1

    if count > 20:
        break

    time.sleep(0.25)

# Release the video capture and writer objects
cap.Live_stop()
out.release()

# Close any OpenCV windows
cv2.destroyAllWindows()