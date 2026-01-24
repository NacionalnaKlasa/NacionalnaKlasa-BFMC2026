"""
Preprocessing Module

Handles image preprocessing: Gamma correction, edge detection, and ROI masking.
"""

import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class PreprocessingConfig:
    """Configuration for preprocessing stage"""
    # Gamma correction
    gamma: float = 1.5
    
    # Canny edge detection
    blur_kernel: int = 5
    canny_low: float = 50
    canny_high: float = 150
    
    # ROI trapezoid corners (x_ratio, y_ratio)
    roi_bottom_left: Tuple[float, float] = (0.5, 0.75)
    roi_bottom_right: Tuple[float, float] = (1.0, 0.75)
    roi_top_right: Tuple[float, float] = (0.6, 0.6)
    roi_top_left: Tuple[float, float] = (0.4, 0.6)


@dataclass
class PreprocessingResult:
    """Output from preprocessing stage"""
    edges: np.ndarray = None           # Masked edge image
    roi_mask: np.ndarray = None        # ROI mask for visualization
    roi_points: np.ndarray = None      # ROI trapezoid points
    gamma_frame: np.ndarray = None     # Gamma corrected frame (for debug)
    success: bool = False
    error_msg: str = ""


class Preprocessing:
    """
    Preprocessing stage for lane detection
    
    Pipeline: Frame -> Gamma -> Canny -> ROI Mask -> Edges
    """
    
    def __init__(self, config: PreprocessingConfig = None):
        self._config = config or PreprocessingConfig()
        self._lut = None
        self._build_gamma_lut()
    
    def configure(self, config: PreprocessingConfig) -> None:
        """Update configuration"""
        self._config = config
        self._build_gamma_lut()
    
    @property
    def config(self) -> PreprocessingConfig:
        """Get current configuration"""
        return self._config
    
    def _build_gamma_lut(self) -> None:
        """Build lookup table for fast gamma correction"""
        inv_gamma = 1.0 / self._config.gamma
        self._lut = np.array([
            np.clip(pow(i / 255.0, inv_gamma) * 255.0, 0, 255)
            for i in range(256)
        ]).astype(np.uint8)
    
    def _apply_gamma(self, frame: np.ndarray) -> np.ndarray:
        """Apply gamma correction using LUT"""
        return cv2.LUT(frame, self._lut)
    
    def _apply_canny(self, frame: np.ndarray) -> np.ndarray:
        """Apply Gaussian blur + Canny edge detection"""
        # Convert to grayscale
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        
        # Gaussian blur
        kernel = self._config.blur_kernel
        if kernel % 2 == 0:
            kernel += 1
        blurred = cv2.GaussianBlur(gray, (kernel, kernel), 0)
        
        # Canny edge detection
        edges = cv2.Canny(blurred, self._config.canny_low, self._config.canny_high)
        return edges
    
    def get_roi_mask(self, width: int, height: int) -> np.ndarray:
        """Generate ROI mask from trapezoid config"""
        mask = np.zeros((height, width), dtype=np.uint8)
        points = self.get_roi_points(width, height)
        cv2.fillConvexPoly(mask, points, 255)
        return mask
    
    def get_roi_points(self, width: int, height: int) -> np.ndarray:
        """Get ROI trapezoid corner points in pixel coordinates"""
        cfg = self._config
        return np.array([
            [int(cfg.roi_bottom_left[0] * width), int(cfg.roi_bottom_left[1] * height)],
            [int(cfg.roi_bottom_right[0] * width), int(cfg.roi_bottom_right[1] * height)],
            [int(cfg.roi_top_right[0] * width), int(cfg.roi_top_right[1] * height)],
            [int(cfg.roi_top_left[0] * width), int(cfg.roi_top_left[1] * height)]
        ], dtype=np.int32)
    
    def process(self, frame: np.ndarray) -> PreprocessingResult:
        """
        Process frame through preprocessing pipeline
        
        Args:
            frame: Input BGR frame
            
        Returns:
            PreprocessingResult with edges and ROI info
        """
        result = PreprocessingResult()
        
        if frame is None or frame.size == 0:
            result.error_msg = "Empty input frame"
            return result
        
        try:
            height, width = frame.shape[:2]
            
            # Step 1: Gamma correction
            gamma_frame = self._apply_gamma(frame)
            result.gamma_frame = gamma_frame
            
            # Step 2: Canny edge detection
            edges = self._apply_canny(gamma_frame)
            
            # Step 3: Apply ROI mask
            roi_mask = self.get_roi_mask(width, height)
            masked_edges = cv2.bitwise_and(edges, roi_mask)
            
            result.edges = masked_edges
            result.roi_mask = roi_mask
            result.roi_points = self.get_roi_points(width, height)
            result.success = True
            
        except Exception as e:
            result.error_msg = str(e)
        
        return result
