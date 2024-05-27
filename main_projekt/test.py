import cv2
import numpy as np
import scipy.ndimage as ndimage

# img = cv2.imread("test3.jpg")


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
def get_mask(img):
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    # hsv = cv2.cvtColor(gray, cv2.COLOR_BGR2HSV)
    # print(hsv)
    # mask = cv2.inRange(hsv, np.array([0,0,70]), np.array([0,0,130]))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # _, bin_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    # bin_img = bin_img.astype(bool)
    # blurred_image = cv2.GaussianBlur(img, (5, 5), 0)

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
    return mask
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
        print(cv2.pointPolygonTest(cnt, center,True))
        if cv2.pointPolygonTest(cnt, center, False) > 0:
            print(cv2.contourArea(cnt))
            mask = np.zeros((h, w), 'uint8')
            cv2.drawContours(mask, [cnt], -1, 255, -1)
            return mask

    print("errr")


cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    mask = get_mask(frame)
    # print(mask.shape)
    # print(mask)
    if mask is None: mask = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow("mask", mask)
    if cv2.waitKey(1) == ord('q'):
        break

# cv2.imwrite("mask_idk.jpg", get_mask(img))
# cv2.waitKey(0)
img = cv2.imread('idk.jpg')
# img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# # blurred_image = cv2.GaussianBlur(img, (1, 1), 0)
# edges = cv2.Canny(img, threshold1=20, threshold2=120)
# _, bin_img = cv2.threshold(edges, 127, 255, cv2.THRESH_BINARY)
# # print(bin_img)
# mask = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel)
# dilate_kernel = np.ones((3, 3), np.uint8)
# mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, dilate_kernel)
# # mask = ndimage.binary_closing(bin_img, kernel)
# # mask = ndimage.binary_closing(mask, kernel)
# # mask = ndimage.binary_closing(mask, kernel)
# print(mask)
# mask = np.bitwise_not(mask)
# print(mask)
# # mask = mask.astype(np.uint8)*255
#
# cv2.imshow("mask",mask)
# cv2.waitKey(0)
# contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
#
# h, w = img.shape
# center = h // 2, w // 2
# print(len(contours))
#
# for cnt in contours:
#
#     # if cv2.contourArea(cnt) > 5000:
#     # print(cv2.pointPolygonTest(cnt, center,True))
#     if cv2.pointPolygonTest(cnt, center, False) > 0:
#     # print(cv2.contourArea(cnt))
#         mask = np.zeros((h, w), 'uint8')
#         cv2.drawContours(mask, [cnt], -1, 255, -1)
#         cv2.imshow("mask", mask)
#         cv2.waitKey(0)