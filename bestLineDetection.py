import cv2
import numpy as np

# ================= ROI =================
def create_roi_for_bfmc_car(image):
    """
    Create a Region of Interest (ROI) polygon to focus on the road/lane area
    """
    h, w = image.shape[:2]

    lift = 0.15
    top_offset = 0.30

    bottom_y = int(h * (1 - lift))
    top_y    = int(h * top_offset)

    # Define ROI polygon
    polygon = np.array([
        (int(w * 0.02), bottom_y),
        (int(w * 0.98), bottom_y),
        (int(w * 0.80), top_y),
        (int(w * 0.20), top_y)
    ], np.int32)

    mask = np.zeros_like(image)
    cv2.fillPoly(mask, [polygon], 255)

    # Apply mask to the image
    return cv2.bitwise_and(image, mask)

# ================= WHITE LINE CHECK =================
def is_white_line(frame, p1, p2, brightness_threshold=180):
    """
    Check if a line is 'white' by sampling points along the line.
    Returns True if average brightness is above the threshold.
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

# ================= SLOPE TO DEGREES =================
def slope_to_degrees(slope):
    """
    Convert slope (dy/dx) to degrees.
    Returns 90° for vertical lines.
    """
    if slope == float('inf') or slope == float('-inf'):
        return 90.0
    return np.degrees(np.arctan(slope))

# ================= FRAME PROCESS =================
def process_frame(frame):
    """
    Process a single video frame:
    - Convert to grayscale
    - Apply CLAHE (contrast enhancement)
    - Apply Gaussian blur
    - Detect edges using Canny
    - Apply ROI mask
    - Detect lines using Hough Transform
    - Draw horizontal lines in blue
    - Draw lane lines in green
    - Compute average slope for left/right lanes
    - Display slopes at bottom of the frame
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 40, 120)
    masked = create_roi_for_bfmc_car(edges)

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

    left_slopes = []
    right_slopes = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]

            # Calculate slope, handle vertical lines
            if x2 == x1:
                slope = float('inf')
            else:
                slope = (y2 - y1) / (x2 - x1)

            length = np.hypot(x2 - x1, y2 - y1)

            # Horizontal white lines → BLUE
            if abs(slope) < 0.2 and length > 25 and is_white_line(frame, (x1, y1), (x2, y2)):
                cv2.line(result, (x1, y1), (x2, y2), (255, 0, 0), 8)
            else:
                # Other lines → GREEN
                cv2.line(result, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Determine the center x of the line
            cx = (x1 + x2) / 2

            # Separate slopes into left/right lanes
            if slope != float('inf') and slope != float('-inf'):
                if cx < w / 2:
                    left_slopes.append(slope)
                else:
                    right_slopes.append(slope)

        # Average slope for left lane
        avg_left_slope = slope_to_degrees(np.mean(left_slopes)) if left_slopes else 0.0

        # Average slope for right lane
        avg_right_slope = slope_to_degrees(np.mean(right_slopes)) if right_slopes else 0.0

        # Display average slopes at bottom of frame
        font_scale = 0.6
        thickness = 1
        margin = 20  # margin from bottom

        cv2.putText(result, f"Left avg slope: {avg_left_slope:.2f} deg",
                    (30, h - margin - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale,
                    (255, 255, 255),
                    thickness,
                    cv2.LINE_AA)

        cv2.putText(result, f"Right avg slope: {avg_right_slope:.2f} deg",
                    (30, h - margin),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale,
                    (255, 255, 255),
                    thickness,
                    cv2.LINE_AA)

    # ================= ROI DEBUG =================
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

    # Display ROI and processed frame
    cv2.imshow("ROI (magenta)", cv2.resize(roi_debug, (800, 600)))
    cv2.imshow("Lane detection", cv2.resize(result, (800, 600)))

    return result

# ================= RUN FUNCTION =================
def run(input_video="videos/input.mp4", output_video="videos/output.avi"):
    """
    Main function to process a video file.
    Can be called from a launcher script (main.py)
    """
    cap = cv2.VideoCapture(input_video)

    if not cap.isOpened():
        print(f"{input_video} not found")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Save output as AVI with XVID codec for wider compatibility
    out = cv2.VideoWriter(output_video, cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        result = process_frame(frame)
        out.write(result)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Video '{output_video}' successfully created!")

# ================= EXECUTE ONLY IF RUN AS SCRIPT =================
if __name__ == "__main__":
    run()
