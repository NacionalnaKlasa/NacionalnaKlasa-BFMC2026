from ultralytics.models import YOLO

# Load a model
model = YOLO("yolov8n.pt")

# Train the model
results = model.train(
    data="data.yaml",
    epochs=100,
    imgsz=640
)