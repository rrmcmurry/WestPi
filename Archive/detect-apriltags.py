import cv2
import robotpy_apriltag 

def main():
    # Initialize the camera and detector
    cap = cv2.VideoCapture(0)
    detector = robotpy_apriltag.AprilTagDetector()
    detector.addFamily("tag36h11")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = detector.detect(gray)

        if tags:
            for tag in tags:
                print(f"Tag ID: {tag.getId()}, Center: {tag.getCenter()}")


if __name__ == "__main__":
    main()
