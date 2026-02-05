import os
import math
import cv2
import numpy as np

def rotate_image(gray_image):
    th1, th2 = 120, 150
    hough_th, hough_min, hough_max = 150, 50, 50

    blurred = cv2.GaussianBlur(gray_image, (5, 5), 1.5)
    edges = cv2.Canny(blurred, th1, th2, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/360, threshold=hough_th, minLineLength=hough_min, maxLineGap=hough_max)

    angles = []
    if lines is not None:
        for x1, y1, x2, y2 in lines[:, 0]:
            angle_rad = math.atan2((y2 - y1), (x2 - x1))
            angle_deg = math.degrees(angle_rad)
            angles.append(angle_deg)
            print(f"Line: ({x1}, {y1}) to ({x2}, {y2}), Angle: {angle_deg:.2f} degrees")
            
        if angles:
            average_angle = np.mean(angles)
            print(f"Average angle: {average_angle:.2f} degrees")

    (h, w) = gray_img.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, average_angle, 1.0)
    rotated_img = cv2.warpAffine(gray_img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    
    return average_angle, rotated_img

# 초기 설정
image_path = os.path.join("yolo_run", 'obb_test2.jpg')
image = cv2.imread(image_path)
gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
rotated_angle, rotated_img = rotate_image(gray_img)
blurred = cv2.GaussianBlur(rotated_img, (5, 5), 1.5)

cv2.namedWindow("Edge Detection")

def nothing(x):
    pass

cv2.createTrackbar("Canny Th1", "Edge Detection", 120, 500, nothing)
cv2.createTrackbar("Canny Th2", "Edge Detection", 150, 500, nothing)
cv2.createTrackbar("Hough Th", "Edge Detection", 150, 500, nothing)
cv2.createTrackbar("Hough min", "Edge Detection", 50, 1000, nothing)
cv2.createTrackbar("Hough max", "Edge Detection", 50, 500, nothing)

while True:
    th1 = cv2.getTrackbarPos("Canny Th1", "Edge Detection")
    th2 = cv2.getTrackbarPos("Canny Th2", "Edge Detection")
    hough_th = cv2.getTrackbarPos("Hough Th", "Edge Detection")
    hough_min = cv2.getTrackbarPos("Hough min", "Edge Detection")
    hough_max = cv2.getTrackbarPos("Hough max", "Edge Detection")

    edges = cv2.Canny(blurred, th1, th2, apertureSize=3)

    rotated_copy = rotated_img.copy()
    lines = cv2.HoughLinesP(edges, 1, np.pi/360, threshold=hough_th, minLineLength=hough_min, maxLineGap=hough_max)
    if lines is not None:
        angles = []
        for x1, y1, x2, y2 in lines[:, 0]:
            cv2.line(rotated_copy, (x1, y1), (x2, y2), (0, 0, 255), 2)
            angle_rad = math.atan2((y2 - y1), (x2 - x1))
            angle_deg = math.degrees(angle_rad)
            angles.append(angle_deg)
            print(f"Line: ({x1}, {y1}) to ({x2}, {y2}), Angle: {angle_deg:.2f} degrees")
            
        if angles:
            average_angle = np.mean(angles)
            print(f"Average angle: {average_angle:.2f} degrees")

    cv2.waitKey(500)

    combined = np.hstack((edges, rotated_copy))
    cv2.imshow("Edge Detection", combined)

    if cv2.waitKey(10) & 0xFF == 27:
        break

cv2.destroyAllWindows()
