from ultralytics import YOLO
import tkinter as tk
import UI
import time
from threading import Thread
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
import torchvision.transforms as transforms
import spotifyApp
import numpy as np
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
            to_tensor = transforms.Compose([transforms.ToTensor()])
            input = to_tensor(img).unsqueeze(0)
            results = model(input, verbose=False)

            for result in results:
                boxes = result.boxes
                probs = result.probs
                result.save(filename='result.jpg')
                app.setup_box(boxes, probs)
        except Exception as e:
            print(e)

    print("AI thread ended.")

async def websocket_response(websocket, app):
    try:
        while app.is_running:
            if len(app.sent_gesture) > 0:
                most_used_gesture = np.bincount(app.sent_gesture).argmax()
            else:
                most_used_gesture = 4
            await websocket.send(str(most_used_gesture))
            await asyncio.sleep(1)
    except Exception as e:
        print("WebSocket error:", e)

async def websocket_run(app):
    start_server = websockets.serve(lambda ws: websocket_response(ws, app), "localhost", 8765)
    server = await start_server
    print("WebSocket server started")
    try:
        while app.is_running:
            await asyncio.sleep(1)
    finally:
        server.close()
        await server.wait_closed()
        print("WebSocket server stopped.")

def websocket_thread(app):
    asyncio.run(websocket_run(app))

def run_UI_tread():
    root = tk.Tk()
    app = UI.CameraApp(root, "Camera App")

    # Start AI thread
    logic_thread = Thread(target=ai_thread, args=(app,), daemon=True)
    logic_thread.start()

    # Start WebSocket thread
    websocket_thr = Thread(target=websocket_thread, args=(app,), daemon=True)
    websocket_thr.start()

    try:
        root.mainloop()  # Blocks until UI is closed
    finally:
        app.is_running = False  # Stop threads when UI is closed
        logic_thread.join()  # Wait for the AI thread to terminate
        websocket_thr.join()  # Wait for WebSocket thread to terminate
        print("All threads stopped.")

if __name__ == '__main__':
    print("Starting...")
    model = YOLO(path_to_best)
    print("Model loaded")
    run_UI_tread()
