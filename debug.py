import cv2
import numpy as np

def create_roi_for_bfmc_car(image):
    h, w = image.shape[:2]

    lift = 0.15
    top_offset = 0.30

    bottom_y = int(h * (1 - lift))
    top_y    = int(h * top_offset)

    polygon = np.array([
        (int(w * 0.02), bottom_y),
        (int(w * 0.98), bottom_y),
        (int(w * 0.80), top_y),
        (int(w * 0.20), top_y)
    ], np.int32)

    mask = np.zeros_like(image)
    cv2.fillPoly(mask, [polygon], 255)
    return cv2.bitwise_and(image, mask)


def process_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)

    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 40, 120)

    masked = create_roi_for_bfmc_car(edges)

    lines = cv2.HoughLinesP(masked, 1, np.pi/180, threshold=25, minLineLength=30, maxLineGap=100)

    result = frame.copy()
    if lines is not None:
        for line in lines:
            x1,y1,x2,y2 = line[0]
            cv2.line(result, (x1,y1), (x2,y2), (0,255,0), 6)

    # ROI debug polygon
    h, w = frame.shape[:2]
    lift = 0.15
    top_offset = 0.30
    bottom_y = int(h * (1 - lift))
    top_y    = int(h * (top_offset - lift))

    roi_debug = frame.copy()
    pts = np.array([
        (int(w * 0.02), bottom_y),
        (int(w * 0.98), bottom_y),
        (int(w * 0.80), top_y),
        (int(w * 0.20), top_y)
    ], np.int32)

    cv2.polylines(roi_debug, [pts], isClosed=True, color=(255,0,255), thickness=3)

    cv2.imshow("Original + ROI (magenta)", cv2.resize(roi_debug, (800,600)))
    cv2.imshow("Final - Lane Detection", cv2.resize(result, (800,600)))

    return result


# === VIDEO INPUT ===
cap = cv2.VideoCapture("videos/input.mp4")

if not cap.isOpened():
    print("Theres no bideo! Put input.mp4 in folder.")
    exit()

# === PRAVLJENJE VIDEO OUTPUTA ===
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
fps = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter("videos/output.mp4", fourcc, fps, (width, height))

# === PETLJA ===
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    result_frame = process_frame(frame)

    # SNIMI U VIDEO
    out.write(result_frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print("Video 'output.mp4' was succesfully created!")
