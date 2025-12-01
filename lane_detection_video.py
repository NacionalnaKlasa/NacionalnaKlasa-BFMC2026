import numpy as np
import pandas as pd
import cv2
from moviepy.editor import VideoFileClip

def region_of_interest(image):
    height, width = image.shape[:2]

    # same logic as in create_roi_for_bfmc_car()
    lift = 0.15
    top_offset = 0.30

    bottom_y = int(height * (1 - lift))
    top_y    = int(height * top_offset)

    vertices = np.array([[ 
        (int(width * 0.02), bottom_y),   # bottom left
        (int(width * 0.98), bottom_y),   # bottom right
        (int(width * 0.80), top_y),      # top right
        (int(width * 0.20), top_y)       # top left
    ]], dtype=np.int32)

    # mask compatible with grayscale or BGR
    mask = np.zeros_like(image)
    if len(image.shape) > 2:
        ignore_mask_color = (255,) * image.shape[2]
    else:
        ignore_mask_color = 255

    cv2.fillPoly(mask, vertices, ignore_mask_color)
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image


def hough_transform(image):
    return cv2.HoughLinesP(
        image,
        rho=1,
        theta=np.pi/180,
        threshold=20,
        minLineLength=20,
        maxLineGap=500
    )


def average_slope_intercept(lines):
    left_lines, left_weights = [], []
    right_lines, right_weights = [], []

    if lines is None:
        return None, None

    for line in lines:
        for x1, y1, x2, y2 in line:
            if x1 == x2:
                continue   # skip vertical lines

            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1

            # ignore almost horizontal lines
            if abs(slope) < 0.01:
                continue    

            length = np.sqrt((y2 - y1)**2 + (x2 - x1)**2)

            if slope < 0:
                left_lines.append((slope, intercept))
                left_weights.append(length)
            else:
                right_lines.append((slope, intercept))
                right_weights.append(length)

    left_lane  = np.dot(left_weights, left_lines) / np.sum(left_weights) if left_weights else None
    right_lane = np.dot(right_weights, right_lines) / np.sum(right_weights) if right_weights else None

    return left_lane, right_lane


def get_line_points(y1, y2, line):
    if line is None:
        return None
    slope, intercept = line

    if slope == 0:
        return None

    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)

    return (x1, int(y1)), (x2, int(y2))


def make_lane_lines(image, lines):
    left_lane, right_lane = average_slope_intercept(lines)

    height = image.shape[0]
    lift = 0.15
    top_offset = 0.30

    y1 = int(height * (1 - lift))      # bottom of ROI
    y2 = int(height * top_offset)      # top of ROI

    return get_line_points(y1, y2, left_lane), get_line_points(y1, y2, right_lane)


def draw_lane_lines(image, lines, color=[255, 0, 0], thickness=12):
    line_image = np.zeros_like(image)
    for line in lines:
        if line is not None:
            cv2.line(line_image, *line, color, thickness)
    return cv2.addWeighted(image, 1.0, line_image, 1.0, 0.0)


def process_frame(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    region = region_of_interest(edges)
    hough = hough_transform(region)
    return draw_lane_lines(image, make_lane_lines(image, hough))


def process_video(input_video, output_video):
    clip = VideoFileClip(input_video, audio=False)
    processed_clip = clip.fl_image(process_frame)
    processed_clip.write_videofile(output_video, audio=False)


process_video("videos/input.mp4", "videos/outputCode.mp4")
