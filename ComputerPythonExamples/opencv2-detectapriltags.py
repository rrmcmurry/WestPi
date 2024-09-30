import cv2
import robotpy_apriltag 
import numpy as np
import ntcore

teamnumber = 9668

# Initialize the AprilTag detector
detector = robotpy_apriltag.AprilTagDetector()
detector.addFamily("tag36h11")


# Open the camera
cap = cv2.VideoCapture(0)

# Set the capture width and height
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Initialize some variables
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
pointerx = int(width / 2)
pointery = int(height / 2)

# Start NetworkTables and get an instance
ntinst = ntcore.NetworkTableInstance.getDefault()
ntinst.startServer()
ntinst.setServerTeam(teamnumber) 
vision_nt = ntinst.getTable("Vision")  # Create/Access "Vision" table


print(f"Width: {width}, Height: {height}")

while True:
    # Capture a frame 
    _, frame = cap.read()

    # Convert the frame to grayscale for the AprilTagDetector
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect AprilTags in the frame
    results = detector.detect(gray)

    # Draw stuff on the frame based on detected AprilTags
    for result in results:
        # Draw a green polyline around the AprilTag
        points = []
        for i in range(4):
            corner = (int(result.getCorner(i).x),int(result.getCorner(i).y))
            points.append(corner)
        points = np.array(points, dtype=np.int32).reshape((-1,1,2))
        cv2.polylines(frame, [points], True, (0, 255, 0), 2)

        # Draw a red dot at the center of the AprilTag
        apriltagcenterx = int(result.getCenter().x)
        apriltagcentery = int(result.getCenter().y)  
        apriltagcenterpoint = (apriltagcenterx, apriltagcentery)
        cv2.circle(frame, apriltagcenterpoint, 5, (0, 0, 255), -1)

        # Write the Tag ID above the center
        tagid = result.getId()
        cv2.putText(frame, f"ID: {tagid}", (apriltagcenterx - 10,apriltagcentery - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Write the distance from center on the tag
        distancex = pointerx - apriltagcenterx
        distancey = pointery - apriltagcentery 
        cv2.putText(frame, f"Target: ({distancex},{distancey})", (apriltagcenterx - 10,apriltagcentery + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Estimate the distance from the camera
        apriltagupperleft = result.getCorner(0).x
        apriltagupperright = result.getCorner(1).x
        pixels = apriltagupperright - apriltagupperleft
        depth = 4.3003 * 0.9966 ** pixels 
        cv2.putText(frame, f"Distance: {depth}", (apriltagcenterx - 10, apriltagcentery + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Are we close enough?
        if abs(distancex) < 5 & abs(distancey) < 5:
            print("Target acquired")

    # Draw a red dot on the center of the screen
    cv2.circle(frame, (pointerx, pointery), 5, (0, 0, 255), 1)

    # Display the frame
    cv2.imshow('AprilTag Detection', frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()
