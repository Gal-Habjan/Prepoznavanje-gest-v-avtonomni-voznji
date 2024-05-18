import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import scipy.ndimage as ndimage
from scipy.spatial import ConvexHull, convex_hull_plot_2d
def edge_detection(img, strength = 5):
    # mid = strength //2
    # kernel = np.zeros((strength, strength))
    # kernel = cv2.line(kernel, pt1=(strength, mid), pt2=(0, mid), color=(1,), thickness=1) / strength
    #kernel = np.array([[-1,-1,0,1,1],[-1,-1,0,1,1],[-2,-2,0,2,2],[-1,-1,0,1,1],[-1,-1,0,1,1]])/100
    # kernel = np.array([[ -1, 0, 1], [ -1, 0, 1], [ -1, 0, 1]]) / 30
    normalize_by =35
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])/normalize_by
    sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])/normalize_by

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

def imageToPoints(image):
    points = []

    for y in range(len(image)):
        for x in range(len(image[y])):
            if(image[y][x] > 0.9):
                points.append([x,y])

    return points

if __name__ == '__main__':
    image = cv2.imread('test.jpg')

    # Convert the image to grayscale
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Save the grayscale image
    # cv2.imwrite('gray.jpg', gray_image)

    # img = cv2.imread('test.jpg')
    img = cv2.medianBlur(img, 5)
    # print(img)
    out = edge_detection(img)

    # print(out)
    threshold = 150
    _, binary_image = cv2.threshold(out, threshold, 255, cv2.THRESH_BINARY)
    cv2.imwrite('edge_detection.jpg', binary_image)


    points = np.array(imageToPoints(binary_image))
    hull = ConvexHull(points)
    plt.plot(points[:,0], -points[:,1], 'o')
    for simplex in hull.simplices:
        plt.plot(points[simplex, 0], -points[simplex, 1], 'k-')


    plt.show()


