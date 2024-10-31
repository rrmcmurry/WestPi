import cv2
import robotpy_apriltag
from cscore import CameraServer
import ntcore
import time
import numpy 

# Test lab is true if I'm bench testing, false if connected to the robot
testlab = False
teamnumber = 9668
camera_width = 960
camera_height = 640


# Boolean function returns whether target was located
def locate_target(tags, targetid):
    targetlocated = False
    for tag in tags:
        tag_id = tag.getId()
        if tag_id == targetid:
            targetlocated = True 
    return targetlocated

# Returns the target tag object from a set of tags
def get_target(tags, targetid):
    targettag = []
    for tag in tags:
        tag_id = tag.getId()
        if tag_id == targetid:
            targettag = tag
    return targettag

# Set of functions to publish robot controls     
def stop(vision_nt):
    vision_nt.putNumber("X_Axis", 0.00)
    vision_nt.putNumber("Y_Axis", 0.00)
    vision_nt.putNumber("Z_Axis", 0.00)


# Function to orient to target 
def orient_to_target(tag, vision_nt):
    # target is not locked by default
    targetlocked = False
    
    # Grab points from the tag
    UpperLeftPoint = tag.getCorner(0)
    UpperRightPoint = tag.getCorner(1)
    LowerRightPoint = tag.getCorner(2)
    LowerLeftPoint = tag.getCorner(3)
    centerPoint = tag.getCenter()
    
    # Calculate pixel height of each side of the tag
    LeftSideLength = abs(UpperLeftPoint.y - LowerLeftPoint.y)
    RightSideLength = abs(UpperRightPoint.y - LowerRightPoint.y)
    CloserSideLength = max(LeftSideLength, RightSideLength)

    # If the Left side is larger than the right side, we want to strafe right 
    # Expected range: -0.9 through 0.9 
    x = (LeftSideLength - RightSideLength) / CloserSideLength
    x = round(x, 2)
    vision_nt.putNumber("X_Axis", x)
    
    # If close side length is greater than 80% of of the camera's height, we are too close, the value is negative. Otherwise it is positive. 
    # Expected range: -0.2 through 0.8 
    desired_size_ratio = 0.8 # 80% of the camera height
    
    y = -(CloserSideLength / camera_height - desired_size_ratio)
    y = round(y, 2)
    vision_nt.putNumber("Y_Axis", y)
    
    
    # Calculate distance from center relative to camera width 
    # Expected range: -1.0 through 1.0
    z = (centerPoint.x - (camera_width / 2)) / (camera_width / 2) 
    # Dampen turning value based on our strafe value to prevent overturning
    z *= (1 - abs(x)) 
    z = round(z, 2) 
    vision_nt.putNumber("Z_Axis", z)
    
    
    # Target is considered locked if this distance is within 5% of center
    if ((abs(x) < 0.05) and (abs(y) < 0.05) and (abs(z) < 0.05)):                                          
        targetlocked = True
    
    return targetlocked


          
            
# Function to detect AprilTags in a frame
def detect_april_tags(frame, detector):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray)         
    return tags


# Function to publish detected tags to NetworkTables
def publish_tags_to_networktables(tags, vision_nt):
    count = 0
    for tag in tags:
        # For each detected tag, get the tag ID
        tag_id = tag.getId()
        
        # If the tag ID is greater than 16, its a false detection
        if tag_id > 16:  
            continue
            
        # Count number of tags detected   
        count += 1    
        
        # Get CenterPoint
        centerPoint = tag.getCenter()

        # Publish tag ID and center point position to NetworkTables
        vision_nt.putNumber(f"Tag_{tag_id}_X", centerPoint.x)
        vision_nt.putNumber(f"Tag_{tag_id}_Y", centerPoint.y)

    vision_nt.putNumber("Tags_detected",count)
    
# Function to publish detected tags to NetworkTables
def draw_tags_on_frame(frame, tags):
    for tag in tags:
        # For each detected tag, get the tag ID
        tag_id = tag.getId()
        
        # If the tag ID is greater than 16, its a false detection
        if tag_id > 16:  
            continue
            
        # Draw a green polyline around the AprilTag
        points = []
        for i in range(4):
            corner = (int(tag.getCorner(i).x),int(tag.getCorner(i).y))
            points.append(corner)
        points = numpy.array(points, dtype=numpy.int32).reshape((-1,1,2))
        cv2.polylines(frame, [points], True, (0, 255, 0), 5)

    return frame


# Function to check the game state and decide what to do next
def game_logic(frame, detector, vision_nt):
    # This game, follow me, is simple 
    # We want to lock onto a target AprilTag
    # Turn towards it and then maintain a certain distance away from it
    
    # Detect all AprilTags
    tags = detect_april_tags(frame, detector)

    # Publish detected AprilTags on networktables
    publish_tags_to_networktables(tags, vision_nt)
    
    # Start by assuming target is not located or locked on
    target_located = False
    target_locked = False
    
    # Set our target AprilTag ID to 1
    target_id = 1   

    # See if that target ID is in the set of tags detected
    target_located = locate_target(tags, target_id)                      
    
    # If the target ID is found
    if target_located:  
        # Get the details of that target tag
        target_tag = get_target(tags, target_id) 
        # And turn towards the target until we are "locked on"
        target_locked = orient_to_target(target_tag, vision_nt)   
        
    # If the target is not found
    else:        
        # Just sit there.
        stop(vision_nt) 
        
    
                                             


    
    



def main():
    print("Initializing Camera")
    # Initialize the camera 
    # cap = cv2.VideoCapture(0)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)
    CameraServer.enableLogging()
    camera = CameraServer.startAutomaticCapture()
    camera.setResolution(camera_width, camera_height)
    cvSink = CameraServer.getVideo()
    output = CameraServer.putVideo("Camera", camera_width, camera_height)
    frame = numpy.zeros(shape=(camera_height, camera_width, 3), dtype=numpy.uint8)
    
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
    # Create/Access "Vision" network table
    vision_nt = ntinst.getTable("Vision")  

    
    print("Entering game logic")
    while True:
        # Grab frame 
        t, frame = cvSink.grabFrame(frame)
        
        if t == 0:
            print("Error in cvSink")
            continue
        
        # Run game logic 
        game_logic(frame, detector, vision_nt)
        
        # Draw on the video
        tags = detect_april_tags(frame, detector)
        results = draw_tags_on_frame(frame, tags)      
        
        output.putFrame(results)        
        
        time.sleep(0.1)


if __name__ == "__main__":
    main()


