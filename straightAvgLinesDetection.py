import cv2
import numpy as np

# ================= ROI =================
def create_roi_for_bfmc_car(image):
    """
    Create a Region of Interest (ROI) polygon to focus on the lane area
    """
    h, w = image.shape[:2]

    lift = 0.15
    top_offset = 0.30

    bottom_y = int(h * (1 - lift))
    top_y    = int(h * top_offset)

    # Define polygon for ROI
    polygon = np.array([
        (int(w * 0.02), bottom_y),
        (int(w * 0.98), bottom_y),
        (int(w * 0.80), top_y),
        (int(w * 0.20), top_y)
    ], np.int32)

    mask = np.zeros_like(image)
    cv2.fillPoly(mask, [polygon], 255)

    # Mask the original image to keep only the ROI
    return cv2.bitwise_and(image, mask)


# ================= WHITE LINE CHECK =================
def is_white_line(frame, p1, p2, brightness_threshold=180):
    """
    Check if a line is 'white' by sampling points along it
    """
    xs = np.linspace(p1[0], p2[0], 10).astype(int)
    ys = np.linspace(p1[1], p2[1], 10).astype(int)

    values = []
    for x, y in zip(xs, ys):
        if 0 <= x < frame.shape[1] and 0 <= y < frame.shape[0]:
            b, g, r = frame[y, x]
            values.append((r, g, b))

    if not values:
        return False

    avg_color = np.mean(values, axis=0)
    return avg_color.mean() > brightness_threshold


# ================= FRAME PROCESS =================
def process_frame(frame):
    """
    Process a single video frame:
    - Convert to grayscale
    - Apply CLAHE (contrast enhancement)
    - Gaussian blur
    - Canny edge detection
    - Detect Hough lines
    - Classify horizontal lines vs. lane lines
    - Draw lines and slope angles
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 40, 120)
    masked = create_roi_for_bfmc_car(edges)

    # Detect lines using Hough Transform
    lines = cv2.HoughLinesP(
        masked,
        rho=1,
        theta=np.pi / 180,
        threshold=25,
        minLineLength=30,
        maxLineGap=100
    )

    result = frame.copy()
    h, w = frame.shape[:2]

    if lines is not None:
        left_lines = []
        right_lines = []
        horizontal_lines = []

        # Classify each detected line
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x1 == x2:
                continue  # skip vertical lines

            slope = (y2 - y1) / (x2 - x1)
            length = np.hypot(x2 - x1, y2 - y1)
            center_x = (x1 + x2) / 2

            # 1. Horizontal white lines (parking/start/finish)
            if abs(slope) < 0.2 and length > 40 and is_white_line(frame, (x1,y1), (x2,y2)):
                horizontal_lines.append(line)
                cv2.line(result, (x1,y1), (x2,y2), (255, 0, 0), 9)  # BLUE thick

            # 2. Other lane lines – separate into left/right based on position
            else:
                if length > 30:  # filter short lines
                    if center_x < w / 2:
                        # Left side – expect negative or slightly positive slope
                        if slope < 2.0:
                            left_lines.append([x1, y1, x2, y2])
                    else:
                        # Right side – expect positive or slightly negative slope
                        if slope > -2.0:
                            right_lines.append([x1, y1, x2, y2])

        # =================== FUNCTION TO AVERAGE LINES ===================
        def average_line(lines_list):
            if not lines_list:
                return None
            lines = np.array(lines_list)
            x1s, y1s, x2s, y2s = lines[:,0], lines[:,1], lines[:,2], lines[:,3]
            # Average coordinates
            x1 = int(np.mean(x1s))
            y1 = int(np.mean(y1s))
            x2 = int(np.mean(x2s))
            y2 = int(np.mean(y2s))
            return (x1, y1, x2, y2)

        # =================== DRAW AVERAGE LANE LINES ===================
        # Left lane
        if left_lines:
            lx1, ly1, lx2, ly2 = average_line(left_lines)
            cv2.line(result, (lx1, ly1), (lx2, ly2), (0, 255, 0), 7)  # GREEN thick

        # Right lane
        if right_lines:
            rx1, ry1, rx2, ry2 = average_line(right_lines)
            cv2.line(result, (rx1, ry1), (rx2, ry2), (0, 255, 0), 7)  # GREEN thick

        # =================== DISPLAY SLOPES (average only) ===================
        def get_slope_degrees(x1, y1, x2, y2):
            if x2 == x1:
                return 90.0
            slope = (y2 - y1) / (x2 - x1)
            return round(np.degrees(np.arctan(slope)), 2)

        left_text = "Left: N/A"
        right_text = "Right: N/A"

        if left_lines:
            left_text = f"Left avg: {get_slope_degrees(lx1, ly1, lx2, ly2)} deg"
        if right_lines:
            right_text = f"Right avg: {get_slope_degrees(rx1, ry1, rx2, ry2)} deg"

        # Draw the slope text at bottom of frame
        font_scale = 0.6
        thickness = 1
        margin = 30  # margin from bottom

        cv2.putText(result, left_text,
                    (30, h - margin - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale,
                    (255, 255, 255),
                    thickness,
                    cv2.LINE_AA)

        cv2.putText(result, right_text,
                    (30, h - margin),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale,
                    (255, 255, 255),
                    thickness,
                    cv2.LINE_AA)

    # ============ ROI DEBUG ============ 
    lift = 0.15
    top_offset = 0.30
    bottom_y = int(h * (1 - lift))
    top_y = int(h * top_offset)
    roi_debug = frame.copy()
    pts = np.array([
        (int(w * 0.02), bottom_y),
        (int(w * 0.98), bottom_y),
        (int(w * 0.80), top_y),
        (int(w * 0.20), top_y)
    ], np.int32)
    cv2.polylines(roi_debug, [pts], True, (255, 0, 255), 3)
    cv2.imshow("ROI (magenta)", cv2.resize(roi_debug, (800, 600)))
    cv2.imshow("Lane detection", cv2.resize(result, (800, 600)))

    return result


# ================= RUN FUNCTION =================
def run_str_avg_lines(input_video="videos/input.mp4", output_video="videos/outputStrAvgLines.avi"):
    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        print(f"{input_video} not found")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_video, cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        out.write(process_frame(frame))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Video '{output_video}' successfully created!")

if __name__ == "__main__":
    run_str_avg_lines()