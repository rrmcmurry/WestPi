
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
        self.pidforward = PIDController(0.2,0,0.6)
        self.pidstrafe = PIDController(0.2,0,0.6)
        self.pidrotate = PIDController(0.015,0,0)
    
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
    
    
    # Align to a specified AprilTag        
    def align_to_tag(self, tag_id, currentorientation):
        # Logic to align to the specified AprilTag 
        self.currentorientation = currentorientation
        
        targetlocked = False

        if self.target_located(tag_id):
            targettag = self.get_targettag(tag_id)

            UpperLeftPoint = targettag.getCorner(3) 
            UpperRightPoint = targettag.getCorner(2) 
            LowerRightPoint = targettag.getCorner(1)
            LowerLeftPoint = targettag.getCorner(0) 
            centerPoint = targettag.getCenter()

            # Calculate pixel height of each side of the tag
            LeftSideLength = abs(UpperLeftPoint.y - LowerLeftPoint.y)
            RightSideLength = abs(UpperRightPoint.y - LowerRightPoint.y)
            CloserSideLength = max(LeftSideLength, RightSideLength)

            # This ratio represents our distance from the AprilTag
            RatioOfAprilTagToCameraHeight = CloserSideLength / self.camera_height 
            
            # This ratio represents how far we are from being squarely in front of the AprilTag smaller values means closer to square.
            RatioOfSideLengthDifferencesToCloserSide = (LeftSideLength - RightSideLength) / CloserSideLength 

            # Distance from the center of the AprilTag to the Center of the Image as a ratio.. so values between -1 and 1
            CenterOfImage = self.camera_width / 2
            DistanceFromCenter = (centerPoint.x - CenterOfImage) / CenterOfImage 

            # Use PID to compute values
            forward = self.pidforward.compute(0.8,RatioOfAprilTagToCameraHeight)
            strafe = self.pidstrafe.compute(0,RatioOfSideLengthDifferencesToCloserSide) 
            rotate = self.pidrotate.compute(0,DistanceFromCenter)

            # At this point forward and strafe are robot oriented. Translating to field oriented.
            currentorientationinradians = math.radians(self.currentorientation)
            fieldforward = forward * math.cos(currentorientationinradians) - strafe * math.sin(currentorientationinradians)
            fieldstrafe = forward * math.sin(currentorientationinradians) + strafe * math.cos(currentorientationinradians)

            targetlocked = RatioOfAprilTagToCameraHeight == 0.8 and RatioOfSideLengthDifferencesToCloserSide == 0 and DistanceFromCenter == 0

            if targetlocked:
                self.controller.stop()
            else:
                # Publishing values to the network controller
                self.controller.setLeftJoyY(fieldforward)
                self.controller.setLeftJoyX(fieldstrafe)
                self.controller.setRightJoyX(rotate)

        else:
            # If we can't see the AprilTag... spin in place
            self.controller.stop()
            self.controller.setRightJoyX(-0.3)

       

        return targetlocked
        

   
    
