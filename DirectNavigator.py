
from NetworkController import NetworkController
from PIDController import PIDController

# A class for defining a field with obstacles that can give directions
class DirectNavigator:
    def __init__(self):
        self.controller = NetworkController()
        self.pidalignment = PIDController(2,0,0.1)

    def navigate_to(self, targetposition, targetalignment):
        self.targetx, self.targety = targetposition
        self.targetz = targetalignment

    def aligned_to_target(self, currentorientation):
        aligned = False
        targetorientation = self.targetz
        
        
        # Force our angle values to be between 0 and 360
        targetorientation = targetorientation % 360
        currentorientation = currentorientation % 360

        # Calculate the angular difference
        outofalignment = (targetorientation - currentorientation + 180) % 360 -180

        # Check alignment threshhold
        if abs(outofalignment) > 0.5:             
            z = -(outofalignment / abs(outofalignment)) # Limit our speed to -0.3 or +0.3        
        else:
            z = 0
            aligned = True
 
        # z = self.pidalignment.compute(targetorientation, currentorientation)

        self.controller.setRightJoyX(z)
        return aligned

    # Calculate the best direction in degrees
    def navigate_from(self, current_position, current_alignment):

        current_x_float, current_y_float = current_position

        # Adjusting for the zero based table and rounding to an integer
        currentx = round(current_x_float)
        currenty = round(current_y_float)        

        aligned = self.aligned_to_target(current_alignment)
        ontarget = (currentx == self.targetx and currenty == self.targety)
        
        # Use resulting angle to calculate controller values between -1 and 1
        forward = (self.targetx - currentx)/5
        strafe = (self.targety - currenty)/5

        forward = round(forward * 100)/100
        strafe = round(strafe * 100)/100

        # Set controller values
        # If you're on target, stop
        if ontarget and aligned:
            self.controller.stop()
        elif ontarget:
            self.controller.setLeftJoyY(0)
            self.controller.setLeftJoyX(0)
        else:
            self.controller.setLeftJoyY(forward)
            self.controller.setLeftJoyX(strafe)
            

        return (ontarget and aligned)

