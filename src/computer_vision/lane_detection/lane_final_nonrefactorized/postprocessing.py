"""
Postprocessing Module

Handles steering calculation from detected lanes using P regulator.
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional

from lane_detection import LaneLines, Line


@dataclass
class PostprocessingConfig:
    """Configuration for postprocessing stage"""
    kp: float = 0.5                   # Proportional gain
    target_center: float = 0.5        # Target lane position (0.5 = center)
    max_output: float = 1.0           # Maximum steering output
    deadzone: float = 0.02            # Deadzone around target
    
    # Lane width estimation (ratio of frame width)
    estimated_lane_width: float = 0.35


@dataclass 
class SteeringOutput:
    """Steering calculation result"""
    steering: float = 0.0             # -1.0 (left) to +1.0 (right)
    error: float = 0.0                # Raw error value
    lane_center: float = 0.5          # Detected lane center (0-1)
    valid: bool = False


@dataclass
class PostprocessingResult:
    """Output from postprocessing stage"""
    steering: SteeringOutput = None
    success: bool = False
    error_msg: str = ""
    
    def __post_init__(self):
        if self.steering is None:
            self.steering = SteeringOutput()


class Postprocessing:
    """
    Postprocessing stage for lane detection
    
    Pipeline: Lane Lines -> Calculate Center -> P Regulator -> Steering Output
    """
    
    def __init__(self, config: PostprocessingConfig = None):
        self._config = config or PostprocessingConfig()
    
    def configure(self, config: PostprocessingConfig) -> None:
        """Update configuration"""
        self._config = config
    
    @property
    def config(self) -> PostprocessingConfig:
        """Get current configuration"""
        return self._config
    
    def _calculate_lane_center(self, lanes: LaneLines, 
                                frame_width: int, frame_height: int) -> float:
        """
        Calculate normalized lane center position
        
        Returns:
            Lane center as ratio (0 = left edge, 1 = right edge)
        """
        y_eval = float(frame_height)  # Evaluate at bottom of frame
        
        left_x = 0.0
        right_x = float(frame_width)
        
        # Calculate x position of each lane at bottom
        if lanes.left is not None:
            if abs(lanes.left.slope) > 1e-6 and lanes.left.slope != float('inf'):
                left_x = (y_eval - lanes.left.intercept) / lanes.left.slope
        
        if lanes.right is not None:
            if abs(lanes.right.slope) > 1e-6 and lanes.right.slope != float('inf'):
                right_x = (y_eval - lanes.right.intercept) / lanes.right.slope
        
        # Estimate missing lane from the other
        estimated_width = frame_width * self._config.estimated_lane_width
        
        if lanes.left is None and lanes.right is not None:
            left_x = right_x - estimated_width
        elif lanes.left is not None and lanes.right is None:
            right_x = left_x + estimated_width
        
        # Calculate normalized center
        lane_center_x = (left_x + right_x) / 2.0
        return lane_center_x / frame_width
    
    def _apply_p_control(self, lane_center: float) -> SteeringOutput:
        """Apply P controller to calculate steering"""
        output = SteeringOutput()
        output.lane_center = lane_center
        output.valid = True
        
        # Calculate error (positive = car is right of center)
        output.error = lane_center - self._config.target_center
        
        # Apply deadzone
        if abs(output.error) < self._config.deadzone:
            output.steering = 0.0
            return output
        
        # P control: negative error -> steer left, positive -> steer right
        output.steering = -self._config.kp * output.error
        
        # Clamp output
        output.steering = max(-self._config.max_output,
                              min(self._config.max_output, output.steering))
        
        return output
    
    def process(self, lanes: LaneLines, 
                frame_width: int, frame_height: int) -> PostprocessingResult:
        """
        Calculate steering from detected lanes
        
        Args:
            lanes: Detected lane lines
            frame_width: Frame width for normalization
            frame_height: Frame height for calculation
            
        Returns:
            PostprocessingResult with steering output
        """
        result = PostprocessingResult()
        
        if not lanes.valid():
            result.steering.valid = False
            result.error_msg = "No valid lanes detected"
            return result
        
        try:
            # Step 1: Calculate lane center
            lane_center = self._calculate_lane_center(
                lanes, frame_width, frame_height
            )
            
            # Step 2: Apply P controller
            result.steering = self._apply_p_control(lane_center)
            result.success = True
            
        except Exception as e:
            result.error_msg = str(e)
        
        return result
    
    def process_from_center(self, lane_center: float) -> PostprocessingResult:
        """
        Calculate steering from explicit lane center value
        
        Args:
            lane_center: Normalized lane center (0-1)
            
        Returns:
            PostprocessingResult with steering output
        """
        result = PostprocessingResult()
        
        try:
            result.steering = self._apply_p_control(lane_center)
            result.success = True
        except Exception as e:
            result.error_msg = str(e)
        
        return result
