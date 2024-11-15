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

from ntcore import NetworkTables

# Initialize NetworkTables (replace with your server IP)
NetworkTables.initialize(server='10.96.68.2')  # Replace with your RoboRIO's IP
ControllerTable = NetworkTables.getTable('Controller')  # Name your table as needed

class FlowField:
    def __init__(self, width, height, goal_x, goal_y):
        self.width = width
        self.height = height
        self.cost_field = [[99 for _ in range(width)] for _ in range(height)]
        self.cost_field[goal_y-1][goal_x-1] = 0
        self.spread_costs_from_goal(goal_x, goal_y)

    def spread_costs_from_goal(self, goal_x, goal_y):
        for distance in range(1, max(self.width, self.height)):
            for y in range(self.height):
                for x in range(self.width):
                    if self.cost_field[y][x] == distance - 1:
                        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < self.height and 0 <= nx < self.width:
                                if self.cost_field[ny][nx] > distance:
                                    self.cost_field[ny][nx] = distance


    def add_obstacle(self, start_x, start_y, obstacle_width, obstacle_height):
        for y in range(start_y-1, start_y + obstacle_height-1):
            for x in range(start_x-1, start_x + obstacle_width-1):
                self.cost_field[y][x] = 99

    def print_flowfield(self):
        # Format and print the cost field as a grid
        for row in self.cost_field:
            print(" ".join(f"{cell:2}" for cell in row))

    # Calculate the best direction in degrees
    def get_directions(self, current_x, current_y):
        current_x = current_x-1
        current_y = current_y-1        
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        weights = []

        
        # Check all 8 neighbors (including diagonals)
        for dy, dx in directions:
            neighbor_x = current_x + dx
            neighbor_y = current_y + dy

            # Only calculate if within bounds
            if 0 <= neighbor_x < self.width and 0 <= neighbor_y < self.height:
                cost = self.cost_field[neighbor_y][neighbor_x]
                if cost == 99:
                    continue

                weight = 1 / cost if cost != 0 else 1  # Inverse of cost, lower cost = stronger pull
                angle = math.atan2(dy, dx)  # Angle in radians
                angleindegrees = math.degrees(angle)
                # print(f"{neighbor_x},{neighbor_y}:{cost}:{angleindegrees}{weight}")
                
                # Store the weighted vector (angle and weight)
                weights.append((math.cos(angle) * weight, math.sin(angle) * weight))

        # Sum the weighted vectors
        sum_x = sum(v[0] for v in weights)
        sum_y = sum(v[1] for v in weights)

        
        # Calculate the resultant angle
        resultant_angle = math.atan2(sum_y, sum_x)  # Angle in radians

        # Convert to degrees (0 degrees is north)
        degrees = math.degrees(resultant_angle)
        return (degrees + 360) % 360  # Ensure the angle is between 0 and 360 degrees

class Controller:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Controller, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Initialize all Xbox controller buttons and axes
        # Axes (joysticks and triggers range from -1.0 to 1.0)
        self.left_joy_x = 0.0
        self.left_joy_y = 0.0
        self.right_joy_x = 0.0
        self.right_joy_y = 0.0
        self.left_trigger = 0.0
        self.right_trigger = 0.0
        
        # Buttons (Boolean values)
        self.a_button = False
        self.b_button = False
        self.x_button = False
        self.y_button = False
        self.left_bumper = False
        self.right_bumper = False
        self.back_button = False
        self.start_button = False
        self.left_stick_button = False
        self.right_stick_button = False
        self.dpad_up = False
        self.dpad_down = False
        self.dpad_left = False
        self.dpad_right = False

    # Setter methods for each axis
    def setLeftJoyX(self, value):
        self.left_joy_x = value

    def setLeftJoyY(self, value):
        self.left_joy_y = value

    def setRightJoyX(self, value):
        self.right_joy_x = value

    def setRightJoyY(self, value):
        self.right_joy_y = value

    def setLeftTrigger(self, value):
        self.left_trigger = value

    def setRightTrigger(self, value):
        self.right_trigger = value

    # Setter methods for each button
    def setAButton(self, pressed):
        self.a_button = pressed

    def setBButton(self, pressed):
        self.b_button = pressed

    def setXButton(self, pressed):
        self.x_button = pressed

    def setYButton(self, pressed):
        self.y_button = pressed

    def setLeftBumper(self, pressed):
        self.left_bumper = pressed

    def setRightBumper(self, pressed):
        self.right_bumper = pressed

    def setBackButton(self, pressed):
        self.back_button = pressed

    def setStartButton(self, pressed):
        self.start_button = pressed

    def setLeftStickButton(self, pressed):
        self.left_stick_button = pressed

    def setRightStickButton(self, pressed):
        self.right_stick_button = pressed

    def setDpadUp(self, pressed):
        self.dpad_up = pressed

    def setDpadDown(self, pressed):
        self.dpad_down = pressed

    def setDpadLeft(self, pressed):
        self.dpad_left = pressed

    def setDpadRight(self, pressed):
        self.dpad_right = pressed

    # Push method to send all values to NetworkTables
    def publish(self):
        # Push axes
        ControllerTable.putNumber('leftJoyX', self.left_joy_x)
        ControllerTable.putNumber('leftJoyY', self.left_joy_y)
        ControllerTable.putNumber('rightJoyX', self.right_joy_x)
        ControllerTable.putNumber('rightJoyY', self.right_joy_y)
        ControllerTable.putNumber('leftTrigger', self.left_trigger)
        ControllerTable.putNumber('rightTrigger', self.right_trigger)

        # Push buttons
        ControllerTable.putBoolean('aButton', self.a_button)
        ControllerTable.putBoolean('bButton', self.b_button)
        ControllerTable.putBoolean('xButton', self.x_button)
        ControllerTable.putBoolean('yButton', self.y_button)
        ControllerTable.putBoolean('leftBumper', self.left_bumper)
        ControllerTable.putBoolean('rightBumper', self.right_bumper)
        ControllerTable.putBoolean('backButton', self.back_button)
        ControllerTable.putBoolean('startButton', self.start_button)
        ControllerTable.putBoolean('leftStickButton', self.left_stick_button)
        ControllerTable.putBoolean('rightStickButton', self.right_stick_button)
        ControllerTable.putBoolean('dpadUp', self.dpad_up)
        ControllerTable.putBoolean('dpadDown', self.dpad_down)
        ControllerTable.putBoolean('dpadLeft', self.dpad_left)
        ControllerTable.putBoolean('dpadRight', self.dpad_right)

controller = Controller()




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


# Function to orient to target 
def orient_to_target(tag):
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
    controller.setLeftJoyX(x)

    # If close side length is greater than 80% of of the camera's height, we are too close, the value is negative. Otherwise it is positive. 
    # Expected range: -0.2 through 0.8 
    desired_size_ratio = 0.8 # 80% of the camera height
    
    y = -(CloserSideLength / camera_height - desired_size_ratio)
    y = round(y, 2)
    controller.setLeftJoyY(y)
    
    # Calculate distance from center relative to camera width 
    # Expected range: -1.0 through 1.0
    z = (centerPoint.x - (camera_width / 2)) / (camera_width / 2) 
    # Dampen turning value based on our strafe value to prevent overturning
    z *= (1 - abs(x)) 
    z = round(z, 2) 
    controller.setRightJoyX(z)
    
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
def game_logic(frame, detector):
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
        target_locked = orient_to_target(target_tag)   
        
    # If the target is not found
    else:        
        # Just sit there.
        controller.setLeftJoyX(0)
        controller.setLeftJoyY(0)
        controller.setRightJoyX(0)

    controller.publish()    
        

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

    print("Entering game logic")
    # Enter main loop to run game logic
    while True:
        # Grab video frame 
        t, frame = cvSink.grabFrame(frame)
        
        # Run game logic 
        game_logic(frame, detector)
        
        # Draw tags on the video frame
        tags = detect_april_tags(frame, detector)
        results = draw_tags_on_frame(frame, tags)      
        output.putFrame(results)        
        
        # Sleep 
        time.sleep(0.1)


if __name__ == "__main__":
    main()


