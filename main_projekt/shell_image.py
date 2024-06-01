import time

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import scipy.ndimage as ndimage
from scipy.spatial import ConvexHull

def edge_detection(img, normalize_by = 35):

    sobel_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])/normalize_by
    sobel_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])/normalize_by

    # If the image is grayscale
    if len(img.shape) == 2:
        img = img[:, :, np.newaxis]

    # Initialize the output image
    edge_img = np.zeros_like(img, dtype=float)

    # Apply Sobel operator
    for i in range(img.shape[2]):  # loop over image channels
        grad_x = ndimage.convolve(img[:, :, i], sobel_x)
        grad_y = ndimage.convolve(img[:, :, i], sobel_y)
        edge_img[:, :, i] = np.hypot(grad_x, grad_y)


    return edge_img


def get_points_from_binary_image(binary_image):
    points = np.argwhere(binary_image == 255)
    return points

def reduce_points(points, max_points):
    while len(points) > max_points:
        new_points = []
        for i in range(0, len(points) - 1, 2):
            new_point = (points[i] + points[i + 1]) // 2
            new_points.append(new_point)
        if len(points) % 2 == 1:
            new_points.append(points[-1])
        points = np.array(new_points)
    return points
def get_mask(img):
    kernel = np.ones((13, 13), np.uint8)

    original = img
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #
    edges = cv2.Canny(img, threshold1=30, threshold2=120)

    _, bin_img = cv2.threshold(edges, 127, 255, cv2.THRESH_BINARY)
    # print(bin_img)
    kernel = np.ones((5, 5), np.uint8)
    dilate_kernel = np.ones((7, 7), np.uint8)
    bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_DILATE, dilate_kernel)
    bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel)
    # print(mask)
    mask = np.bitwise_not(bin_img)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    h, w = img.shape
    center = h // 2, w // 2


    for cnt in contours:
        if cv2.pointPolygonTest(cnt, center, False) > 0:

            mask = np.zeros((h, w), 'uint8')
            cv2.drawContours(mask, [cnt], -1, 255, -1)
            return cv2.bitwise_and(original, original, mask=mask)

    # print("errr")
def get_hull_from_image(image):

    img = get_mask(image)
    # print(img)
    if img is not None and len(img)>0:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    img = cv2.medianBlur(img, 5)
    img_edge = edge_detection(img)
    threshold = 128
    _, binary_image = cv2.threshold(img_edge, threshold, 255, cv2.THRESH_BINARY)
    points = get_points_from_binary_image(binary_image)
    if len(points) >= 3:
        hull = ConvexHull(points)
    else:
        return None

    return hull

