import numpy as np
import cv2

class PreprocessingFrame():
    
    def __init__(self, config):
        self.gamma = config.Gamma.gamma      # Value of parameter gamma
        self._lut = config.Gamma.lut        # Look up table for gamma transform
    
    def apply_gamma(self, frame: np.ndarray) -> np.ndarray:
        """Apply gamma correction using lookup table"""
        if self._lut is None:
            inv_gamma = 1.0 / self.gamma
            self._lut = np.array([
                np.clip(pow(i / 255.0, inv_gamma) * 255.0, 0, 255)
                for i in range(256)
            ]).astype(np.uint8)
        return cv2.LUT(frame, self._lut)

    