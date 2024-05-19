from ultralytics import YOLO
# import tkinter as tk
# import UI
# import time
# from threading import Thread
# import os
# import torchvision.transforms as transforms
path_to_best = "runs/detect/train6/weights/best.pt"

if __name__ == '__main__':
    model = YOLO(path_to_best)  # load a pretrained model (recommended for training)
    model.train(data="config.yaml", epochs=100, batch=16, imgsz=640, device=0)