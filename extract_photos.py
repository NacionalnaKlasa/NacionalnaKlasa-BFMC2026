import cv2
import os
from tqdm import tqdm
import random
import shutil

# =========================
# CONFIG
# =========================
VIDEOS = [
    r"C:\Users\Korisnik\Desktop\BOSCH\CODE\Floyd\videos\novi_video.mp4"
]

OUTPUT_DIR = "dataset"
FPS_EXTRACT = 1          # frames per second to extract
VAL_SPLIT = 0.2          # 20% validation
IMAGE_FORMAT = ".jpg"

# =========================
# CREATE YOLO STRUCTURE
# =========================
img_train = os.path.join(OUTPUT_DIR, "images/train")
img_val = os.path.join(OUTPUT_DIR, "images/val")
lbl_train = os.path.join(OUTPUT_DIR, "labels/train")
lbl_val = os.path.join(OUTPUT_DIR, "labels/val")

for d in [img_train, img_val, lbl_train, lbl_val]:
    os.makedirs(d, exist_ok=True)

# =========================
# FRAME EXTRACTION
# =========================
all_images = []

for video_path in VIDEOS:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Cannot open {video_path}")
        continue

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(round(fps / FPS_EXTRACT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_id = 0
    saved_id = 0

    print(f"📹 Processing {video_path} ({fps:.2f} FPS)")

    for _ in tqdm(range(total_frames)):
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % frame_interval == 0:
            filename = f"{os.path.splitext(os.path.basename(video_path))[0]}_{saved_id:06d}{IMAGE_FORMAT}"
            path = os.path.join(img_train, filename)
            cv2.imwrite(path, frame)
            all_images.append(filename)
            saved_id += 1

        frame_id += 1

    cap.release()

print(f"✅ Extracted {len(all_images)} images")

# =========================
# TRAIN / VAL SPLIT
# =========================
random.shuffle(all_images)
val_count = int(len(all_images) * VAL_SPLIT)

val_images = all_images[:val_count]
train_images = all_images[val_count:]

for img in val_images:
    shutil.move(
        os.path.join(img_train, img),
        os.path.join(img_val, img)
    )

print(f"📊 Train images: {len(train_images)}")
print(f"📊 Val images: {len(val_images)}")

print("🎯 Dataset ready for labeling & YOLOv8 training")
