from dataclasses import dataclass

@dataclass(frozen=True)
class YOLOModel:
    model_path: str = "/home/konstantin/Desktop/sign_detection_refactorized/models/yolov8n.pt"
    conf_threshold: float = 0.4

@dataclass(frozen=True)
class SignClasses:
    names = [
        "parking",
        "stop",
        "priority_road",
        "highway",
        "end_highway",
        "one_way_street",
        "crosswalk",
        "pedestrian_walking",
        "pedestrian",
        "roundabout",
    ]

class SignConfig:
    def __init__(self):
        self.Model = YOLOModel()
        self.Classes = SignClasses()
