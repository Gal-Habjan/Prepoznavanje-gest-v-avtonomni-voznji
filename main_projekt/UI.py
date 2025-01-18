import tkinter as tk
import cv2
import requests
from PIL import Image, ImageTk
from enum import IntEnum
import spotifyApp
import webbrowser
from threading import Thread
import threading
import time
import shell_image
import numpy as np
from datetime import datetime
import paho.mqtt.client as mqtt
from prometheus_client import start_http_server, Counter
import voice_recognition as voice




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
        self.save_image = False
        self.test_no_camera = True
        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source)
        self.camera_url = "http://esp32.local/capture?"
        self.sent_gesture = []
        self.canvas = tk.Canvas(master, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH),
                                height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()
        self.gesture_label = tk.Label(master, text="Waiting..")
        self.gesture_label.pack(anchor=tk.CENTER, expand=True)
        # self.turn_down_volume_counter = Counter('volume_down', 'volume down counter')
        # self.turn_up_volume_counter = Counter('volume_up', 'volume up counter')
        # self.toggle_pause_counter = Counter('toggle_pause', 'toggle pause counter')
        # self.next_song_counter = Counter('next_song', 'next song counter')
        # self.send_requests = Counter('all_requests', 'all processed images and sent requests')
        # self.broker = "10.8.11.3"
        #
        #
        # self.port = 1883
        # self.topic = "/data"
        # self.mqtt_client = mqtt.Client(client_id="producer_1", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        # self.mqtt_client.connect(self.broker, self.port, 360)
        # self.mqtt_client.on_connect = self.on_connect
        # start_http_server(8000)
        self.vid = cv2.VideoCapture(0)
        self.rgb_frame = None
        self.snapshot_queue = []
        self.current_box = None
        self.current_prob = None
        self.lock = threading.Lock()
        self.fetch_image()
        self.update()

        button = tk.Button(master, text="Authenticate", command=self.open_url)
        button.pack(pady=20)
        self.voice_label = tk.Label(master, text="Click listen and speak for 3 seconds")
        self.voice_label.pack(anchor=tk.CENTER, expand=True)
        button2 = tk.Button(master, text="Listen", command=self.listen_to_voice_button)
        button2.pack(pady=10)
        button3 = tk.Button(master, text="Save", command=self.save_image_button)
        button3.pack(pady=10)
        self.spotify_thread = None
        self.voice_thread = None

        # self.wait_for_sound()


    def on_connect(self, client, userdata, flags, reasonCode, properties=None):
        print("Povezava z GESTA MQTT: " + str(reasonCode))

    def open_url(self):
        url = "http://127.0.0.1:5000"  # Replace this with your desired URL
        webbrowser.open_new(url)

    def setup_box(self, box, prob):
        self.current_box = box
        self.current_prob = prob

    def close_window(self):
        self.is_running = False

        if self.spotify_thread and self.spotify_thread.is_alive():
            self.spotify_thread.join()
        if self.voice_thread and self.voice_thread.is_alive():
            self.voice_thread.join()
        self.master.destroy()

    def snapshot(self):
        if self.current_box:
            ret, frame = self.vid.read()
            if ret:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)
                # Save the image using PIL
                return pil_image
        else:
            if self.rgb_frame is not None:
                pil_image = Image.fromarray(self.rgb_frame)

                # Save the image using PIL
                return pil_image

    def fetch_image(self):


        def fetch():
            try:
                response = requests.get(self.camera_url, timeout=0.25)
                if response.status_code == 200:
                    img_array = np.array(bytearray(response.content), dtype=np.uint8)
                    frame = cv2.imdecode(img_array, -1)
                    self.rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")

            self.fetch_image()
        if self.test_no_camera is False:
        # Run the fetch in a separate thread
            threading.Thread(target=fetch, daemon=True).start()

    def call_spotify(self, gesture, function=None):

        try:
            # message = "sending sent_gesture" + sent_gesture.name+ " " + datetime.now().strftime("%H:%M:%S")
            # ret = self.mqtt_client.publish(self.topic, message, qos=1, retain=False)
            # self.send_requests.inc(1)
            # print("Pošiljanje: " + message + " " + str(ret.rc))
            if gesture is not None:
                function = gestures_features_dict[gesture]

            if function == Features.NEXT_SONG:
                # self.next_song_counter.inc(1)
                spotifyApp.call_next_song()

            elif function == Features.TOGGLE_PAUSE:
                # self.toggle_pause_counter.inc(1)
                spotifyApp.call_toggle_pause()

            elif function == Features.TURN_UP_VOL:
                # self.turn_up_volume_counter.inc(1)
                spotifyApp.call_volume_up()

            elif function == Features.TURN_DOWN_VOL:
                # self.turn_down_volume_counter.inc(1)
                spotifyApp.call_volume_down()
        except Exception as e:
            print("Exception while calling spotify", e)
        time.sleep(1)

    def listen_to_voice_button(self):
        if self.voice_thread is None or not self.voice_thread.is_alive():
            print("start thread")
            self.voice_thread = Thread(target=self.wait_for_sound)

            self.voice_thread.start()

    def save_image_button(self):
        self.save_image = True
    def wait_for_sound(self):
        with self.lock:
            print("Start listening")
            try:
                predicted_command, probabilities = voice.get_command_from_voice()
                print(f"Predicted Command: {predicted_command}")
                feature = Features.DO_NOTHING
                if predicted_command == Features.TURN_UP_VOL.name:

                    feature = Features.TURN_UP_VOL
                elif predicted_command == Features.TURN_DOWN_VOL.name:
                    feature = Features.TURN_DOWN_VOL
                elif predicted_command == Features.NEXT_SONG.name:
                    feature = Features.NEXT_SONG

                elif predicted_command == Features.TOGGLE_PAUSE.name:
                    feature = Features.TOGGLE_PAUSE

                self.voice_label.config(text=feature.name)
                self.call_spotify(None, feature)
            except Exception as e:
                print(f"Error in wait_for_sound: {e}")

    def draw_hull_on_image(self, original_image, hull, offset=(0, 0)):
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
        if self.test_no_camera:
            ret, frame = self.vid.read()
            self.rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        try:

            if self.rgb_frame is not None :



                copyOfFrame = self.rgb_frame.copy()
                if self.current_box is not None and len(self.current_box.data) > 0:
                    # print(self.current_box.data)
                    # Extract box coordinates
                    x_min, y_min, x_max, y_max, prob, clas = self.current_box.data[0]

                    x_min, y_min, x_max, y_max, prob, clas = int(x_min.item()), int(y_min.item()), int(
                        x_max.item()), int(
                        y_max.item()), prob.item(), int(clas.item())
                    # print(x_min, y_min, x_max, y_max, prob, clas)
                    # Draw bounding box
                    cropped_image = copyOfFrame[y_min:y_max, x_min:x_max]
                    cv2.rectangle(copyOfFrame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
                    try:
                        hull = shell_image.get_hull_from_image(cropped_image)
                        offset = (x_min, y_min)
                        copyOfFrame = self.draw_hull_on_image(copyOfFrame, hull, offset)
                    except Exception as e:
                        print("Exception while getting hull", e)

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
                    self.sent_gesture.append(gesture)

                    if self.spotify_thread is None or not self.spotify_thread.is_alive():
                        self.spotify_thread = Thread(target=self.call_spotify, args=(gesture,))
                        self.spotify_thread.start()
                    # self.call_spotify(sent_gesture)
                    # Add label and probability
                    label = f"{gesture.name}, Probability: {prob:.2f}"  # Adjust as needed
                    cv2.putText(copyOfFrame, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0),
                                2)
                    self.gesture_label.config(text=gestures_features_dict[gesture].name)
                else:
                    self.sent_gesture.append(Gestures.NONE)
                    self.gesture_label.config(text="Waiting..")
                if len(self.sent_gesture) > 5:
                    self.sent_gesture = self.sent_gesture[3:]
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(copyOfFrame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)


        except Exception as e:

            print(f"An error occurred: {e}")
        self.master.after(10, self.update)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
