# 🛣️ Lane Detection & Lateral Control

Algorithms for lane detection and calculation of steering error.

## ⚙️ Methodology
- **Approach:** Bird's Eye View (Perspective Transform) + Sliding Window / Histogram.
- **Output:** Lateral Error (distance from lane center) & Heading Error (angle).
## 📐 Calibration
Camera calibration matrix is located in `calibration/camera_matrix.npz`.
Re-calibration is necessary if the camera angle or height changes.

## 📂 Contents
- `experiments/`: Test scripts for image processing (Thresholding, Canny edge).
- `test_videos/`: Raw recordings from the track for offline testing.