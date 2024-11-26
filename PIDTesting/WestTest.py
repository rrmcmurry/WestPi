
import ntcore # type: ignore
import time
from NetworkController import NetworkController
from OdometryManager import OdometryManager
from DirectNavigator import DirectNavigator
from AprilTagAligner import AprilTagAligner
from GameManager import GameManager
from CameraManager import CameraManager

# This should be False unless bench testing the raspberry pi.
networktablesserver = False   
serverlocation = '10.96.68.2'
serverlocation = '192.168.16.126'

testNavigatorObjective = (5,5)
testOrientation = 0
testAprilTagObjective = 1

        
# Main Loop
def main():

    # Initialize class instances
    ntinst = ntcore.NetworkTableInstance.getDefault()    
    if networktablesserver:
        ntinst.startServer()
    else:
        ntinst.startClient4("WestPi")
        ntinst.setServer(serverlocation)
    # ntinst.setServerTeam(9668)     
    GameTable = ntinst.getTable('GameManager')  
    camera = CameraManager()      
    odometry = OdometryManager.get_instance()
    navigator = DirectNavigator()
    april_tag_aligner = AprilTagAligner()  
    controller = NetworkController()
    

    navigator.navigate_to(testNavigatorObjective, testOrientation)

    print("Starting PID Test... ")
    # Enter main loop to run game logic
    while True:

        # Call periodic functions 
        camera.periodic()
        controller.periodic()        
        odometry.periodic()

        humandriver = GameTable.getBoolean("HumanDriver", True)
        
        # Let the human drive
        if humandriver:
            continue

        currentposition = odometry.get_position()
        currentorientation = odometry.get_orientation()

        navigator.navigate_from(currentposition, currentorientation)            

        # april_tag_aligner.align_to_tag(testAprilTagObjective, currentorientation)                 
        
        



if __name__ == "__main__":
    main()


