import cv2

class PostprocessingFrame:
    def __init__(self, config):
       self.roi_y_top = config.ROI_Y.roi_top_y
       self.roi_y_bottom = config.ROI_Y.roi_bottom_y

    def calculate_lane_center(self, left_line, right_line, frame_width):
        """Calculate lane center. If one line missing, assume average lane width"""
        if left_line is None and right_line is None:
            return frame_width // 2
        elif left_line is None:
            lane_width = 200  # assumed width in pixels
            return right_line[0] - lane_width//2
        elif right_line is None:
            lane_width = 200
            return left_line[0] + lane_width//2
        else:
            left_x = (left_line[0] + left_line[2]) // 2
            right_x = (right_line[0] + right_line[2]) // 2
            return (left_x + right_x) // 2
    
    def p_control(self, lane_center, frame_width):
        """Simple proportional control steering signal [-1,1]"""
        error = lane_center - frame_width // 2
        steering = error / (frame_width // 2)  # normalize
        return max(min(steering, 1.0), -1.0)
    
    # Not necessary for car
    def draw_lane_center(self, frame, lane_center, color=(0,0,255), thickness=2):
        """Draw vertical line at lane center"""
        h = frame.shape[0]
        cv2.line(frame, (lane_center, int(h*self.roi_y_top)), (lane_center, int(h*self.roi_y_bottom)), color, thickness)
        return frame