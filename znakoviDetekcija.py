# from ultralytics import YOLO
# import cv2
# import math

# # 1. Učitaj YOLO model
# model = YOLO("yolov8n.pt")  # ili specifičan model za saobraćajne znakove

# # 2. Otvori ulazni video
# cap = cv2.VideoCapture("input.mp4")

# # 3. Pripremi izlazni video
# fourcc = cv2.VideoWriter_fourcc(*"mp4v")
# out = cv2.VideoWriter("output1.mp4", fourcc, 30.0,
#                       (int(cap.get(3)), int(cap.get(4))))

# # 4. Lista klasa koje želimo da označimo (primjer)
# traffic_sign_classes = ["stop", "traffic light", "fire hydrant"] 
# # Ako koristiš specijalni model → koristi njegove klase

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # YOLO predikcija po frejmu
#     results = model(frame, stream=True)

#     for result in results:
#         boxes = result.boxes

#         for box in boxes:
#             cls_id = int(box.cls[0])
#             cls_name = model.names[cls_id]

#             # Ako nas zanima samo određeni znak
#             if cls_name not in traffic_sign_classes:
#                 continue

#             # Koordinate detekcije
#             x1, y1, x2, y2 = map(int, box.xyxy[0])

#             # Izračunaj centar i poluprečnik za crtanje kruga
#             cx = (x1 + x2) // 2
#             cy = (y1 + y2) // 2
#             radius = int(max((x2 - x1), (y2 - y1)) / 2)

#             # Crtaj krug oko objekta
#             cv2.circle(frame, (cx, cy), radius, (0, 0, 255), 3)

#             # Prikaži naziv klase
#             cv2.putText(frame, cls_name, (x1, y1 - 10),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

#     # Upis u izlazni video
#     out.write(frame)

# # Zatvori fajlove
# cap.release()
# out.release()
# cv2.destroyAllWindows()

from ultralytics import YOLO
import cv2

# 1. Učitaj YOLO model za saobraćajne znakove
model = YOLO("bestDetectTrafficSign.pt")

# 2. Učitaj ulazni video
cap = cv2.VideoCapture("input.mp4")

# 3. Spremaj izlazni video
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter("output1.mp4", fourcc, 30.0,
                      (int(cap.get(3)), int(cap.get(4))))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO detekcija
    results = model(frame, stream=True)

    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            radius = int(max((x2 - x1), (y2 - y1)) / 2)

            cv2.circle(frame, (cx, cy), radius, (0, 0, 255), 3)
            cv2.putText(frame, cls_name, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    out.write(frame)

cap.release()
out.release()
cv2.destroyAllWindows()
