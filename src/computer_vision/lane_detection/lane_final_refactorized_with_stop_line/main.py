import time
import cv2

from typing import Tuple
from dataclasses import dataclass

from preprocessingFrame import PreprocessingFrame
from processingFrame import ProcessingFrame
from postprocessingFrame import PostprocessingFrame


############# Parameters for Preprocessing ##############
# Using dataclass for immutable configuration
@dataclass(frozen=True) 
class Gamma:
    gamma: float = 1.5
    lut: None | list = None
#########################################################

############### Parameters for Processing ###############
@dataclass(frozen=True)
class Canny:
    blur_kernel: int = 5
    canny_low: int = 50
    canny_high: int = 150

@dataclass(frozen=True)
class ROI:
# Trapezoid ROI corners (x_ratio, y_ratio)
    roi_bottom_left: Tuple[float, float] = (0.1, 0.75)
    roi_bottom_right: Tuple[float, float] = (0.9, 0.75)
    roi_top_right: Tuple[float, float] = (0.7, 0.6)
    roi_top_left: Tuple[float, float] = (0.3, 0.6)

############# Parameters for Stop Line #############
@dataclass(frozen=True)
class StopLine:
    min_length_ratio: float = 0.1     # Min dužina linije (30% širine ekrana)
    y_tolerance: int = 10              # Tolerancija za grupiranje linija (±10px)
    slope_threshold: float = 0.5       # Max nagib za horizontalnu liniju
    min_segments: int = 1              # Min broj segmenata za validnu stop liniju

### NAJBOLJI PARAMETRI ZA ZAUSTAVNU
    #0.1
    #10
    #0.4
    #1
#########################################################

############# Parameters for Postprocessing #############
@dataclass(frozen=True)
class Hough:
    hough_threshold: int = 50
    hough_min_line_length: int = 40
    hough_max_line_gap: int = 100
    min_slope: float = 0.3
    max_slope: float = 3.0

@dataclass(frozen=True)
class ROI_Y:
    roi_top_y: float = 0.6
    roi_bottom_y: float = 0.95
#########################################################

class Config:
    def __init__(self):
        self.Gamma = Gamma()
        self.Canny = Canny()
        self.ROI = ROI()
        self.Hough = Hough()
        self.ROI_Y = ROI_Y()
        self.StopLine = StopLine()  # <-- DODATO

def frame_receive(frame):
    print("Frame received:", frame)

def frame_send(frame):
    print("Frame sent:", frame)

def main():
    
    video_path = "/home/konstantin/Documents/ntp_staza_video_novi/output_video1768839027.4817054.avi"
    video = cv2.VideoCapture(video_path)

    config = Config()
    preprocessing = PreprocessingFrame(config)
    processing = ProcessingFrame(config)
    postprocessing = PostprocessingFrame(config)

    while True:
        ret, frame = video.read()
        if not ret:
            break

        frame_receive(frame)
        
        # Preprocessing
        gamma = preprocessing.apply_gamma(frame)

        # Processing
        edges = processing.apply_canny(gamma)
        roi = processing.apply_roi(edges)
        lane_lines, stop_lines = processing.apply_hough(roi)
        left_avg, right_avg = processing.average_lines(lane_lines, frame.shape[1])

        # Detekcija i fitovanje zaustavne linije
        stop_line = processing.fit_stop_line(stop_lines, frame.shape[1])

        # Postprocessing
        lane_center = postprocessing.calculate_lane_center(left_avg, right_avg, frame.shape[1])
        steering = postprocessing.p_control(lane_center, frame.shape[1])

        # Vizualizacija
        vis_frame = processing.draw_lines(gamma, left_avg, right_avg)
        if stop_line is not None:
            cv2.line(vis_frame, (stop_line[0], stop_line[1]), 
                    (stop_line[2], stop_line[3]), (255, 0, 0), 4)
            print("ZAUSTAVNA LINIJA DETEKTOVANA!")
        vis_frame = postprocessing.draw_lane_center(vis_frame, lane_center)

        cv2.imshow("Lane Detection", vis_frame)
        print("Steering:", steering)

        frame_send(frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(1/18)

    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


#RADI ONAKOOm NIJE LOSE
#     while True:
#         ret, frame = video.read()
#         if not ret:
#             break

#         frame_receive(frame)
        
#         # Preprocessing
#         gamma = preprocessing.apply_gamma(frame)

#         # Processing
#         edges = processing.apply_canny(gamma)
#         roi = processing.apply_roi(edges)
#         lane_lines, stop_lines = processing.apply_hough(roi)
#         left_avg, right_avg = processing.average_lines(lane_lines, frame.shape[1])

#         # Detekcija zaustavne linije - biramo najnižu (najbližu autu)
#         stop_line = None
#         if stop_lines:
#             stop_line = max(stop_lines, key=lambda line: (line[1] + line[3]) / 2)

#         # Postprocessing
#         lane_center = postprocessing.calculate_lane_center(left_avg, right_avg, frame.shape[1])
#         steering = postprocessing.p_control(lane_center, frame.shape[1])

#         # Vizualizacija
#         vis_frame = processing.draw_lines(gamma, left_avg, right_avg)
#         if stop_line is not None:
#             cv2.line(vis_frame, (stop_line[0], stop_line[1]), 
#                     (stop_line[2], stop_line[3]), (0, 0, 255), 4)
#             print("ZAUSTAVNA LINIJA DETEKTOVANA!")
#         vis_frame = postprocessing.draw_lane_center(vis_frame, lane_center)

#         cv2.imshow("Lane Detection", vis_frame)
#         print("Steering:", steering)

#         frame_send(frame)
        
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#         time.sleep(0.05)

#     video.release()
#     cv2.destroyAllWindows()
    
# if __name__ == "__main__":
#     main()


##POCETNI KOD
#     while True:
#         ret, frame = video.read()
#         if not ret:
#             break

#         frame_receive(frame)
        
#         # # Preprocessing
#         gamma = preprocessing.apply_gamma(frame)

#         # # Processing
#         # edges = processing.apply_canny(gamma)
#         # roi = processing.apply_roi(edges)
#         # lines = processing.apply_hough(roi)
#         # left_avg, right_avg = processing.average_lines(lines, frame.shape[1])

#         # # Detekcija i crtanje zaustavne linije
#         # stop_line = processing.detect_stop_line(lines)
       

#         # # Postprocessing
#         # lane_center = postprocessing.calculate_lane_center(left_avg, right_avg, frame.shape[1])
#         # steering = postprocessing.p_control(lane_center, frame.shape[1])

#         # frame_send(frame)

#         # # Vizualization
#         # # Not necessary for car
        
#         # vis_frame = processing.draw_lines(gamma, left_avg, right_avg)
#         # vis_frame = postprocessing.draw_lane_center(vis_frame, lane_center)

#         ##TESTING
#         # Processing
#         edges = processing.apply_canny(gamma)
#         roi = processing.apply_roi(edges)
#         lane_lines, stop_lines = processing.apply_hough(roi)  # <-- IZMENA
#         left_avg, right_avg = processing.average_lines(lane_lines, frame.shape[1])  # <-- Koristimo lane_lines

#         # Detekcija zaustavne linije - biramo najnižu (najbližu autu)
#         stop_line = None
#         if stop_lines:
#         # Biramo liniju sa najvećim y (najniža na ekranu = najbliža autu)
#             stop_line = max(stop_lines, key=lambda line: (line[1] + line[3]) / 2)

# #         # Vizualizacija
# #         vis_frame = processing.draw_lines(gamma, left_avg, right_avg)
# #         if stop_line is not None:
# #             cv2.line(vis_frame, (stop_line[0], stop_line[1]), 
# #                     (stop_line[2], stop_line[3]), (0,0,255), 4)
# #             print("ZAUSTAVNA LINIJA DETEKTOVANA!")
# #         vis_frame = postprocessing.draw_lane_center(vis_frame, lane_center)
# #         ######

# #         cv2.imshow("Lane Detection", vis_frame)
# #         print("Steering:", steering)

# #         frame_send(frame)
# #         if cv2.waitKey(1) & 0xFF == ord('q'):
# #             break
# #         time.sleep(0.05)

# #     video.release()
# #     cv2.destroyAllWindows()
    
# # if __name__ == "__main__":
# #     main()