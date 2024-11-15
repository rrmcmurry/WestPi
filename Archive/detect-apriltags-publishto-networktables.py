import cv2
import robotpy_apriltag
import ntcore
import time
# import logging

testlab = True
teamnumber = 9668
camera_width = 320
camera_height = 240


# logging.basicConfig(level=logging.DEBUG)

# Function to detect AprilTags in a frame
def detect_april_tags(frame, detector):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray)         
    return tags


# Function to publish detected tags to NetworkTables
def publish_tags_to_networktables(tags, vision_nt):
    count = 0
    for tag in tags:
        count += 1
        tag_id = tag.getId()
        if tag_id > 16:  # Only report if tag id is 0-16
            continue
        centerPoint = tag.getCenter()
        x = (centerPoint.x - (camera_width / 2)) / camera_width
        y = (centerPoint.y - (camera_height / 2)) / camera_height
        # print(f"Tag ID: {tag_id}, Center: ({centerPoint.x}, {centerPoint.y})")
        # Publish tag ID and position to NetworkTables
        vision_nt.putNumber(f"Tag_{tag_id}_X", x)
        vision_nt.putNumber(f"Tag_{tag_id}_Y", y)

    vision_nt.putNumber("Tags_detected",count)
    
    if (count == 0):
        vision_nt.putNumber(f"Tag_1_X", 0)
        vision_nt.putNumber(f"Tag_1_Y", 0)


# Function to check the game state and decide what to do next
def game_logic(frame, detector, vision_nt):
    # Future development: 
    #   Need to define game objectives and logic sequence here
    # Example:
    # If NoteLoaded & TargetLocked
    #   Fire on target
    # Else if NoteLoaded
    #   Lock on target
    # Else if NoteFound
    #   Load note
    # Else 
    #   Find note
    
    # First game is simple - lock on target and stay at certain distance 
    # If TargetLocked
    #   OptimizeDistance
    # Else if TargetLocated
    #   ObtainTargetLock
    # Else
    #   LocateTarget
    
    
    # For simplicity, I'm starting with just detecting AprilTags
    tags = detect_april_tags(frame, detector)

    # And publishing the detected tags on networktables
    publish_tags_to_networktables(tags, vision_nt)


def main():
    print("Initializing Camera")
    # Initialize the camera 
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)
    
    print("Initializing AprilTag detector")
    # Initialize AprilTag Detector
    detector = robotpy_apriltag.AprilTagDetector()
    detector.addFamily("tag36h11")

    print("Starting NetworkTables")
    # Start NetworkTables and get an instance
    
    ntinst = ntcore.NetworkTableInstance.getDefault() 

    if testlab:
        ntinst.startServer()
    else: 
        ntinst.startClient4("10.96.68.2")
        
    ntinst.setServerTeam(teamnumber) 
    vision_nt = ntinst.getTable("Vision")  # Create/Access "Vision" table

    
    print("Entering game logic")
    while True:
        # Grab frame 
        _, frame = cap.read()

        # Run game logic 
        game_logic(frame, detector, vision_nt)
        
        time.sleep(0.1)


if __name__ == "__main__":
    main()



