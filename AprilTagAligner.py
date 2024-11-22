
import cv2
import robotpy_apriltag
import numpy 
import math
from cscore import CameraServer
from NetworkController import NetworkController
from OdometryManager import OdometryManager

# A class for aligning to AprilTags
class AprilTagAligner:
    def __init__(self):
        print("Initializing Camera")
        # Initialize the camera
        self.camera_width = 960
        self.camera_height = 640
        CameraServer.enableLogging()
        camera = CameraServer.startAutomaticCapture()
        camera.setResolution(self.camera_width, self.camera_height)
        self.cvSink = CameraServer.getVideo()
        self.output = CameraServer.putVideo("Camera", self.camera_width, self.camera_height)
        self.frame = numpy.zeros(shape=(self.camera_height, self.camera_width, 3), dtype=numpy.uint8)
        
        self.OdometryMannager = OdometryManager.get_instance()
        self.controller = NetworkController()

        print("Initializing AprilTag detector")
        # Initialize AprilTag Detector
        self.detector = robotpy_apriltag.AprilTagDetector()
        self.detector.addFamily("tag36h11")
        pass
        
    # Function that runs on every loop no matter what.
    def periodic(self):
        # Grab video frame 
        t, self.frame = self.cvSink.grabFrame(self.frame)
        # Detect all AprilTags
        self.tags = self.detect_april_tags(self.frame, self.detector)
        # Draw any tags found on frame
        results = self.draw_tags_on_frame(self.frame, self.tags)
        # Push the results out to the CameraServer
        self.output.putFrame(results) 
        return
        
    # Function to detect AprilTags in a frame
    def detect_april_tags(self, frame, detector):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.tags = detector.detect(gray)         
        return self.tags
        
    def align_to_tag(self, tag_id):
        # Logic to align to the specified AprilTag
        aligned = False
        if self.target_located(tag_id):
            aligned = self.orient_to_target(self.get_targettag(tag_id))
        else:
            print(f"Error: Cannot find tag {tag_id}")

        return aligned
        

    # Boolean function returns whether target was located
    def target_located(self, targettagid):
        targetlocated = False
        for tag in self.tags:
            tag_id = tag.getId()
            if tag_id == targettagid:
                targetlocated = True
        return targetlocated
        
    # Returns the target tag object from a set of tags    
    def get_targettag(self, targettagid):
        targettag = []
        for tag in self.tags:
            tag_id = tag.getId()
            if tag_id == targettagid:
                targettag = tag
        return targettag
    
    # Function to draw detected apriltags on a video frame
    def draw_tags_on_frame(self, frame, tags):
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
    
    # Function to orient to target 
    def orient_to_target(self, tag):
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

        
        
        
        # FORWARD: If close side length out of camera's height is greater than 80%, the value goes negative. Otherwise it is positive.         
        """ expected values are -0.2 to +0.8 """
        desired_size_ratio = 0.8 
        forward = -(CloserSideLength / self.camera_height - desired_size_ratio)
        """ expected values are now -0.25 to +1.0 """
        forward = forward * 1.25 

        # STRAFE: If the Left side is larger than the right side, we want to strafe right 
        """ expected values are between -0.5 and +0.5 """
        strafe = (LeftSideLength - RightSideLength) / CloserSideLength
        """ expected values are between -.75 and 0.75 """
        strafe = -strafe * 1.5 

        # ROTATE: Calculate distance between center of apriltag and center of camera 
        """ Expected range: -1.0 through 1.0 """
        rotate = -(centerPoint.x - (self.camera_width / 2)) / (self.camera_width / 2) 
        """ Dampening rotation based on our current strafe value to prevent overturning """
        rotate = -rotate * 0.3
        # rotate *= (1 - abs(strafe)) 
        
        
        # Target is considered locked if robot oriented strafe, forward, and rotate values are all lower than 0.10
        if ((abs(strafe) < 0.20) and (abs(forward) < 0.20) and (abs(rotate) < 0.20)):                                          
            targetlocked = True


        # At this point forward and strafe are robot oriented. Translating to field oriented.
        currentorientation = math.radians(self.OdometryMannager.get_orientation())
        fieldforward = forward * math.cos(currentorientation) - strafe * math.sin(currentorientation)
        fieldstrafe = forward * math.sin(currentorientation) + strafe * math.cos(currentorientation)

        # Rounding everything to 2 decimals
        fieldforward = round(fieldforward * 0.5, 2)
        fieldstrafe = -round(fieldstrafe * 0.5, 2)
        rotate = round(rotate, 2) 

        # Publishing values to the network controller
        self.controller.setLeftJoyY(fieldforward)
        self.controller.setLeftJoyX(fieldstrafe)
        self.controller.setRightJoyX(rotate)
        

        return targetlocked