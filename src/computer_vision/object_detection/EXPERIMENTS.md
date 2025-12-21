# 🧪 Experiments Log - Traffic Sign Detection

**Owner:** Konstantin
**Goal:** Develop a robust traffic sign detection model for BFMC 2026 capable of running on RPi5.

## 📊 Summary Table

| ID | Date | Model | Dataset Size | ImgSz | Epochs | mAP@50 | mAP@50-95 | Key Configuration / Changes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP-001** | 16.12.2025. | YOLOv8n | ~1,800 | 512 | 50 | 0.72 | 0.45 | Baseline training on public Roboflow data only. No augmentations. |
| **EXP-002** | 17.12.2025. | YOLOv8n | **15,256** | **256** | 50 | **0.99** | **0.59** | Added custom dataset + aggressive augmentation. Reduced img size to 256 for speed. **Current Production Candidate.** |

---

## 📝 Detailed Analysis

### 🟢 EXP-002: Production Candidate *-in progress...-*
**Date:** 18.12.2025.
**Status:** In progress...

**Context:**
We significantly increased the dataset size by merging public BFMC datasets with our own lab recordings. Changed input resolution to `256x256` to match the target inference resolution on Raspberry Pi.

**Observations:**
1.  **Convergence:** in progress...
2.  **Class Separation:** in progress...
3.  **Small Objects:** in progress...

**Next Steps:**
- in progress...

---

### 🔴 EXP-001: Baseline (Archived)
**Date:** 16.12.2025.
**Status:** ❌ RETIRED

**Issues:**
- High False Positive rate for "Crosswalk, Stop, Highway" signs, pedestrian and car.
- **Reason:** Insufficient dataset diversity.