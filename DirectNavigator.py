
from NetworkController import NetworkController
from PIDController import PIDController
from PIDController import AnglePIDController

# A class for defining a field with obstacles that can give directions
class DirectNavigator:
    def __init__(self):
        p=0.01
        i=0.00
        d=0.00
        self.controller = NetworkController()
        self.pidalignment = AnglePIDController(0.015,0,0)
        self.pidforward = PIDController(p,i,d)
        self.pidstrafe = PIDController(p,i,d)
        self.pidforwardpassthrough = PIDController(0.5,0,0.2)
        self.pidstrafepassthrough = PIDController(0.5,0,0.2)
        self.pathindex = 0
        self.targetx = 0
        self.targety = 0
        self.targetz = 0

    def set_passthrough(self, path):
        self.path = path
        self.pathindex = 0
        
    def passthrough(self, position, margin=1.5, lookahead_distance=2.0):
        currentx, currenty = position
        if self.pathindex >= len(self.path):
            return True
    
        # Get the current target based on lookahead
        lookahead_target = get_lookahead_target(self.path, position, lookahead_distance)
        if not lookahead_target:
            return True  # End of path
    
        targetx, targety = lookahead_target
        forward = self.pidforwardpassthrough.compute(targetx, currentx)
        strafe = self.pidstrafepassthrough.compute(targety, currenty)
    
        self.controller.setLeftJoyY(forward)
        self.controller.setLeftJoyX(strafe)
    
        # Check if within margin to the current waypoint
        waypointx, waypointy = self.path[self.pathindex]
        if abs(waypointx - currentx) <= margin and abs(waypointy - currenty) <= margin:
            self.pathindex += 1
    
        return False

    def get_lookahead_target(path, current_position, lookahead_distance):
        currentx, currenty = current_position
        for i in range(len(path) - 1):
            startx, starty = path[i]
            endx, endy = path[i+1]
            segment_length = distance((startx, starty), (endx, endy))
            # Check if lookahead point is in this segment
            if segment_length >= lookahead_distance:
                ratio = lookahead_distance / segment_length
                lookaheadx = startx + ratio * (endx - startx)
                lookaheady = starty + ratio * (endy - starty)
                return lookaheadx, lookaheady
            else:
                # Reduce lookahead distance by segmentlenth for next segment
                lookahead_distance -= segment_length
        return None
        
    
    def distance(point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return ((x2-x1) ** 2 + (y2-y1) ** 2) ** 0.5
    
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
        withinzmargin = abs((self.targetz - currentz + 180) % 360 - 180) <= anglemargin
        ontarget = withinxmargin and withinymargin and withinzmargin

        return ontarget

