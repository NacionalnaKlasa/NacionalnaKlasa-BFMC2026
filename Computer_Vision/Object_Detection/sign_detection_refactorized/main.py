from processingFrame import SignDetectionFrame
from postprocessingFrame import SignPostprocessingFrame
from config import SignConfig

import cv2

def main():
    config = SignConfig()
    sign_processing = SignDetectionFrame(config)
    sign_postprocessing = SignPostprocessingFrame(config)
    video_path = "/home/konstantin/Documents/ntp_staza_znakovi/output_video1769267615.585304.avi"
    video = cv2.VideoCapture(video_path)
    
    if not video.isOpened():
        print("Ne mogu da otvorim video")
        return

    cv2.namedWindow("Signs", cv2.WINDOW_NORMAL)

    while True:
        ret, frame = video.read()
        if not ret:
            break

        detection = sign_processing.detect(frame)
        frame = sign_postprocessing.draw(frame, detection)
        
        cv2.imshow("Signs", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()

if __name__== "__main__":
    main()