from ultralytics import YOLO

class SignDetectionFrame:
    def __init__(self, config):
        self.model = YOLO(config.Model.model_path)
        self.conf_threshold = config.Model.conf_threshold

    def detect(self, frame):
        """
        Returns raw detections:
        [
            {
              class_id,
              confidence,
              bbox [x1,y1,x2,y2]
            }
        ]
        """
        results = self.model(frame, conf=self.conf_threshold, verbose=False)

        detections = []
        for r in results:
            for box in r.boxes:
                detections.append({
                    "class_id": int(box.cls[0]),
                    "confidence": float(box.conf[0]),
                    "bbox": box.xyxy[0].tolist()
                })

        return detections
