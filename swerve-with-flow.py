import cv2
import robotpy_apriltag
from cscore import CameraServer
import ntcore
import time
import numpy 

# Constants
teamnumber = 9668
camera_width = 960
camera_height = 640

flow_field = [
    [ # Field 0 - Flow to center
        [(0.9, 1), (0.7, 1), (0.5, 1), (0.3, 1), (0.1, 1), (0, 1), (-0.1, 1), (-0.3, 1), (-0.5, 1), (-0.7, 1), (-0.9, 1)],
        [(0.9, 1), (0.7, 1), (0.5, 1), (0.3, 1), (0.1, 1), (0, 1), (-0.1, 1), (-0.3, 1), (-0.5, 1), (-0.7, 1), (-0.9, 1)],
        [(0.9, 1), (0.7, 1), (0.5, 1), (0.3, 1), (0.1, 1), (0, 1), (-0.1, 1), (-0.3, 1), (-0.5, 1), (-0.7, 1), (-0.9, 1)],
        [(0.9, 1), (0.7, 1), (0.5, 1), (0.3, 1), (0.1, 1), (0, 1), (-0.1, 1), (-0.3, 1), (-0.5, 1), (-0.7, 1), (-0.9, 1)],
        [(0.9, 1), (0.7, 1), (0.5, 1), (0.3, 1), (0.1, 1), (0, 1), (-0.1, 1), (-0.3, 1), (-0.5, 1), (-0.7, 1), (-0.9, 1)],
        [(0.9, 1), (0.7, 1), (0.5, 1), (0.3, 1), (0.1, 1), (0, 1), (-0.1, 1), (-0.3, 1), (-0.5, 1), (-0.7, 1), (-0.9, 1)],
        [(0.9, 0.7), (0.7, 0.7), (0.5, 0.7), (0.3, 0.7), (0.1, 0.7), (0, 0.7), (-0.1, 0.7), (-0.3, 0.7), (-0.5, 0.7), (-0.7, 0.7), (-0.9, 0.7)],
        [(0.9, 0.5), (0.7, 0.5), (0.5, 0.5), (0.3, 0.5), (0.1, 0.5), (0, 0.5), (-0.1, 0.5), (-0.3, 0.5), (-0.5, 0.5), (-0.7, 0.5), (-0.9, 0.5)],
        [(0.9, 0.3), (0.7, 0.3), (0.5, 0.3), (0.3, 0.3), (0.1, 0.3), (0, 0.3), (-0.1, 0.3), (-0.3, 0.3), (-0.5, 0.3), (-0.7, 0.3), (-0.9, 0.3)],
        [(0.9, 0.1), (0.7, 0.1), (0.5, 0.1), (0.3, 0.1), (0.1, 0.1), (0, 0.1), (-0.1, 0.1), (-0.3, 0.1), (-0.5, 0.1), (-0.7, 0.1), (-0.9, 0.1)],
        [(0.9, 0), (0.7, 0), (0.5, 0), (0.3, 0), (0.1, 0), (0, 0), (-0.1, 0), (-0.3, 0), (-0.5, 0), (-0.7, 0), (-0.9, 0)],
        [(0.9, -0.1), (0.7, -0.1), (0.5, -0.1), (0.3, -0.1), (0.1, -0.1), (0, -0.1), (-0.1, -0.1), (-0.3, -0.1), (-0.5, -0.1), (-0.7, -0.1), (-0.9, -0.1)],
        [(0.9, -0.3), (0.7, -0.3), (0.5, -0.3), (0.3, -0.3), (0.1, -0.3), (0, -0.3), (-0.1, -0.3), (-0.3, -0.3), (-0.5, -0.3), (-0.7, -0.3), (-0.9, -0.3)],
        [(0.9, -0.5), (0.7, -0.5), (0.5, -0.5), (0.3, -0.5), (0.1, -0.5), (0, -0.5), (-0.1, -0.5), (-0.3, -0.5), (-0.5, -0.5), (-0.7, -0.5), (-0.9, -0.5)],
        [(0.9, -0.7), (0.7, -0.7), (0.5, -0.7), (0.3, -0.7), (0.1, -0.7), (0, -0.7), (-0.1, -0.7), (-0.3, -0.7), (-0.5, -0.7), (-0.7, -0.7), (-0.9, -0.7)],
        [(0.9, -1), (0.7, -1), (0.5, -1), (0.3, -1), (0.1, -1), (0, -1), (-0.1, -1), (-0.3, -1), (-0.5, -1), (-0.7, -1), (-0.9, -1)],
        [(0.9, -1), (0.7, -1), (0.5, -1), (0.3, -1), (0.1, -1), (0, -1), (-0.1, -1), (-0.3, -1), (-0.5, -1), (-0.7, -1), (-0.9, -1)],
        [(0.9, -1), (0.7, -1), (0.5, -1), (0.3, -1), (0.1, -1), (0, -1), (-0.1, -1), (-0.3, -1), (-0.5, -1), (-0.7, -1), (-0.9, -1)],
        [(0.9, -1), (0.7, -1), (0.5, -1), (0.3, -1), (0.1, -1), (0, -1), (-0.1, -1), (-0.3, -1), (-0.5, -1), (-0.7, -1), (-0.9, -1)],
        [(0.9, -1), (0.7, -1), (0.5, -1), (0.3, -1), (0.1, -1), (0, -1), (-0.1, -1), (-0.3, -1), (-0.5, -1), (-0.7, -1), (-0.9, -1)],
        [(0.9, -1), (0.7, -1), (0.5, -1), (0.3, -1), (0.1, -1), (0, -1), (-0.1, -1), (-0.3, -1), (-0.5, -1), (-0.7, -1), (-0.9, -1)]      
    ],
    [ # Field 1 - Flow to starting corner
        [(0, 0), (-0.1, 0), (-0.2, 0), (-0.5, 0), (-0.7, 0), (-1, 0), (-1, 0), (-1, 0), (-1, 0), (-1, 0), (-1, 0)],
        [(0, -0.1), (-0.1, -0.1), (-0.2, -0.1), (-0.5, -0.1), (-0.7, -0.1), (-1, -0.1), (-1, -0.1), (-1, -0.1), (-1, -0.1), (-1, -0.1), (-1, -0.1)],
        [(0, -0.3), (-0.1, -0.3), (-0.2, -0.3), (-0.5, -0.3), (-0.7, -0.3), (-1, -0.3), (-1, -0.3), (-1, -0.3), (-1, -0.3), (-1, -0.3), (-1, -0.3)],
        [(0, -0.5), (-0.1, -0.5), (-0.2, -0.5), (-0.5, -0.5), (-0.7, -0.5), (-1, -0.5), (-1, -0.5), (-1, -0.5), (-1, -0.5), (-1, -0.5), (-1, -0.5)],
        [(0, -0.7), (-0.1, -0.7), (-0.2, -0.7), (-0.5, -0.7), (-0.7, -0.7), (-1, -0.7), (-1, -0.7), (-1, -0.7), (-1, -0.7), (-1, -0.7), (-1, -0.7)],
        [(0, -1), (-0.1, -1), (-0.2, -1), (-0.5, -1), (-0.7, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)],
        [(0, -1), (-0.1, -1), (-0.2, -1), (-0.5, -1), (-0.7, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)],
        [(0, -1), (-0.1, -1), (-0.2, -1), (-0.5, -1), (-0.7, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)],
        [(0, -1), (-0.1, -1), (-0.2, -1), (-0.5, -1), (-0.7, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)],
        [(0, -1), (-0.1, -1), (-0.2, -1), (-0.5, -1), (-0.7, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)],
        [(0, -1), (-0.1, -1), (-0.2, -1), (-0.5, -1), (-0.7, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)],
        [(0, -1), (-0.1, -1), (-0.2, -1), (-0.5, -1), (-0.7, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)],
        [(0, -1), (-0.1, -1), (-0.2, -1), (-0.5, -1), (-0.7, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)],
        [(0, -1), (-0.1, -1), (-0.2, -1), (-0.5, -1), (-0.7, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)],
        [(0, -1), (-0.1, -1), (-0.2, -1), (-0.5, -1), (-0.7, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)],
        [(0, -1), (-0.1, -1), (-0.2, -1), (-0.5, -1), (-0.7, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)],
        [(0, -1), (-0.1, -1), (-0.2, -1), (-0.5, -1), (-0.7, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)],
        [(0, -1), (-0.1, -1), (-0.2, -1), (-0.5, -1), (-0.7, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)],
        [(0, -1), (-0.1, -1), (-0.2, -1), (-0.5, -1), (-0.7, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)],
        [(0, -1), (-0.1, -1), (-0.2, -1), (-0.5, -1), (-0.7, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)],
        [(0, -1), (-0.1, -1), (-0.2, -1), (-0.5, -1), (-0.7, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)]

    ]
]


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


# Function to stop
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


# Function to draw detected apriltags on a video frame
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
    ntinst.startClient4("10.96.68.2")    
    ntinst.setServerTeam(teamnumber) 
    vision_nt = ntinst.getTable("Vision")  
    
    print("Entering game logic")
    # Enter main loop to run game logic
    while True:
        # Grab video frame 
        t, frame = cvSink.grabFrame(frame)
        
        # Run game logic 
        game_logic(frame, detector, vision_nt)
        
        # Draw tags on the video frame
        tags = detect_april_tags(frame, detector)
        results = draw_tags_on_frame(frame, tags)      
        output.putFrame(results)        
        
        # Sleep 
        time.sleep(0.1)


if __name__ == "__main__":
    main()


