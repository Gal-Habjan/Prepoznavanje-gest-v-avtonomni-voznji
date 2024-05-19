import tkinter as tk
import cv2
from PIL import Image, ImageTk
from enum import Enum


class Gestures(Enum):
    FIST = 0
    HAND = 1
    PEACE = 2
    THUMBS_UP = 3
    NONE = 4


class CameraApp:
    def __init__(self, master, window_title):
        self.master = master
        self.master.title(window_title)
        self.is_running = True
        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source)

        self.canvas = tk.Canvas(master, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH),
                                height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()

        self.btn_snapshot = tk.Button(master, text="Snapshot", width=50, command=self.snapshot)
        self.btn_snapshot.pack(anchor=tk.CENTER, expand=True)
        self.vid = cv2.VideoCapture(0)
        self.snapshot_queue = []
        self.current_box = None
        self.current_prob = None
        self.update()

    def setup_box(self, box, prob):
        self.current_box = box
        self.current_prob = prob

    def close_window(self):
        self.is_running = False
        self.master.destroy()

    def snapshot(self):
        print("should ss")
        ret, frame = self.vid.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            # Save the image using PIL
            pil_image.save("snapshot.png")

    def update(self):
        ret, frame = self.vid.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if self.current_box is not None and len(self.current_box.data) > 0:
                #print(self.current_box.data)
                # Extract box coordinates
                x_min, y_min, x_max, y_max, prob, clas = self.current_box.data[0]

                x_min, y_min, x_max, y_max, prob, clas = int(x_min.item()), int(y_min.item()), int(x_max.item()), int(
                    y_max.item()), prob.item(), int(clas.item())
                print(x_min, y_min, x_max, y_max, prob, clas)
                # Draw bounding box
                cv2.rectangle(rgb_frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
                gesture = Gestures.NONE
                if clas == Gestures.FIST.value:
                    gesture = Gestures.FIST
                elif clas == Gestures.HAND.value:
                    gesture = Gestures.HAND
                elif clas == Gestures.PEACE.value:
                    gesture = Gestures.PEACE
                elif clas == Gestures.THUMBS_UP.value:
                    gesture = Gestures.THUMBS_UP
                elif clas == Gestures.NONE.value:
                    gesture = Gestures.NONE

                # Add label and probability
                label = f"{gesture}, Probability: {prob:.2f}"  # Adjust as needed
                cv2.putText(rgb_frame, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(rgb_frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.master.after(10, self.update)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Create a master and pass it to the CameraApp class
