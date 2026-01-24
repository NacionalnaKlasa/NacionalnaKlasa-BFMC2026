#!/usr/bin/env python3
"""
Lane Detection Component - Example Usage

Simple integration example showing how to use the lane detection component.
"""

import time
import cv2
#from lane_final_nonrefactorized import Pipeline, PipelineConfig, PreprocessingConfig, LaneDetectionConfig, PostprocessingConfig
from pipeline import Pipeline, PipelineConfig
from preprocessing import PreprocessingConfig
from lane_detection import LaneDetectionConfig
from postprocessing import PostprocessingConfig

def main():
    # Configure the pipeline
    config = PipelineConfig(
        preprocessing=PreprocessingConfig(
            gamma=1.5,
            blur_kernel=5,
            canny_low=50,
            canny_high=150,
            # Trapezoid ROI corners (x_ratio, y_ratio)
            roi_bottom_left=(0.1, 0.75),
            roi_bottom_right=(0.9, 0.75),
            roi_top_right=(0.7, 0.6),
            roi_top_left=(0.3, 0.6),
        ),
        detection=LaneDetectionConfig(
            hough_threshold=50,
            hough_min_line_length=40,
            hough_max_line_gap=100,
            min_slope=0.3,
            max_slope=3.0,
            roi_top_y=0.6,
            roi_bottom_y=0.95,
        ),
        postprocessing=PostprocessingConfig(
            kp=0.5,
            target_center=0.5,
            deadzone=0.02,
        ),
        debug_mode=True,
    )
    
    # Create pipeline instance
    pipeline = Pipeline(config)
    
    # Open video source (camera or file)
    cap = cv2.VideoCapture("/home/konstantin/Documents/ntp_staza_video_novi/output_video1768839027.4817054.avi")
    
    frame_id = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame through pipeline
        result = pipeline.process(frame, frame_id)
        frame_id += 1
        
        # Use the steering output
        if result.success and result.steering.valid:
            steering = result.steering.steering  # Range: [-1, +1]
            error = result.steering.error
            print(f"Frame {frame_id:4d} | Steering: {steering:+.2f} | Error: {error:+.3f}")
        
        # Show debug visualization
        if result.debug_frame is not None:
            cv2.imshow("Lane Detection", result.debug_frame)
        
        if cv2.waitKey(1) == 27:  # ESC to exit
            break
        time.sleep(1/30.0)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
