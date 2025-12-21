# Lane Detection Project

This project implements lane detection on road videos using computer vision techniques like edge detection, Hough Transform, and ROI (Region of Interest) masking. There are two main detection options:

1. **Basic Lane Detection**
2. **Strong Averaged Lane Lines** - uses averaged lines for stronger lane detection.

## Getting Started

These instructions will help you set up the project on your local machine using a virtual environment.

### Pre-requisites

To run this project, you need:

- Python 3.x (installed on your system)
- A terminal with Bash support (e.g., Git Bash on Windows)


## Project Structure:

    main.py – Launcher script that allows choosing between the two detection modes.
    bestLineDetection.py – Basic lane detection (displays all detected lines and average slopes for left/right lanes).
    straightAvgLinesDetection.py – Improved version with stronger averaging of lane lines (draws only one thick averaged line per side).


## Common Features in Both Modes:

    1. Custom Region of Interest (ROI) trapezoid tailored to the BFMC car's camera perspective.
    2. Contrast enhancement using CLAHE.
    3. Gaussian blur and Canny edge detection.
    4. Probabilistic Hough Transform (HoughLinesP) for line detection.
    5. Special detection of horizontal white lines (e.g., start/finish) – drawn in thick blue.
    6. ROI visualization in a separate window (magenta outline).
    7. Display of average lane slopes in degrees at the bottom of the frame.
    8. Saving the processed video to an output file.
