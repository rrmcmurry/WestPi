
from NetworkController import NetworkController
from PIDController import PIDController
from PIDController import AnglePIDController

# A class for defining a field with obstacles that can give directions
class DirectNavigator:
    def __init__(self):
        self.controller = NetworkController()
        self.pidalignment = AnglePIDController(0.015,0,0)
        self.pidforward = PIDController(0.2,0,0.6)
        self.pidstrafe = PIDController(0.2,0,0.6)
        self.targetx = 0
        self.targety = 0
        self.targetz = 0

    def navigate_to(self, targetposition, targetalignment):
        self.targetx, self.targety = targetposition
        self.targetz = targetalignment

    def navigate_from(self, position, currentz, margin = 0.5, anglemargin = 5):
        currentx, currenty = position
        
        # Compute controller values 
        forward = self.pidforward.compute(self.targetx, currentx)
        strafe = self.pidstrafe.compute(self.targety, currenty)
        rotate = self.pidalignment.compute(self.targetz, currentz)
        
        # Set controller values
        self.controller.setLeftJoyY(forward)
        self.controller.setLeftJoyX(strafe)
        self.controller.setRightJoyX(rotate)
                
        # Are we within margins to be on target?
        withinxmargin = abs(self.targetx - currentx) <= margin     
        withinymargin = abs(self.targety - currenty) <= margin     
        withinzmargin = abs(self.targetz - currentz) <= anglemargin
        ontarget = withinxmargin and withinymargin and withinzmargin

        return (ontarget)

