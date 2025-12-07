import numpy as np
import cv2
from moviepy.editor import VideoFileClip

# ============================================================
# ROI ZA BFMC AUTO
# ============================================================
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

# ============================================================
# PROVERA DA LI JE LINIJA BELA
# ============================================================
def is_white_line(frame, p1, p2, brightness_threshold=180):
    xs = np.linspace(p1[0], p2[0], 10).astype(int)
    ys = np.linspace(p1[1], p2[1], 10).astype(int)

    values = []
    for x, y in zip(xs, ys):
        if 0 <= x < frame.shape[1] and 0 <= y < frame.shape[0]:
            b, g, r = frame[y, x]
            values.append((r, g, b))

    if len(values) == 0:
        return False

    avg_color = np.mean(values, axis=0)

    return avg_color.mean() > brightness_threshold

# ============================================================
# HOUGH TRANSFORM
# ============================================================
def hough_transform(image):
    rho = 1
    theta = np.pi / 180
    threshold = 20
    minLineLength = 20
    maxLineGap = 300

    lines = cv2.HoughLinesP(image, rho, theta, threshold,
                            minLineLength=minLineLength,
                            maxLineGap=maxLineGap)
    return lines if lines is not None else []

# ============================================================
# DETEKCIJA LINIJA: LEVA, DESNA, BELA HORIZONTALNA
# ============================================================
def average_slope_intercept(lines, frame):
    left_lines, left_weights = [], []
    right_lines, right_weights = [], []
    horizontal_lines = []

    for line in lines:
        x1, y1, x2, y2 = line[0]

        if x2 == x1:
            continue

        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1
        length = np.sqrt((y2 - y1)**2 + (x2 - x1)**2)

        # HORIZONTALNE (BELI FILTER)
        if abs(slope) < 0.2:
            if length > 25:
                if is_white_line(frame, (x1, y1), (x2, y2)):
                    horizontal_lines.append(((x1, y1), (x2, y2)))
            continue

        # LEVA / DESNA TRKA
        if slope < 0:
            left_lines.append((slope, intercept))
            left_weights.append(length)
        else:
            right_lines.append((slope, intercept))
            right_weights.append(length)

    def weighted_avg(lines, weights):
        if len(lines) == 0:
            return None
        return np.average(lines, axis=0, weights=weights)

    left_lane = weighted_avg(left_lines, left_weights)
    right_lane = weighted_avg(right_lines, right_weights)

    return left_lane, right_lane, horizontal_lines

# ============================================================
# PRETVARANJE NAGIBA U KOORDINATE
# ============================================================
def pixel_points(y1, y2, line):
    if line is None:
        return None

    slope, intercept = line

    if abs(slope) < 1e-3:
        slope = 1e-3 if slope >= 0 else -1e-3
    if abs(slope) > 50:
        slope = 50 if slope > 0 else -50

    try:
        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)
        return ((x1, int(y1)), (x2, int(y2)))
    except:
        return None

# ============================================================
# SVI LINIJSKI SEGMENTI
# ============================================================
def lane_lines(image, hough_lines):
    if len(hough_lines) == 0:
        return [], []

    left_lane, right_lane, horizontal = average_slope_intercept(hough_lines, image)

    y1 = image.shape[0]
    y2 = int(y1 * 0.6)

    left_line  = pixel_points(y1, y2, left_lane)
    right_line = pixel_points(y1, y2, right_lane)

    lane_lines_out = []
    if left_line:
        lane_lines_out.append(left_line)
    if right_line:
        lane_lines_out.append(right_line)

    return lane_lines_out, horizontal

# ============================================================
# DETEKCIJA RASKRSNICE
# ============================================================
def detect_intersection(horizontal_lines, min_count=1):
    return len(horizontal_lines) >= min_count

# ============================================================
# CRTANJE LINIJA
# ============================================================
def draw_lane_lines(image, lane_lines, horizontal_lines,
                    color=(0, 255, 0), thickness=15):
    line_image = np.zeros_like(image)

    # Lane lines (green)
    for line in lane_lines:
        cv2.line(line_image, line[0], line[1], color, thickness)

    # Horizontal white lines (yellow)
    for h in horizontal_lines:
        cv2.line(line_image, h[0], h[1], (0, 255, 255), 10)

    return cv2.addWeighted(image, 1.0, line_image, 0.8, 0.0)

# ============================================================
# FRAME PROCESSOR
# ============================================================
def frame_processor(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    roi = create_roi_for_bfmc_car(edges)

    hough_lines = hough_transform(roi)
    lanes, horizontal = lane_lines(frame, hough_lines)

    result = draw_lane_lines(frame, lanes, horizontal)


    return result

# ============================================================
# MAIN — VIDEO PROCESSING
# ============================================================
if __name__ == "__main__":
    input_video = "videos/input.mp4"
    output_video = "videos/outputFinal.mp4"

    print("Obrada videa u toku... (može potrajati nekoliko minuta)")

    clip = VideoFileClip(input_video)
    processed_clip = clip.fl_image(frame_processor)
    processed_clip.write_videofile(output_video,
                                   audio=False,
                                   threads=4,
                                   preset='fast')

    print("Gotovo! Video sačuvan:", output_video)
