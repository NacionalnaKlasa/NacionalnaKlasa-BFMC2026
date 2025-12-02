import numpy as np
import cv2
from moviepy.editor import VideoFileClip

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


def average_slope_intercept(lines):
    left_lines, left_weights = [], []
    right_lines, right_weights = [], []

    for line in lines:
        x1, y1, x2, y2 = line[0]  # jer je shape (1,4)

        if x2 == x1 or abs(x2 - x1) < 10:
            continue

        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1
        length = np.sqrt((y2 - y1)**2 + (x2 - x1)**2)

        if abs(slope) < 0.5 or abs(slope) > 10:
            continue

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

    return left_lane, right_lane


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


def lane_lines(image, lines):
    # ISPRAVKA: ne koristi "if not lines" → koristi len(lines)
    if len(lines) == 0:
        return []

    left_lane, right_lane = average_slope_intercept(lines)

    y1 = image.shape[0]
    y2 = int(y1 * 0.6)

    left_line = pixel_points(y1, y2, left_lane)
    right_line = pixel_points(y1, y2, right_lane)

    valid_lines = []
    if left_line and len(left_line) == 2:
        valid_lines.append(left_line)
    if right_line and len(right_line) == 2:
        valid_lines.append(right_line)

    return valid_lines


def draw_lane_lines(image, lines, color=(0, 255, 0), thickness=15):
    line_image = np.zeros_like(image)
    for line in lines:
        if line is not None:
            cv2.line(line_image, line[0], line[1], color, thickness)
    return cv2.addWeighted(image, 1.0, line_image, 0.8, 0.0)


def frame_processor(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    roi = create_roi_for_bfmc_car(edges)
    hough_lines = hough_transform(roi)
    lanes = lane_lines(frame, hough_lines)
    result = draw_lane_lines(frame, lanes, color=(0, 255, 0), thickness=15)
    return result


# ==================== POKRETANJE ====================
if __name__ == "__main__":
    input_video = "videos/input.mp4"
    output_video = "videos/outputFinal.mp4"

    print("Obrada videa u toku... (može potrajati par minuta)")
    clip = VideoFileClip(input_video)
    processed_clip = clip.fl_image(frame_processor)
    processed_clip.write_videofile(output_video, audio=False, threads=4, preset='fast')
    print("Gotovo! Video sačuvan:", output_video)