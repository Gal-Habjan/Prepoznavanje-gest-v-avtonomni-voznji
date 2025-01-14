from ultralytics import YOLO
import tkinter as tk
import UI
import time
from threading import Thread
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
import torchvision.transforms as transforms
import spotifyApp

path_to_best = "./runs/detect/train10/weights/best.pt"
model = None
from PIL import Image
import websockets
import asyncio
import compression
def ai_thread(app):

    while app.is_running:
        try:
            img = app.snapshot()
            save_path = "captured_image.jpg"


            #img.save(save_path)
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
                result.save(filename='result.jpg')
                app.setup_box(boxes, probs)
                compression.compress_image("result.jpg","compressed_image.jpg")
        except Exception as e:
            print(e)

    print("end")


async def websocket_response(websocket, app):
    while(True):
        await websocket.send(str(app.sent_gesture))
        await asyncio.sleep(1)

async def websocket_run(app):
    # Create and start websocket server
    start_server = websockets.serve(lambda ws: websocket_response(ws, app), "localhost", 8765)
    await start_server
    print("WebSocket server started")
    await asyncio.Future()  # Keeps the server running indefinitely

def websocket_thread(app):
    # Start the websocket server using asyncio.run
    asyncio.run(websocket_run(app))
def run_UI_tread():
    root = tk.Tk()
    app = UI.CameraApp(root, "Camera App")

    logic_thread = Thread(target=ai_thread, args=(app,))
    logic_thread.daemon = True  # terminates after main thread
    logic_thread.start()
    websocket_thr = Thread(target=websocket_thread, args=(app,))
    websocket_thr.start()
    root.mainloop()

if __name__ == '__main__':
    print("start")

    model = YOLO(path_to_best)

    print("model loaded")

    # ui_thread = Thread(target=run_UI_tread, args=())
    #
    # ui_thread.start()
    run_UI_tread()


