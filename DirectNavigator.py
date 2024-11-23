
from NetworkController import NetworkController
from PIDController import PIDController
from PIDController import AnglePIDController

# A class for defining a field with obstacles that can give directions
class DirectNavigator:
    def __init__(self):
        self.controller = NetworkController()
        self.pidalignment = AnglePIDController(0.8,0,0)
        self.pidforward = PIDController(1,0,0)
        self.pidstrafe = PIDController(1,0,0)
        self.targetx = 0
        self.targety = 0
        self.targetz = 0

    def navigate_to(self, targetposition, targetalignment):
        self.targetx, self.targety = targetposition
        self.targetz = targetalignment

    # Calculate the best direction in degrees
    def navigate_from(self, current_position, current_angle):

        current_x_float, current_y_float = current_position

        # Adjusting for the zero based table and rounding to an integer
        currentx = round(current_x_float,1)
        currenty = round(current_y_float,1)
        currentz = round(current_angle,1)

        
        # Use resulting angle to calculate controller values between -1 and 1
        forward = self.pidforward.compute(self.targetx, current_x_float)
        strafe = self.pidstrafe.compute(self.targety, current_y_float)
        rotate = self.pidalignment.compute(self.targetz, current_angle)
        
        aligned = (currentz == self.targetz)
        ontarget = (currentx == self.targetx and currenty == self.targety)

        # Set controller values
        # If you're on target, stop
        if ontarget:
            self.controller.stop()
        elif ontarget:
            self.controller.setLeftJoyY(0)
            self.controller.setLeftJoyX(0)
        else:
            self.controller.setLeftJoyY(forward)
            self.controller.setLeftJoyX(strafe)
        
        if aligned:
            self.controller.setRightJoyX(0)
        else:
            self.controller.setRightJoyX(rotate)
            

        return (ontarget and aligned)
