# 🛑 Traffic Sign Detection Module

Documentation of the training and evaluation process of the YOLOv8 model for BFMC 2025.

## 📊 Model Specifications
- **Architecture:** YOLOv8 Nano (`yolov8n`)
- **Input Resolution:** 256x256 px
- **Classes:** 13 (BFMC Standard)
- **Performance (Val):** mAP@50: **0.99** | mAP@50-95: **0.59**
- **Inference Hardware:** Raspberry Pi 5 (CPU/NPU)

## 🗂️ Directory Structure
- `config/`: YAML Configuration of classes and paths (Data lineage).
- `notebooks/`: Jupyter notebooks for training reproduction (Google Colab).
- `weights/`: Archive of trained models (`.pt`).
- `analysis/`: Performance graphs and Confusion Matrix. *- In progress*
- `tests/`: Demo recordings (GIF/MP4) for model verification.
## 🔄 Reproducibility
1. V1 dataset is hosted on **Roboflow Universe**: *https://app.roboflow.com/konstantin-arfm1/nacionalnaklasa-bfmc2026/1*
2. Use `notebooks/training.ipynb` to run the training.
3. For deployment on the vehicle, use `Brain/src/models/best_v1.pt`.
## 🧪 Experiments
See [EXPERIMENTS.md](./EXPERIMENTS.md) for a detailed changelog and engineering decisions made during development.