import time

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import scipy.ndimage as ndimage
from scipy.spatial import ConvexHull

def edge_detection(img, normalize_by = 35):
    # mid = strength //2
    # kernel = np.zeros((strength, strength))
    # kernel = cv2.line(kernel, pt1=(strength, mid), pt2=(0, mid), color=(1,), thickness=1) / strength
    #kernel = np.array([[-1,-1,0,1,1],[-1,-1,0,1,1],[-2,-2,0,2,2],[-1,-1,0,1,1],[-1,-1,0,1,1]])/100
    # kernel = np.array([[ -1, 0, 1], [ -1, 0, 1], [ -1, 0, 1]]) / 30

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
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    # hsv = cv2.cvtColor(gray, cv2.COLOR_BGR2HSV)
    # # print(hsv)
    # mask = cv2.inRange(hsv, np.array([0,0,70]), np.array([0,0,130]))
    # contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    #
    # h, w, _ = img.shape
    # center = h // 2, w // 2
    # print(len(contours))
    #
    # for cnt in contours:
    #
    #     if cv2.contourArea(cnt) >5000:
    #          if cv2.pointPolygonTest(cnt, center, False) > 0:
    #             print(cv2.contourArea(cnt))
    #             mask = np.zeros((h, w), 'uint8')
    #             cv2.drawContours(mask, [cnt], -1, 255, -1)
    #             return cv2.bitwise_and(img, img, mask=mask)
    #
    #     # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    # hsv = cv2.cvtColor(gray, cv2.COLOR_BGR2HSV)
    # print(hsv)
    # mask = cv2.inRange(hsv, np.array([0,0,70]), np.array([0,0,130]))
    original = img
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # _, bin_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    # bin_img = bin_img.astype(bool)
    # blurred_image = cv2.GaussianBlur(img, (3, 3), 0)

    # Perform Canny edge detection
    edges = cv2.Canny(img, threshold1=30, threshold2=120)

    _, bin_img = cv2.threshold(edges, 127, 255, cv2.THRESH_BINARY)
    # print(bin_img)
    kernel = np.ones((5, 5), np.uint8)
    dilate_kernel = np.ones((7, 7), np.uint8)
    bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_DILATE, dilate_kernel)
    bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel)
    # print(mask)
    mask = np.bitwise_not(bin_img)
    # print(mask)
    # mask = mask.astype(np.uint8)*255

    # return mask*255
    # Step 2: Combine the gradients to get the overall edge response
    # gradient_magnitude = np.hypot(sobel_x, sobel_y)
    # gradient_magnitude = gradient_magnitude / np.max(gradient_magnitude) * 255  # Normalize to range 0-255
    # gradient_magnitude = gradient_magnitude.astype(np.uint8)
    # return gradient_magnitude
    # mask = ndimage.binary_closing(gradient_magnitude, kernel).astype(np.uint8)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    h, w = img.shape
    center = h // 2, w // 2
    print(len(contours))

    for cnt in contours:

        # if cv2.contourArea(cnt) > 5000:
        print(cv2.pointPolygonTest(cnt, center, True))
        if cv2.pointPolygonTest(cnt, center, False) > 0:
            print(cv2.contourArea(cnt))
            mask = np.zeros((h, w), 'uint8')
            cv2.drawContours(mask, [cnt], -1, 255, -1)
            return cv2.bitwise_and(original, original, mask=mask)

    # print("errr")
def get_hull_from_image(image):
    # start_time = time.time()
    img = get_mask(image)
    print(img)
    if img is not None and len(img)>0:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # print(img.shape)
    # print(img.shape)
    #
    # print("GOT IMAGE MASK")
    img = cv2.medianBlur(img, 5)
    img_edge = edge_detection(img)
    threshold = 128
    _, binary_image = cv2.threshold(img_edge, threshold, 255, cv2.THRESH_BINARY)
    points = get_points_from_binary_image(binary_image)
    if len(points) >= 3:
        hull = ConvexHull(points)
    else:
        return None
    # end_time = time.time()

    # print(f"time: {(end_time - start_time):.4f} seconds")
    return hull



if __name__ == '__main__':

    image = cv2.imread('test3.jpg')

    # get_hull_from_image(image)
    # size = image.shape
    # scale = 200/image.shape[0]
    # img = cv2.resize(image, (int(image.shape[1]*scale), int(image.shape[0]*scale)), interpolation=cv2.INTER_AREA)
    # Convert the image to grayscale
    img = image
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #
    # # Save the grayscale image
    # cv2.imwrite('gray.jpg', gray_image)

    # img = cv2.imread('test.jpg')
    img = cv2.medianBlur(img, 3)
    # print(img)
    out = edge_detection(img,9)
    # print(out)
    threshold = 128
    _, binary_image = cv2.threshold(out, threshold, 255, cv2.THRESH_BINARY)
    cv2.imwrite('edge_detection.jpg', binary_image)
    # #print(binary_image)
    # points = get_points_from_binary_image(binary_image)
    # #print("first points", points)
    #
    # # max_points = 10000 #idk kok naj jih bo
    # # if len(points) > max_points:
    # #     points = reduce_points(points, max_points)
    # #     #print("downslaced points", points)
    #
    # if len(points) >= 3:
    #     hull = ConvexHull(points)
    #
    #     plt.imshow(binary_image, cmap='gray')
    #
    #     for simplex in hull.simplices:
    #         plt.plot(points[simplex, 1], points[simplex, 0], 'r-')
    #     plt.plot(points[hull.vertices, 1], points[hull.vertices, 0], 'ro-', markersize=2)
    #     plt.show()
    # else:
    #     #print("wa wa")
    #     pass
    #
    # #print("hull", hull.vertices)
    #
    #
    # # extract points from hull
    # hull_points = points[hull.vertices]
    #
    # # ok flippam x pa y ker nevem zakaj obrne okol
    # hull_points_flipped = hull_points[:, ::-1]
    #
    # # mask za flipped convex hull reginon
    # mask = np.zeros_like(binary_image)
    # cv2.fillPoly(mask, [hull_points_flipped], 255)
    #
    # # resize na size od original img
    # mask_resized = cv2.resize(mask, (image.shape[1], image.shape[0]))
    #
    # # convert u uint8
    # mask_resized = mask_resized.astype(np.uint8)
    #
    # # apply
    # masked_image = cv2.bitwise_and(image, image, mask=mask_resized)
    #
    # # rotated bounding box iz convex hull points
    # rect = cv2.minAreaRect(hull_points_flipped)
    # box = cv2.boxPoints(rect)
    # box = np.intp(box)
    #
    # # bounding box korodinate
    # x, y, w, h = cv2.boundingRect(box)
    #
    # cropped_image = masked_image[y:y + h, x:x + w]
    #
    #
    # cv2.imwrite('cropped_image.jpg', cropped_image)




