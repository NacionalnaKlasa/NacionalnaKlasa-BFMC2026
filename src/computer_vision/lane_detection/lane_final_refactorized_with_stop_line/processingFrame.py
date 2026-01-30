import cv2
import numpy as np
from typing import Tuple, List

class ProcessingFrame():
    def __init__(self, config):
        self.blur_kernel = config.Canny.blur_kernel
        self.canny_low = config.Canny.canny_low
        self.canny_high = config.Canny.canny_high
        self.roi = config.ROI
        self.hough_threshold = config.Hough.hough_threshold
        self.hough_min_line_length = config.Hough.hough_min_line_length
        self.hough_max_line_gap = config.Hough.hough_max_line_gap
        self.min_slope = config.Hough.min_slope
        self.max_slope = config.Hough.max_slope

        # Stop line parametri
        self.stop_min_length_ratio = config.StopLine.min_length_ratio
        self.stop_y_tolerance = config.StopLine.y_tolerance
        self.stop_slope_threshold = config.StopLine.slope_threshold
        self.stop_min_segments = config.StopLine.min_segments
    
    def apply_canny(self, frame: np.ndarray) -> np.ndarray:
        """Convert to grayscale and apply Gaussian blur + Canny"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
        kernel = self.blur_kernel
        if kernel % 2 == 0:
            kernel += 1
        blurred = cv2.GaussianBlur(gray, (kernel, kernel), 0)
        edges = cv2.Canny(blurred, self.canny_low, self.canny_high)
        return edges
    
    def apply_roi(self, edges: np.ndarray) -> np.ndarray:
        """Apply trapezoid ROI mask"""
        h, w = edges.shape
        pts = np.array([[
            (int(w * self.roi.roi_bottom_left[0]), int(h * self.roi.roi_bottom_left[1])),
            (int(w * self.roi.roi_bottom_right[0]), int(h * self.roi.roi_bottom_right[1])),
            (int(w * self.roi.roi_top_right[0]), int(h * self.roi.roi_top_right[1])),
            (int(w * self.roi.roi_top_left[0]), int(h * self.roi.roi_top_left[1]))
        ]], dtype=np.int32)
        mask = np.zeros_like(edges)
        cv2.fillPoly(mask, pts, 255)
        return cv2.bitwise_and(edges, mask)
    
    # def apply_hough(self, edges: np.ndarray) -> List[Tuple[int,int,int,int]]:
    #     """Detect lines using Hough Transform and filter by slope"""
    #     lines = cv2.HoughLinesP(
    #         edges,
    #         rho=1,
    #         theta=np.pi/180,
    #         threshold=self.hough_threshold,
    #         minLineLength=self.hough_min_line_length,
    #         maxLineGap=self.hough_max_line_gap
    #     )
    #     filtered = []
    #     if lines is not None:
    #         for x1, y1, x2, y2 in lines[:,0]:
    #             if x2 - x1 == 0:
    #                 continue
    #             slope = (y2 - y1) / (x2 - x1)
    #             if self.min_slope < abs(slope) < self.max_slope:
    #                 filtered.append((x1, y1, x2, y2))
    #     return filtered
    
    #OVO ISPOD JE RADILO SA STOP ZNAKOM
    # def apply_hough(self, edges: np.ndarray) -> Tuple[List[Tuple[int,int,int,int]], List[Tuple[int,int,int,int]]]:
    #     """Detect lines using Hough Transform - separate lane lines and stop lines"""
    #     lines = cv2.HoughLinesP(
    #         edges,
    #         rho=1,
    #         theta=np.pi/180,
    #         threshold=self.hough_threshold,
    #         minLineLength=self.hough_min_line_length,
    #         maxLineGap=self.hough_max_line_gap
    #     )
        
    #     lane_lines = []  # Vertikalne linije (trake)
    #     stop_lines = []  # Horizontalne linije (zaustavne)
        
    #     if lines is not None:
    #         for x1, y1, x2, y2 in lines[:,0]:
    #             if x2 - x1 == 0:
    #                 continue
    #             slope = (y2 - y1) / (x2 - x1)
                
    #             # Horizontalne linije (zaustavne)
    #             if abs(slope) < 0.3:
    #                 stop_lines.append((x1, y1, x2, y2))
    #             # Vertikalne linije (trake)
    #             elif self.min_slope < abs(slope) < self.max_slope:
    #                 lane_lines.append((x1, y1, x2, y2))
    
    #     return lane_lines, stop_lines
    def apply_hough(self, edges: np.ndarray) -> Tuple[List[Tuple[int,int,int,int]], List[Tuple[int,int,int,int]]]:
        """Detect lines using Hough Transform - separate lane lines and stop lines"""
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=self.hough_threshold,
            minLineLength=self.hough_min_line_length,
            maxLineGap=self.hough_max_line_gap
        )
        
        lane_lines = []
        stop_lines = []
        
        if lines is not None:
            for x1, y1, x2, y2 in lines[:,0]:
                if x2 - x1 == 0:
                    continue
                slope = (y2 - y1) / (x2 - x1)
                
                # Horizontalne linije (zaustavne) - koristi konfigurabilan parametar
                if abs(slope) < self.stop_slope_threshold:
                    stop_lines.append((x1, y1, x2, y2))
                # Vertikalne linije (trake)
                elif self.min_slope < abs(slope) < self.max_slope:
                    lane_lines.append((x1, y1, x2, y2))
        
        return lane_lines, stop_lines

    def average_lines(self, lines: List[Tuple[int,int,int,int]], width: int) -> Tuple[Tuple[int,int,int,int], Tuple[int,int,int,int]]:
        """Separate left/right lines and average them"""
        left_lines = []
        right_lines = []
        for x1, y1, x2, y2 in lines:
            slope = (y2 - y1)/(x2 - x1)
            if slope < 0:
                left_lines.append((x1,y1,x2,y2))
            else:
                right_lines.append((x1,y1,x2,y2))

        def line_average(group):
            if not group:
                return None
            x_coords = []
            y_coords = []
            for x1,y1,x2,y2 in group:
                x_coords += [x1,x2]
                y_coords += [y1,y2]
            poly = np.polyfit(y_coords, x_coords, 1)  # x = m*y + b
            y1_out = min(y_coords)
            y2_out = max(y_coords)
            x1_out = int(poly[0]*y1_out + poly[1])
            x2_out = int(poly[0]*y2_out + poly[1])
            return (x1_out, y1_out, x2_out, y2_out)

        left_avg = line_average(left_lines)
        right_avg = line_average(right_lines)
        return left_avg, right_avg
    
    # Not necessary for car
    def draw_lines(self, frame: np.ndarray, left_line, right_line, color=(0,255,0), thickness=3) -> np.ndarray:
        """Draw left and right lines on frame"""
        line_img = frame.copy()
        if left_line is not None:
            cv2.line(line_img, (left_line[0], left_line[1]), (left_line[2], left_line[3]), color, thickness)
        if right_line is not None:
            cv2.line(line_img, (right_line[0], right_line[1]), (right_line[2], right_line[3]), color, thickness)
        return line_img
    
    def detect_stop_line(self, lines: List[Tuple[int,int,int,int]], slope_threshold: float = 0.1) -> Tuple[int,int,int,int]:
        """
        Detektuje horizontalnu (zaustavnu) liniju među pronađenim linijama.
        Vraća koordinate linije ili None ako nije pronađena.
        """
        for x1, y1, x2, y2 in lines:
            if x2 - x1 == 0:
                continue
            slope = (y2 - y1) / (x2 - x1)
            if abs(slope) < slope_threshold:
                return (x1, y1, x2, y2)
        return None
    # def fit_stop_line(self, stop_lines: List[Tuple[int,int,int,int]], frame_width: int, min_length_ratio: float = 0.3) -> Tuple[int,int,int,int]:
    #     """
    #     Filtrira i fituje zaustavnu liniju.
    #     - Filtrira kratke segmente (isprekidane linije)
    #     - Spaja sve segmente u jednu kontinualnu liniju
        
    #     Args:
    #         stop_lines: Lista detektovanih horizontalnih linija
    #         frame_width: Širina frejma
    #         min_length_ratio: Minimalna dužina linije kao procenat širine frejma (default 30%)
        
    #     Returns:
    #         Fitovana zaustavna linija ili None
    #     """
    #     if not stop_lines:
    #         return None
        
    #     # KORAK 1: Filtriranje - ukloni kratke segmente (delove isprekidanih linija)
    #     min_length = frame_width * min_length_ratio
    #     filtered_lines = []
        
    #     for x1, y1, x2, y2 in stop_lines:
    #         length = abs(x2 - x1)
    #         if length >= min_length:
    #             filtered_lines.append((x1, y1, x2, y2))
        
    #     if not filtered_lines:
    #         return None
        
    #     # KORAK 2: Biramo najnižu liniju (najbliža autu)
    #     closest_line = max(filtered_lines, key=lambda line: (line[1] + line[3]) / 2)
    #     avg_y = (closest_line[1] + closest_line[3]) // 2
        
    #     # KORAK 3: Skupljamo sve segmente koji su na sličnoj y-poziciji (±10px)
    #     y_threshold = 10
    #     similar_lines = []
    #     for x1, y1, x2, y2 in filtered_lines:
    #         line_y = (y1 + y2) // 2
    #         if abs(line_y - avg_y) <= y_threshold:
    #             similar_lines.append((x1, y1, x2, y2))
        
    #     # KORAK 4: Fitovanje - spajamo sve segmente u jednu liniju
    #     all_x = []
    #     all_y = []
    #     for x1, y1, x2, y2 in similar_lines:
    #         all_x.extend([x1, x2])
    #         all_y.extend([y1, y2])
        
    #     # Računamo prosečnu y poziciju
    #     fitted_y = int(np.mean(all_y))
        
    #     # Krajnje tačke su min i max x koordinata
    #     fitted_x1 = min(all_x)
    #     fitted_x2 = max(all_x)
        
    #     return (fitted_x1, fitted_y, fitted_x2, fitted_y)

    def fit_stop_line(self, stop_lines: List[Tuple[int,int,int,int]], frame_width: int) -> Tuple[int,int,int,int]:
        """
        Filtrira i fituje zaustavnu liniju koristeći konfiguracione parametre.
        """
        if not stop_lines:
            return None
        
        # KORAK 1: Filtriranje
        min_length = frame_width * self.stop_min_length_ratio
        filtered_lines = []
        
        for x1, y1, x2, y2 in stop_lines:
            length = abs(x2 - x1)
            if length >= min_length:
                filtered_lines.append((x1, y1, x2, y2))
        
        if not filtered_lines:
            return None
        
        # KORAK 2: Biramo najnižu liniju
        closest_line = max(filtered_lines, key=lambda line: (line[1] + line[3]) / 2)
        avg_y = (closest_line[1] + closest_line[3]) // 2
        
        # KORAK 3: Skupljamo slične linije
        similar_lines = []
        for x1, y1, x2, y2 in filtered_lines:
            line_y = (y1 + y2) // 2
            if abs(line_y - avg_y) <= self.stop_y_tolerance:
                similar_lines.append((x1, y1, x2, y2))
        
        # KORAK 4: Provera minimalnog broja segmenata
        if len(similar_lines) < self.stop_min_segments:
            return None
        
        # KORAK 5: Fitovanje
        all_x = []
        all_y = []
        for x1, y1, x2, y2 in similar_lines:
            all_x.extend([x1, x2])
            all_y.extend([y1, y2])
        
        fitted_y = int(np.mean(all_y))
        fitted_x1 = min(all_x)
        fitted_x2 = max(all_x)
        
        return (fitted_x1, fitted_y, fitted_x2, fitted_y)