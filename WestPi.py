import cv2
import robotpy_apriltag
from cscore import CameraServer
import ntcore
import time
import numpy 
import math

# Constants
networktablesserver = True
networktablesserverip = '10.96.68.2'
gameobjectives = [
    {"action": "navigate", "target": (7, 10), "orientation": 90},   # Stage 0
    {"action": "align", "tag_id": 1},                               # Stage 1
    {"action": "wait", "duration": 3},                              # Stage 2
    {"action": "navigate", "target": (1, 5), "orientation":180},    # Stage 3
    {"action": "align", "tag_id": 2},                               # Stage 4
    {"action": "wait", "duration": 3},                              # Stage 5
    {"action": "navigate", "target": (5, 5), "orientation":0},      # Stage 6
    {"action": "wait", "duration": 5},                              # Stage 7
    {"action": "navigate", "target": (1, 1), "orientation":0},      # Stage 8
]


    

# A class for defining a field with obstacles that can give directions
class FlowField:
    def __init__(self):
        self.controller = NetworkController()


    def spread_costs_from_goal(self, goal_x, goal_y):
        for distance in range(1, max(self.width, self.height)):
            for y in range(self.height):
                for x in range(self.width):
                    if self.cost_field[y][x] == distance - 1:
                        for dy, dx in [(-1, 0), (-1,-1), (0,-1), (1,-1), (1, 0), (1, 1), (0, 1), (-1,1)]:
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < self.height and 0 <= nx < self.width:
                                if self.cost_field[ny][nx] > distance:
                                    self.cost_field[ny][nx] = distance


    def generate_flowfield(self, goal, orientation):
        self.goal_x, self.goal_y = goal
        self.goal_z = orientation
        self.width = 21
        self.height = 12
        self.cost_field = [[99 for _ in range(self.width)] for _ in range(self.height)]
        self.cost_field[self.goal_y][self.goal_x] = 0
        self.spread_costs_from_goal(self.goal_x, self.goal_y)
        self.add_obstacle(10,5,2,2) # a 2x2 block right in the middle 
        self.print_flowfield()
        
     
    def add_obstacle(self, start_x, start_y, obstacle_width, obstacle_height):
        for y in range(start_y, start_y + obstacle_height):
            for x in range(start_x, start_x + obstacle_width):
                self.cost_field[y][x] = 99

    def print_flowfield(self):
        # Format and print the cost field as a grid
        formatted_rows = []
        for row in self.cost_field:
            formatted_row = " ".join(f"{cell:2}" for cell in row).strip()
            formatted_rows.append(formatted_row)
            print(formatted_row)

    def aligned_to_target(self, currentorientation):
        aligned = False
        turn = self.goal_z - currentorientation  
        z = 0
        if turn == 0:
            z = 0
            aligned = True
        elif turn < -5: 
            z = -1
        elif turn > 5:
            z = 1
        else:
            z = turn / 5
 
        self.controller.setRightJoyX(z)
        return aligned

    # Calculate the best direction in degrees
    def get_directions(self, current_position, current_alignment):
        current_x_float, current_y_float = current_position

        # Adjusting for the zero based table and rounding to an integer
        current_x = round(current_x_float)
        current_y = round(current_y_float)        

        ontarget = False

        aligned = self.aligned_to_target(current_alignment)

        if current_x == self.goal_x and current_y == self.goal_y:
            ontarget = True
        

        # A set of directions for neighboring cells
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        # An array to store x and y values multiplied by their cost
        weights = []

        # Check all 8 neighbors (including diagonals)
        for dy, dx in directions:
            neighbor_x = current_x + dx
            neighbor_y = current_y + dy

            # Only calculate if within bounds
            if 0 <= neighbor_x < self.width and 0 <= neighbor_y < self.height:
                # Grab the cost of this field
                cost = self.cost_field[neighbor_y][neighbor_x]
                # Skip it if the cost is 99
                #if cost == 99:
                #    continue

                # Weight is the inverse of cost, lower cost = stronger pull
                weight = 1 / cost if cost != 0 else 1  

                # Convert direction into an angle in radians
                angle = math.atan2(dy, dx)  

                # Store the weighted vector (angle and weight)
                """ x value = math.cos(angle) """
                """ y value = math.sin(angle) """
                """ Weighted x value = math.cos(angle) * weight """
                """ Weighted y value = math.sin(angle) * weight """
                weights.append((math.cos(angle) * weight, math.sin(angle) * weight))

        # Add up the weighted vectors
        sum_x = sum(v[0] for v in weights)
        sum_y = sum(v[1] for v in weights)

        # Convert this to an angle in Radians
        resultant_angle = math.atan2(sum_y, sum_x)  

        # Use resulting angle to calculate controller values between -1 and 1
        forward = math.cos(resultant_angle)
        strafe = math.sin(resultant_angle)

        forward = round(forward * 100)/100
        strafe = round(strafe * 100)/100

        # Set controller values
        if ontarget:
            self.controller.setLeftJoyY(0)
            self.controller.setLeftJoyX(0)        
        elif 0 > current_x or current_x > self.width or 0 > current_y or current_y > self.height:
            self.controller.setLeftJoyY(-current_x / current_x)
            self.controller.setLeftJoyX(-current_y / current_y)
        else:
            self.controller.setLeftJoyY(forward)
            self.controller.setLeftJoyX(strafe)
        
        self.controller.publish()

        return (ontarget and aligned)


# A class for emulating an Xbox controller over NetworkTables
class NetworkController:
    _instance = None  # Singleton instance
    

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NetworkController, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Initialize NetworkTables 
        ntinst = ntcore.NetworkTableInstance.getDefault()        
        self.ControllerTable = ntinst.getTable('NetworkController') 

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

    # Method to send all values to NetworkTables
    def publish(self):
        # Push axes
        self.ControllerTable.putNumber('leftJoyX', self.left_joy_x)
        self.ControllerTable.putNumber('leftJoyY', self.left_joy_y)
        self.ControllerTable.putNumber('rightJoyX', self.right_joy_x)
        self.ControllerTable.putNumber('rightJoyY', self.right_joy_y)
        self.ControllerTable.putNumber('leftTrigger', self.left_trigger)
        self.ControllerTable.putNumber('rightTrigger', self.right_trigger)

        # Push buttons
        self.ControllerTable.putBoolean('aButton', self.a_button)
        self.ControllerTable.putBoolean('bButton', self.b_button)
        self.ControllerTable.putBoolean('xButton', self.x_button)
        self.ControllerTable.putBoolean('yButton', self.y_button)
        self.ControllerTable.putBoolean('leftBumper', self.left_bumper)
        self.ControllerTable.putBoolean('rightBumper', self.right_bumper)
        self.ControllerTable.putBoolean('backButton', self.back_button)
        self.ControllerTable.putBoolean('startButton', self.start_button)
        self.ControllerTable.putBoolean('leftStickButton', self.left_stick_button)
        self.ControllerTable.putBoolean('rightStickButton', self.right_stick_button)
        self.ControllerTable.putBoolean('dpadUp', self.dpad_up)
        self.ControllerTable.putBoolean('dpadDown', self.dpad_down)
        self.ControllerTable.putBoolean('dpadLeft', self.dpad_left)
        self.ControllerTable.putBoolean('dpadRight', self.dpad_right)


# A class for tracking current position
class OdometryManager:
    _instance = None

    @staticmethod
    def get_instance():
        if OdometryManager._instance is None:
            OdometryManager()
        return OdometryManager._instance

    def __init__(self):
        if OdometryManager._instance is not None:
            raise Exception("This class is a singleton!")
        OdometryManager._instance = self

        # Initialize NetworkTables and the Pose table
        ntinst = ntcore.NetworkTableInstance.getDefault()
        self.pose_table = ntinst.getTable("Pose")

        # Default position and orientation
        self.current_position = (0.0, 0.0)  # X, Y coordinates
        self.current_orientation = 0.0     # Z orientation (angle in degrees or radians)

    def update_position(self):
        """Fetch the latest position and orientation from the NetworkTables Pose table."""
        x = self.pose_table.getNumber("X", 0.0)
        y = self.pose_table.getNumber("Y", 0.0)
        z = self.pose_table.getNumber("Z", 0.0)

        self.current_position = (x, y)
        self.current_orientation = z

    def get_position(self):
        """Return the current X, Y coordinates."""
        return self.current_position

    def get_orientation(self):
        """Return the current orientation (Z value)."""
        return self.current_orientation

    def adjust_for_error(self, correction):
        """
        Apply a correction to the position.
        :param correction: Tuple (dx, dy, dz) for X, Y, and orientation corrections.
        """
        dx, dy, dz = correction
        x, y = self.current_position
        self.current_position = (x + dx, y + dy)
        self.current_orientation += dz

        """
        # Optionally, push these adjustments back to NetworkTables
        self.pose_table.putNumber("X", self.current_position[0])
        self.pose_table.putNumber("Y", self.current_position[1])
        self.pose_table.putNumber("Z", self.current_orientation)
        """


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

        # STRAFE: If the Left side is larger than the right side, we want to strafe right 
        """ expected values are between -0.5 and +0.5 """
        strafe = (LeftSideLength - RightSideLength) / CloserSideLength
        """ expected values are between -.75 and 0.75 """
        strafe = strafe * 1.5 
        
        
        # FORWARD: If close side length out of camera's height is greater than 80%, the value goes negative. Otherwise it is positive.         
        """ expected values are -0.2 to +0.8 """
        desired_size_ratio = 0.8 
        forward = -(CloserSideLength / self.camera_height - desired_size_ratio)
        """ expected values are now -0.25 to +1.0 """
        forward = forward * 1.25 

        # ROTATE: Calculate distance between center of apriltag and center of camera 
        """ Expected range: -1.0 through 1.0 """
        rotate = (centerPoint.x - (self.camera_width / 2)) / (self.camera_width / 2) 
        """ Dampening rotation based on our current strafe value to prevent overturning """
        rotate *= (1 - abs(strafe)) 
        
        
        # Target is considered locked if robot oriented strafe, forward, and rotate values are all lower than 0.10
        if ((abs(strafe) < 0.10) and (abs(forward) < 0.10) and (abs(rotate) < 0.10)):                                          
            targetlocked = True


        # At this point forward and strafe are robot oriented. Translating to field oriented.
        currentorientation = math.radians(self.OdometryMannager.get_orientation())
        fieldforward = forward * math.cos(currentorientation) - strafe * math.sin(currentorientation)
        fieldstrafe = forward * math.sin(currentorientation) + strafe * math.cos(currentorientation)

        # Rounding everything to 2 decimals
        fieldforward = round(fieldforward, 2)
        fieldstrafe = round(fieldstrafe, 2)
        rotate = round(rotate, 2) 

        # Publishing values to the network controller
        self.controller.setLeftJoyY(fieldforward)
        self.controller.setLeftJoyX(fieldstrafe)
        self.controller.setRightJoyX(rotate)
        self.controller.publish()

        return targetlocked


# A class for defining the stages of the game and the objectives in that stage
class GameManager:
    def __init__(self):
        ntinst = ntcore.NetworkTableInstance.getDefault() 
        if networktablesserver:
            ntinst.startServer()
        else:
            ntinst.startClient4(networktablesserverip)
        self.GameTable = ntinst.getTable('GameManager') 
        self.objectivechanged = True
        self.stage = 0
        self.wait_start_time = None
        self.objectives = gameobjectives
        self.print_current_objective()

    def get_current_objective(self):
        if self.stage < len(self.objectives):
            return self.objectives[self.stage]
        return None  # Game is complete

    def print_current_objective(self):
        if self.stage < len(self.objectives):
            self.GameTable.putNumber('Stage', self.stage)
            objective = self.objectives[self.stage]
            action = objective["action"]
            self.GameTable.putString("Action",action)     
            try:
                targetx, targety = objective["target"]
                targetorientation = objective["orientation"]
                self.GameTable.putString("Target",f"({targetx},{targety})")
                self.GameTable.putString("Target Orientation",f"{targetorientation} degrees")
            except:
                self.GameTable.putString("Target",f"None")
            try:
                targettag = objective["tag_id"]
                self.GameTable.putString("Target Apriltag", f"{targettag}")
            except:
                self.GameTable.putString("Target Apriltag", f"None")
            print(f"Objective: {self.objectives[self.stage]}")

    def advance_stage(self):        
        self.stage += 1
        self.objectivechanged = True
        self.wait_start_time = None 
        print(f"Advancing to stage {self.stage}")
        self.print_current_objective()
        
        
    def objective_has_changed(self):
        changed = self.objectivechanged
        self.objectivechanged = False
        return changed
        
  
        
# Main Loop
def main():

    # Initialize class instances
    game_manager = GameManager()    
    odometry_manager = OdometryManager.get_instance()
    navigator = FlowField()
    april_tag_aligner = AprilTagAligner()    

    print("Entering game logic")
    # Enter main loop to run game logic
    while True:

        # Call periodic functions for things that need to update every time
        april_tag_aligner.periodic()
        
        # Get our current objective from the game manager
        objective = game_manager.get_current_objective()
        if not objective:
            print("Game complete!")
            break

        # Get our current position from the odometry manager
        odometry_manager.update_position()

        # If navigating
        if objective["action"] == "navigate":
            # On first round, set up navigator
            if game_manager.objective_has_changed():
                navigator.generate_flowfield(objective["target"], objective["orientation"])
                
            # Navigate to target and align to target alignment
            ontarget = navigator.get_directions(odometry_manager.get_position(), odometry_manager.get_orientation())
            if ontarget: 
                game_manager.advance_stage()

        # If aligning to an April Tag
        elif objective["action"] == "align":
            aligned = april_tag_aligner.align_to_tag(objective["tag_id"])                 
            if aligned:
                game_manager.advance_stage()

        # If waiting
        elif objective["action"] == "wait":            
            if game_manager.objective_has_changed():
                game_manager.wait_start_time = time.time()
            elapsed_time = time.time() - game_manager.wait_start_time
            print(f"{elapsed_time}")
            if elapsed_time >= objective["duration"]:            
                game_manager.advance_stage()
        
        
        # Sleep 
        """ only needed if pushing values to networktables on the roborio to prevent flooding """
        # time.sleep(0.1)


if __name__ == "__main__":
    main()


