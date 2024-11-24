
import cv2
import robotpy_apriltag
import numpy 
import math
from cscore import CameraServer
from NetworkController import NetworkController
from PIDController import PIDController
from PIDController import AnglePIDController
from CameraManager import CameraManager

# A class for aligning to AprilTags
class AprilTagAligner:
    def __init__(self):        
        # Initialize 
        self.camera = CameraManager.get_instance()
        self.camera_width = self.camera.camera_width
        self.camera_height = self.camera.camera_height        
        self.controller = NetworkController()
        self.pidalignment = AnglePIDController(0.015,0,0)
        self.pidforward = PIDController(0.2,0,0.6)
        self.pidstrafe = PIDController(0.2,0,0.6)
        
    
    # Align to a specified AprilTag        
    def align_to_tag(self, tag_id, currentorientation):
        # Logic to align to the specified AprilTag 
        self.currentorientation = currentorientation
        aligned = False
        # If we can see the tag, align to it
        if self.target_located(tag_id):
            aligned = self.orient_to_target(self.get_targettag(tag_id))
        # Otherwise spin in a circle to the right
        else:
            self.controller.stop()
            self.controller.setRightJoyX(-0.3)

        return aligned
        

    # Boolean function returns whether target was located
    def target_located(self, targettagid):
        targetlocated = False       
        self.tags = self.camera.detect_april_tags()
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
        
    
    
    # Function to orient to target 
    def orient_to_target(self, tag):
        # target is not locked by default
        targetlocked = False
        
        # Full tag definition here for reference:
        # robotpy_apriltag.AprilTagDetector().detect(cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY))[0]

        # Grab points from the tag - These wrap counter-clockwise around the tag. Index 0 is bottom left corner.
        
        UpperLeftPoint = tag.getCorner(3) 
        UpperRightPoint = tag.getCorner(2) 
        LowerRightPoint = tag.getCorner(1)
        LowerLeftPoint = tag.getCorner(0) 
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
        currentorientationinradians = math.radians(self.currentorientation)
        fieldforward = forward * math.cos(currentorientationinradians) - strafe * math.sin(currentorientationinradians)
        fieldstrafe = forward * math.sin(currentorientationinradians) + strafe * math.cos(currentorientationinradians)

        # Rounding everything to 2 decimals
        fieldforward = round(fieldforward * 0.5, 2)
        fieldstrafe = -round(fieldstrafe * 0.5, 2)
        rotate = round(rotate, 2) 

        if targetlocked:
            self.controller.stop()
        else:
            # Publishing values to the network controller
            self.controller.setLeftJoyY(fieldforward)
            self.controller.setLeftJoyX(fieldstrafe)
            self.controller.setRightJoyX(rotate)
        

        return targetlocked