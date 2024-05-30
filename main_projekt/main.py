from ultralytics import YOLO
import tkinter as tk
import UI
import time
from threading import Thread
import os
import torchvision.transforms as transforms
import spotifyApp

path_to_best = "./runs/detect/train6/weights/best.pt"
model = None


def ai_thread(app):
    i = 0
    while app.is_running:
        print(app.is_running)
        # print("i",i)
        i += 1
        img = app.snapshot()

        to_tensor = transforms.Compose([
            transforms.ToTensor()
        ])
        input = to_tensor(img)
        input = input.unsqueeze(0)
        results = model(input)

        # Process results list
        for result in results:
            boxes = result.boxes  # Boxes object for bounding box outputs
            # print("box", boxes)
            # masks = result.masks  # Masks object for segmentation masks outputs
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
    # model = YOLO("yolov8n.yaml")  # build a new model from scratch
    model = YOLO(path_to_best)  # load a pretrained model (recommended for training)
    # model.train(data="config.yaml", epochs=100, batch=16, imgsz=640, device=0)

    print("model loaded")

    ui_thread = Thread(target=run_UI_tread, args=())


    ui_thread.start()

