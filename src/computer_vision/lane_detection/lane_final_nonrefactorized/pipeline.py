"""
Lane Detection Pipeline

Modular pipeline combining: Preprocessing -> Lane Detection -> Postprocessing
"""

import cv2
import numpy as np
import time
import threading
from dataclasses import dataclass, field
from typing import Optional, List

from preprocessing import Preprocessing, PreprocessingConfig, PreprocessingResult
from lane_detection import LaneDetection, LaneDetectionConfig, LaneDetectionResult, LaneLines, Line
from postprocessing import Postprocessing, PostprocessingConfig, PostprocessingResult, SteeringOutput


@dataclass
class PipelineConfig:
    """Master configuration for the entire pipeline"""
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    detection: LaneDetectionConfig = field(default_factory=LaneDetectionConfig)
    postprocessing: PostprocessingConfig = field(default_factory=PostprocessingConfig)
    debug_mode: bool = False


@dataclass
class PipelineResult:
    """Complete result from pipeline processing"""
    frame_id: int = 0
    timestamp_ms: int = 0
    
    # Stage results
    preprocessing: PreprocessingResult = field(default_factory=PreprocessingResult)
    detection: LaneDetectionResult = field(default_factory=LaneDetectionResult)
    postprocessing: PostprocessingResult = field(default_factory=PostprocessingResult)
    
    # Convenience accessors
    @property
    def lanes(self) -> LaneLines:
        return self.detection.lanes
    
    @property
    def steering(self) -> SteeringOutput:
        return self.postprocessing.steering
    
    # Debug visualization
    debug_frame: Optional[np.ndarray] = None
    
    # Overall status
    success: bool = False
    error_msg: str = ""


class Pipeline:
    """
    Modular Lane Detection Pipeline
    
    Stages:
        1. Preprocessing: Gamma -> Canny -> ROI Mask
        2. Detection: Hough -> Line Filtering -> Averaging
        3. Postprocessing: Lane Center -> P Regulator -> Steering
    
    Each stage can be used independently or as part of the full pipeline.
    """
    
    def __init__(self, config: PipelineConfig = None):
        self._config = config or PipelineConfig()
        self._config_lock = threading.Lock()
        
        # Initialize stages
        self._preprocessing = Preprocessing(self._config.preprocessing)
        self._detection = LaneDetection(self._config.detection)
        self._postprocessing = Postprocessing(self._config.postprocessing)
        
        self._debug_mode = self._config.debug_mode
    
    # ========================================================================
    # Configuration
    # ========================================================================
    
    def configure(self, config: PipelineConfig) -> None:
        """Thread-safe configuration update"""
        with self._config_lock:
            self._config = config
            self._preprocessing.configure(config.preprocessing)
            self._detection.configure(config.detection)
            self._postprocessing.configure(config.postprocessing)
            self._debug_mode = config.debug_mode
    
    def get_config(self) -> PipelineConfig:
        """Get current configuration"""
        with self._config_lock:
            return PipelineConfig(
                preprocessing=self._preprocessing.config,
                detection=self._detection.config,
                postprocessing=self._postprocessing.config,
                debug_mode=self._debug_mode
            )
    
    def set_debug_mode(self, enabled: bool) -> None:
        """Enable/disable debug visualization"""
        self._debug_mode = enabled
    
    @property
    def debug_mode(self) -> bool:
        return self._debug_mode
    
    # ========================================================================
    # Stage Access (for independent use)
    # ========================================================================
    
    @property
    def preprocessing(self) -> Preprocessing:
        """Access preprocessing stage directly"""
        return self._preprocessing
    
    @property
    def detection(self) -> LaneDetection:
        """Access detection stage directly"""
        return self._detection
    
    @property
    def postprocessing(self) -> Postprocessing:
        """Access postprocessing stage directly"""
        return self._postprocessing
    
    # ========================================================================
    # Processing
    # ========================================================================
    
    def process(self, frame: np.ndarray, frame_id: int = 0) -> PipelineResult:
        """
        Process frame through all pipeline stages
        
        Args:
            frame: Input BGR frame
            frame_id: Optional frame identifier
            
        Returns:
            PipelineResult with all stage outputs
        """
        result = PipelineResult()
        result.frame_id = frame_id
        result.timestamp_ms = int(time.time() * 1000)
        
        if frame is None or frame.size == 0:
            result.error_msg = "Empty input frame"
            return result
        
        height, width = frame.shape[:2]
        
        try:
            # Stage 1: Preprocessing
            result.preprocessing = self._preprocessing.process(frame)
            if not result.preprocessing.success:
                result.error_msg = f"Preprocessing failed: {result.preprocessing.error_msg}"
                return result
            
            # Stage 2: Lane Detection
            result.detection = self._detection.process(
                result.preprocessing.edges, width, height
            )
            if not result.detection.success:
                result.error_msg = f"Detection failed: {result.detection.error_msg}"
                return result
            
            # Stage 3: Postprocessing
            result.postprocessing = self._postprocessing.process(
                result.detection.lanes, width, height
            )
            
            # Debug visualization
            if self._debug_mode:
                result.debug_frame = self._create_debug_frame(frame, result)
            
            result.success = True
            
        except Exception as e:
            result.error_msg = str(e)
        
        return result
    
    def process_preprocessing(self, frame: np.ndarray) -> PreprocessingResult:
        """Run only preprocessing stage"""
        return self._preprocessing.process(frame)
    
    def process_detection(self, edges: np.ndarray, 
                          frame_width: int, frame_height: int) -> LaneDetectionResult:
        """Run only detection stage"""
        return self._detection.process(edges, frame_width, frame_height)
    
    def process_postprocessing(self, lanes: LaneLines,
                               frame_width: int, frame_height: int) -> PostprocessingResult:
        """Run only postprocessing stage"""
        return self._postprocessing.process(lanes, frame_width, frame_height)
    
    # ========================================================================
    # Debug Visualization
    # ========================================================================
    
    def _create_debug_frame(self, original: np.ndarray, 
                            result: PipelineResult) -> np.ndarray:
        """Create debug visualization frame"""
        debug = original.copy()
        height, width = original.shape[:2]
        
        # Draw ROI trapezoid (cyan)
        if result.preprocessing.roi_points is not None:
            cv2.polylines(debug, [result.preprocessing.roi_points], 
                         isClosed=True, color=(255, 255, 0), thickness=2)
        
        # Draw all detected lines (gray, thin)
        for line in result.detection.lanes.all_lines:
            pt1 = (int(line.start[0]), int(line.start[1]))
            pt2 = (int(line.end[0]), int(line.end[1]))
            cv2.line(debug, pt1, pt2, (128, 128, 128), 1)
        
        # Draw left lane (red, thick)
        if result.lanes.left is not None:
            pt1 = (int(result.lanes.left.start[0]), int(result.lanes.left.start[1]))
            pt2 = (int(result.lanes.left.end[0]), int(result.lanes.left.end[1]))
            cv2.line(debug, pt1, pt2, (0, 0, 255), 3, cv2.LINE_AA)
        
        # Draw right lane (blue, thick)
        if result.lanes.right is not None:
            pt1 = (int(result.lanes.right.start[0]), int(result.lanes.right.start[1]))
            pt2 = (int(result.lanes.right.end[0]), int(result.lanes.right.end[1]))
            cv2.line(debug, pt1, pt2, (255, 0, 0), 3, cv2.LINE_AA)
        
        # Draw steering info
        if result.steering.valid:
            center_x = int(result.steering.lane_center * width)
            target_x = int(self._postprocessing.config.target_center * width)
            
            # Lane center marker (green circle)
            cv2.circle(debug, (center_x, height - 30), 10, (0, 255, 0), -1)
            
            # Target marker (magenta line)
            cv2.line(debug, (target_x, height - 50), (target_x, height - 10),
                     (255, 0, 255), 2)
            
            # Steering arrow (yellow)
            arrow_len = int(result.steering.steering * 100)
            cv2.arrowedLine(debug, (width // 2, 50),
                           (width // 2 + arrow_len, 50),
                           (0, 255, 255), 3)
            
            # Text overlay
            info = f"Steering: {result.steering.steering:+.2f}  Error: {result.steering.error:+.3f}"
            cv2.putText(debug, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (255, 255, 255), 2)
        
        return debug
