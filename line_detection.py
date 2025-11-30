print("Ivina line detection")

import cv2
import numpy as np

# 0. Kernel operations
kernel_small = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
kernel_large = cv2.getStructuringElement(cv2.MORPH_DIAMOND,(5,5))

def dilate(img, iterations=1):
    return cv2.dilate(img, kernel_small, iterations=iterations)

def erode(img, iterations=1):
    return cv2.erode(img, kernel_small, iterations=iterations)

def close(img, iterations=1):
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel_large, iterations=iterations)


# 1. Load image
img = cv2.imread("slikaB.jpg")
if img is None:
    print("Error: cannot load image! Check file path and name.")
    exit()

h, w = img.shape[:2]
roi = img[h//3:, :]         # bottom 2/3 of the image
y_offset = h // 3           # vertical offset because ROI is cropped


# 2. HSV mask for white color
hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
lower_white = np.array([0,0,180])
upper_white = np.array([180,40,255])
mask = cv2.inRange(hsv, lower_white, upper_white)
white_only = cv2.bitwise_and(roi, roi, mask=mask)


# 3. Grayscale + equalize histogram
gray = cv2.cvtColor(white_only, cv2.COLOR_BGR2GRAY)
gray_eq = cv2.equalizeHist(gray)


# 4. Blur + Canny edges
blur = cv2.GaussianBlur(gray_eq, (5,5), 0)
edges = cv2.Canny(blur, 50, 150)


# 5. Morphology
closed = close(edges,1)
dil = dilate(closed,1)
final = erode(dil,1)


# 6. Hough Lines
lines = cv2.HoughLinesP(final, rho=1, theta=np.pi/180, threshold=50,
                        minLineLength=50, maxLineGap=15)


# 7. Draw all Hough lines for visualization
all_lines_img = img.copy()
left_points = []
right_points = []

if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        y1_orig = y1 + y_offset
        y2_orig = y2 + y_offset
        slope = (y2 - y1) / (x2 - x1 + 1e-6)

        # Blue = left line, Yellow = right line
        color = (255,0,0) if slope < 0 else (0,255,255)
        cv2.line(all_lines_img, (x1, y1_orig), (x2, y2_orig), color, 2)

        # Collect points for line fitting
        if slope < 0:
            left_points.append([x1, y1_orig])
            left_points.append([x2, y2_orig])
        elif slope > 0:
            right_points.append([x1, y1_orig])
            right_points.append([x2, y2_orig])
else:
    print("No lines detected.")


# 8. Fit one left + one right line
out = img.copy()

def fit_and_draw(points, color):
    pts = np.array(points, dtype=np.float32)
    if len(pts) < 2:
        return None
    vx, vy, x0, y0 = cv2.fitLine(pts, cv2.DIST_L2, 0,0.01,0.01)
    y_top = y_offset
    y_bottom = h
    t_top = (y_top - y0)/vy
    t_bottom = (y_bottom - y0)/vy
    x_top = int(x0 + t_top*vx)
    x_bottom = int(x0 + t_bottom*vx)
    cv2.line(out, (x_top, y_top), (x_bottom, y_bottom), color, 5)
    return (x_top, y_top), (x_bottom, y_bottom)

left_line = fit_and_draw(left_points, (0,0,255))    # red line
right_line = fit_and_draw(right_points, (0,255,0))   # green line


# 9. Fill polygon only in ROI
out_filled = out.copy()
if left_line and right_line:
    lx_top, lx_bottom = left_line
    rx_top, rx_bottom = right_line
    polygon = np.array([lx_top, lx_bottom, rx_bottom, rx_top], dtype=np.int32)
    overlay = out.copy()
    cv2.fillPoly(overlay, [polygon], (0,255,0))
    out_filled = cv2.addWeighted(overlay, 0.3, out, 0.7, 0)


# 10. Display results
cv2.imshow("Original", img)
cv2.waitKey(0)
cv2.imshow("ROI", roi)
cv2.waitKey(0)
cv2.imshow("White mask", mask)
cv2.waitKey(0)
cv2.imshow("White only", white_only)
cv2.waitKey(0)
cv2.imshow("Gray EQ", gray_eq)
cv2.waitKey(0)
cv2.imshow("Blur", blur)
cv2.waitKey(0)
cv2.imshow("Canny edges", edges)
cv2.waitKey(0)
cv2.imshow("Final (morphology)", final)
cv2.waitKey(0)
cv2.imshow("All Hough lines (blue=left, yellow=right)", all_lines_img)
cv2.waitKey(0)
cv2.imshow("Fitted lines + Area", out_filled)

cv2.waitKey(0)
cv2.destroyAllWindows()
