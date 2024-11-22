import ntcore
import time

# A class for emulating an Xbox controller over NetworkTables
class NetworkController:
    _instance = None  # Singleton instance
    

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NetworkController, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        print("NetworkController Initializing")
        # Initialize time for periodic         
        self.last_time = time.time()
        
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

    def reset(self):
        # Sets all xbox controller values back to defaults
        # Axes 
        self.left_joy_x = 0.0
        self.left_joy_y = 0.0
        self.right_joy_x = 0.0
        self.right_joy_y = 0.0
        self.left_trigger = 0.0
        self.right_trigger = 0.0
        
        # Buttons 
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

    def stop(self):
        # Sets joystick values back to zero
        # Axes 
        self.left_joy_x = 0.0
        self.left_joy_y = 0.0
        self.right_joy_x = 0.0
        self.right_joy_y = 0.0
        self.left_trigger = 0.0
        self.right_trigger = 0.0

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

    # Periodic runs once every loop but only publishes to NetworkTables once every 10 milliseconds to prevent network flooding
    """ This should prevent the need to call sleep in the main loop which should improve our video quality """
    def periodic(self):
        elapsed_time = time.time() - self.last_time
        if elapsed_time >= 0.1:            
            self.publish()
            self.last_time = time.time()