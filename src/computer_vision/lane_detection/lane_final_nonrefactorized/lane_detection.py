"""
Lane Detection Module

Handles line detection and lane extraction from preprocessed edges.
"""

import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class Line:
    """Represents a detected line segment"""
    start: Tuple[float, float]  # (x, y)
    end: Tuple[float, float]    # (x, y)
    slope: float = 0.0
    intercept: float = 0.0
    
    def __post_init__(self):
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        if abs(dx) > 1e-6:
            self.slope = dy / dx
            self.intercept = self.start[1] - self.slope * self.start[0]
        else:
            self.slope = float('inf')
            self.intercept = self.start[0]
    
    @property
    def length(self) -> float:
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        return np.sqrt(dx * dx + dy * dy)


@dataclass
class LaneLines:
    """Container for detected left and right lane lines"""
    left: Optional[Line] = None
    right: Optional[Line] = None
    all_lines: List[Line] = field(default_factory=list)
    
    def valid(self) -> bool:
        return self.left is not None or self.right is not None
    
    def both_valid(self) -> bool:
        return self.left is not None and self.right is not None


@dataclass
class LaneDetectionConfig:
    """Configuration for lane detection stage"""
    # Hough transform parameters
    hough_rho: float = 1.0
    hough_theta: float = np.pi / 180
    hough_threshold: int = 50
    hough_min_line_length: float = 50
    hough_max_line_gap: float = 100
    
    # Lane filtering
    split_ratio: float = 0.5          # Left/right split point
    min_slope: float = 0.3            # Minimum valid slope
    max_slope: float = 3.0            # Maximum valid slope
    
    # ROI for line extrapolation (y ratios)
    roi_top_y: float = 0.6
    roi_bottom_y: float = 1


@dataclass
class LaneDetectionResult:
    """Output from lane detection stage"""
    lanes: LaneLines = field(default_factory=LaneLines)
    success: bool = False
    error_msg: str = ""


class LaneDetection:
    """
    Lane detection stage
    
    Pipeline: Edges -> Hough Transform -> Filter Lines -> Average -> Lane Lines
    """
    
    def __init__(self, config: LaneDetectionConfig = None):
        self._config = config or LaneDetectionConfig()
    
    def configure(self, config: LaneDetectionConfig) -> None:
        """Update configuration"""
        self._config = config
    
    @property
    def config(self) -> LaneDetectionConfig:
        """Get current configuration"""
        return self._config
    
    def _detect_lines(self, edges: np.ndarray) -> List[Line]:
        """Detect lines using Hough transform"""
        hough_lines = cv2.HoughLinesP(
            edges,
            rho=self._config.hough_rho,
            theta=self._config.hough_theta,
            threshold=self._config.hough_threshold,
            minLineLength=self._config.hough_min_line_length,
            maxLineGap=self._config.hough_max_line_gap
        )
        
        if hough_lines is None:
            return []
        
        lines = []
        for line in hough_lines:
            x1, y1, x2, y2 = line[0]
            lines.append(Line(
                start=(float(x1), float(y1)),
                end=(float(x2), float(y2))
            ))
        return lines
    
    def _is_valid_slope(self, slope: float) -> bool:
        """Check if slope is within valid range"""
        abs_slope = abs(slope)
        return self._config.min_slope <= abs_slope <= self._config.max_slope
    
    def _average_lines(self, lines: List[Line], frame_height: int) -> Optional[Line]:
        """Average multiple lines into a single mean line"""
        if not lines:
            return None
        
        total_weight = 0.0
        avg_slope = 0.0
        avg_intercept = 0.0
        
        for line in lines:
            if abs(line.slope) != float('inf'):
                length = line.length
                avg_slope += line.slope * length
                avg_intercept += line.intercept * length
                total_weight += length
        
        if total_weight < 1e-6 or abs(avg_slope / total_weight) < 1e-6:
            return None
        
        avg_slope /= total_weight
        avg_intercept /= total_weight
        
        # Extrapolate from bottom to top of ROI
        y1 = int(frame_height * self._config.roi_bottom_y)
        y2 = int(frame_height * self._config.roi_top_y)
        
        x1 = (y1 - avg_intercept) / avg_slope
        x2 = (y2 - avg_intercept) / avg_slope
        
        return Line(start=(x1, float(y1)), end=(x2, float(y2)))
    
    def _separate_lines(self, lines: List[Line], 
                        frame_width: int, frame_height: int) -> Tuple[List[Line], List[Line]]:
        """Separate lines into left and right lane candidates"""
        left_lines = []
        right_lines = []
        
        split_x = frame_width * self._config.split_ratio
        roi_top_y = int(frame_height * self._config.roi_top_y)
        
        for line in lines:
            # Skip lines above ROI
            if line.start[1] < roi_top_y and line.end[1] < roi_top_y:
                continue
            
            # Skip invalid slopes
            if not self._is_valid_slope(line.slope):
                continue
            
            center_x = (line.start[0] + line.end[0]) / 2.0
            
            # Left lane: negative slope, left side
            # Right lane: positive slope, right side
            if line.slope < 0 and center_x < split_x:
                left_lines.append(line)
            elif line.slope > 0 and center_x > split_x:
                right_lines.append(line)
        
        return left_lines, right_lines
    
    def process(self, edges: np.ndarray, frame_width: int, frame_height: int) -> LaneDetectionResult:
        """
        Detect lanes from edge image
        
        Args:
            edges: Binary edge image from preprocessing
            frame_width: Original frame width
            frame_height: Original frame height
            
        Returns:
            LaneDetectionResult with detected lanes
        """
        result = LaneDetectionResult()
        
        if edges is None or edges.size == 0:
            result.error_msg = "Empty edge image"
            return result
        
        try:
            # Step 1: Detect all lines
            all_lines = self._detect_lines(edges)
            
            # Step 2: Separate into left/right candidates
            left_lines, right_lines = self._separate_lines(
                all_lines, frame_width, frame_height
            )
            
            # Step 3: Average to get final lane lines
            left_lane = self._average_lines(left_lines, frame_height)
            right_lane = self._average_lines(right_lines, frame_height)
            
            result.lanes = LaneLines(
                left=left_lane,
                right=right_lane,
                all_lines=all_lines
            )
            result.success = True
            
        except Exception as e:
            result.error_msg = str(e)
        
        return result
