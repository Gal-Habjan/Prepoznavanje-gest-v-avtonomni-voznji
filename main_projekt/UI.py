import tkinter as tk
import cv2
from PIL import Image, ImageTk
from enum import IntEnum
import spotifyApp
import webbrowser
from threading import Thread
import time
import shell_image
import numpy as np
class Gestures(IntEnum):
    FIST = 0
    HAND = 1
    PEACE = 2
    THUMBS_UP = 3
    NONE = 4


class Features(IntEnum):
    TURN_DOWN_VOL = 0
    TURN_UP_VOL = 1
    NEXT_SONG = 2
    TOGGLE_PAUSE = 3
    DO_NOTHING = 4


gestures_features_dict = {
    Gestures.FIST: Features.TURN_DOWN_VOL,
    Gestures.HAND: Features.TURN_UP_VOL,
    Gestures.PEACE: Features.NEXT_SONG,
    Gestures.THUMBS_UP: Features.TOGGLE_PAUSE,
    Gestures.NONE: Features.DO_NOTHING

}


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

        self.gesture_label = tk.Label(master, text="Waiting..")
        self.gesture_label.pack(anchor=tk.CENTER, expand=True)
        self.vid = cv2.VideoCapture(0)
        self.snapshot_queue = []
        self.current_box = None
        self.current_prob = None
        self.update()
        button = tk.Button(master, text="Authenticate", command=self.open_url)
        button.pack(pady=20)
        self.spotify_thread = None

    def open_url(self):
        url = "http://127.0.0.1:5000"  # Replace this with your desired URL
        webbrowser.open_new(url)

    def setup_box(self, box, prob):
        self.current_box = box
        self.current_prob = prob

    def close_window(self):
        self.is_running = False
        self.master.destroy()

    def snapshot(self):

        ret, frame = self.vid.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            # Save the image using PIL
            return pil_image

    def call_spotify(self, gesture):
        function = gestures_features_dict[gesture]
        if function == Features.NEXT_SONG:
            spotifyApp.call_next_song()

        elif function == Features.TOGGLE_PAUSE:

            spotifyApp.call_toggle_pause()

        elif function == Features.TURN_UP_VOL:
            spotifyApp.call_volume_up()

        elif function == Features.TURN_DOWN_VOL:
            spotifyApp.call_volume_down()
        time.sleep(1)

    def draw_hull_on_image(self,original_image, hull, offset=(0, 0)):
        if hull is None:
            return original_image

        points = hull.points[hull.vertices]


        # ok flippam x pa y ker nevem zakaj obrne okol
        points = points[:, ::-1]
        points = np.array(points, dtype=np.int32)
        points += np.array(offset)  # Apply the offset to get back to the original image coordinates
        cv2.polylines(original_image, [points], isClosed=True, color=(0, 255, 0), thickness=2)
        return original_image
    def update(self):
        ret, frame = self.vid.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if self.current_box is not None and len(self.current_box.data) > 0:
                # print(self.current_box.data)
                # Extract box coordinates
                x_min, y_min, x_max, y_max, prob, clas = self.current_box.data[0]

                x_min, y_min, x_max, y_max, prob, clas = int(x_min.item()), int(y_min.item()), int(x_max.item()), int(
                    y_max.item()), prob.item(), int(clas.item())
                # print(x_min, y_min, x_max, y_max, prob, clas)
                # Draw bounding box
                cropped_image = rgb_frame[y_min:y_max, x_min:x_max]
                hull = shell_image.get_hull_from_image(cropped_image)
                cv2.rectangle(rgb_frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
                offset = (x_min, y_min)
                rgb_frame = self.draw_hull_on_image(rgb_frame, hull,offset)
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
                if self.spotify_thread is None or not self.spotify_thread.is_alive():
                    self.spotify_thread = Thread(target=self.call_spotify, args=(gesture,))
                    self.spotify_thread.start()
                # self.call_spotify(gesture)
                # Add label and probability
                label = f"{gesture.name}, Probability: {prob:.2f}"  # Adjust as needed
                cv2.putText(rgb_frame, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                self.gesture_label.config(text=gestures_features_dict[gesture].name)
            else:
                self.gesture_label.config(text="Waiting..")
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(rgb_frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.master.after(10, self.update)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Create a master and pass it to the CameraApp class
