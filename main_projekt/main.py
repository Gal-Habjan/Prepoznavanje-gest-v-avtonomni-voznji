from ultralytics import YOLO
import tkinter as tk
import UI
import time
from threading import Thread
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
import torchvision.transforms as transforms
import spotifyApp

path_to_best = "./runs/detect/train6/weights/best.pt"
model = None
from PIL import Image

def ai_thread(app):

    while app.is_running:

        img = app.snapshot()

        to_tensor = transforms.Compose([
            transforms.ToTensor()
        ])
        input = to_tensor(img)
        input = input.unsqueeze(0)
        results = model(input, verbose=False)

        # Process results list
        for result in results:
            boxes = result.boxes  # Boxes object for bounding box outputs
            # print("box", boxes)
            #masks = result.masks  # Masks object for segmentation masks outputs
            # keypoints = result.keypoints  # Keypoints object for pose outputs
            probs = result.probs  # Probs object for classification outputs
            # obb = result.obb  # Oriented boxes object for OBB outputs
            # result.show()  # display to screen
            # result.save(filename='result.jpg')
            app.setup_box(boxes, probs)
    print("end")




def run_UI_tread():
    root = tk.Tk()
    app = UI.CameraApp(root, "Camera App")

    logic_thread = Thread(target=ai_thread, args=(app,))
    logic_thread.daemon = True  # terminates after main thread
    logic_thread.start()
    root.mainloop()

if __name__ == '__main__':
    print("start")

    model = YOLO(path_to_best)

    print("model loaded")

    # ui_thread = Thread(target=run_UI_tread, args=())
    #
    # ui_thread.start()
    run_UI_tread()


