"""
Lane Detection Component for Raspberry Pi 5

Simple, modular lane detection:
    - Preprocessing: Gamma -> Canny -> ROI Mask
    - Lane Detection: Hough -> Filter -> Average
    - Postprocessing: Lane Center -> P Regulator -> Steering
"""

# Preprocessing stage
from .preprocessing import (
    Preprocessing,
    PreprocessingConfig,
    PreprocessingResult,
)

# Lane detection stage
from .lane_detection import (
    LaneDetection,
    LaneDetectionConfig,
    LaneDetectionResult,
    Line,
    LaneLines,
)

# Postprocessing stage
from .postprocessing import (
    Postprocessing,
    PostprocessingConfig,
    PostprocessingResult,
    SteeringOutput,
)

# Complete pipeline
from .pipeline import (
    Pipeline,
    PipelineConfig,
    PipelineResult,
)

__version__ = "2.0.0"

__all__ = [
    # Preprocessing
    "Preprocessing",
    "PreprocessingConfig",
    "PreprocessingResult",
    # Lane Detection
    "LaneDetection",
    "LaneDetectionConfig",
    "LaneDetectionResult",
    "Line",
    "LaneLines",
    # Postprocessing
    "Postprocessing",
    "PostprocessingConfig",
    "PostprocessingResult",
    "SteeringOutput",
    # Pipeline
    "Pipeline",
    "PipelineConfig",
    "PipelineResult",
]
