
import cv2
import robotpy_apriltag
import numpy 
from cscore import CameraServer


# A class for aligning to AprilTags
class CameraManager:
    _instance = None

    @staticmethod
    def get_instance():
        if CameraManager._instance is None:
            CameraManager()
        return CameraManager._instance

    def __init__(self):        
        if CameraManager._instance is not None:
            raise Exception("This class is a singleton!")
        CameraManager._instance = self
        print("Initializing Camera Server")
        # Initialize the camera
        self.camera_width = 960
        self.camera_height = 640
        CameraServer.enableLogging()
        camera = CameraServer.startAutomaticCapture()
        camera.setResolution(self.camera_width, self.camera_height)
        self.cvSink = CameraServer.getVideo()
        self.output = CameraServer.putVideo("Camera", self.camera_width, self.camera_height)
        self.frame = numpy.zeros(shape=(self.camera_height, self.camera_width, 3), dtype=numpy.uint8)
        self.tags = []
     
        print("Initializing AprilTag Detector")
        # Initialize AprilTag Detector
        self.detector = robotpy_apriltag.AprilTagDetector()
        self.detector.addFamily("tag36h11")

        
    # Function that runs on every loop no matter what.
    def periodic(self):
        # Grab video frame 
        t, self.frame = self.cvSink.grabFrame(self.frame)
        # Detect all AprilTags
        self.tags = self.detect_april_tags()
        # Draw any tags found on frame
        results = self.draw_tags_on_frame(self.frame, self.tags)
        # Push the results out to the CameraServer
        self.output.putFrame(results) 
        return
        
    # Function to detect AprilTags in a frame
    def detect_april_tags(self):
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.tags = self.detector.detect(gray)         
        return self.tags
        
 
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
    
    