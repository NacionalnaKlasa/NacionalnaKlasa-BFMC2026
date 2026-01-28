import cv2

from config import SignClasses

class SignPostprocessingFrame:
    def __init__(self, config):
        self.class_names = SignClasses.names

    def draw(self, frame, detections):
        for det in detections:
            x1, y1, x2, y2 = map(int, det["bbox"])
            cls_id = det["class_id"]
            conf = det["confidence"]

            # fallback ako cls_id nije validan
            if 0 <= cls_id < len(self.class_names):
                label = f"{self.class_names[cls_id]} {conf:.2f}"
            else:
                label = f"unknown {conf:.2f}"

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
            print(label)

        return frame
