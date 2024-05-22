import cv2
import numpy as np

# img = cv2.imread("test3.jpg")
def get_mask(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    hsv = cv2.cvtColor(gray, cv2.COLOR_BGR2HSV)
    # print(hsv)
    mask = cv2.inRange(hsv, np.array([0,0,70]), np.array([0,0,130]))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    h, w, _ = img.shape
    center = h // 2, w // 2
    print(len(contours))

    for cnt in contours:

        if cv2.contourArea(cnt) >5000:
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
    if mask is None: mask = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow("mask",mask)
    if cv2.waitKey(1) == ord('q'):
        break

# cv2.imwrite("mask_idk.jpg", get_mask(img))
# cv2.waitKey(0)