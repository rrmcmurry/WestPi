
from NetworkController import NetworkController
from PIDController import PIDController
from PIDController import AnglePIDController

# A class for defining a field with obstacles that can give directions
class DirectNavigator:
    def __init__(self):
        self.controller = NetworkController()
        self.pidalignment = AnglePIDController(0.015,0,0)
        self.pidforward = PIDController(0.1,0,0)
        self.pidstrafe = PIDController(0.1,0,0)
        self.pidforwardpassthrough = PIDController(0.5,0,0.2)
        self.pidstrafepassthrough = PIDController(0.5,0,0.2)
        self.pathindex = 0
        self.targetx = 0
        self.targety = 0
        self.targetz = 0

    def set_passthrough(self, path):
        self.path = path
        self.pathindex = 0
        
    def passthrough(self, position, margin=1.5):
        currentx, currenty = position
        if self.pathindex >= len(self.path):
            return True
        targetx, targety = self.path[self.pathindex]
        forward = self.pidforwardpassthrough.compute(targetx, currentx)
        strafe = self.pidstrafepassthrough.compute(targety, currenty)
        self.controller.setLeftJoyY(forward)
        self.controller.setLeftJoyX(strafe)
        if abs(targetx - currentx) <= margin and abs(targety - currenty) <= margin:            
            self.pathindex = self.pathindex + 1    
        return False

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
        withinzmargin = abs(self.targetz - currentz + 180) % 360 - 180 <= anglemargin
        ontarget = withinxmargin and withinymargin and withinzmargin

        return ontarget

