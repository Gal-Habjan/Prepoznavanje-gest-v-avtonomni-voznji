import cv2
import requests
import numpy as np

# Replace with your ESP32-CAM capture URL
url = "http://192.168.0.20/capture?"

while True:
    try:
        # Send HTTP request to capture an image
        response = requests.get(url, timeout=1)  # Set timeout to avoid hangs
        if response.status_code == 200:
            # Decode image data into a NumPy array
            img_array = np.array(bytearray(response.content), dtype=np.uint8)
            frame = cv2.imdecode(img_array, -1)


            # Display the frame
            cv2.imshow("ESP32-CAM Stream", frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

cv2.destroyAllWindows()