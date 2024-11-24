
import ntcore # type: ignore
import time
from NetworkController import NetworkController
from OdometryManager import OdometryManager
from DirectNavigator import DirectNavigator
from AprilTagAligner import AprilTagAligner
from GameManager import GameManager
from CameraManager import CameraManager

# This should be False unless bench testing the raspberry pi.
networktablesserver = True   

# Set game objectives here.
gameobjectives = [
    {"action": "navigate", "target": (11, 7), "orientation": 270}, 
    {"action": "wait", "duration": 3},     
    {"action": "navigate", "target": (8, 5), "orientation": 90},
    {"action": "wait", "duration": 3},     
    {"action": "navigate", "target": (0, 5), "orientation": 0}, 
    {"action": "wait", "duration": 3},
    {"action": "align", "tag_id": 1}
]
    
        
# Main Loop
def main():

    # Initialize class instances
    ntinst = ntcore.NetworkTableInstance.getDefault()    
    if networktablesserver:
        ntinst.startServer()
    else:
        ntinst.startClient4("10.96.68.2")
    ntinst.setServerTeam(9668)     
    game_manager = GameManager(gameobjectives)  
    camera = CameraManager()      
    odometry = OdometryManager.get_instance()
    navigator = DirectNavigator()
    april_tag_aligner = AprilTagAligner()  
    controller = NetworkController()
    

    print("Entering game logic")
    # Enter main loop to run game logic
    while True:

        # Call periodic functions 
        camera.periodic()
        controller.periodic()        
        odometry.periodic()
        
        # Get our current objective from the game manager
        objective = game_manager.get_current_objective()
        newobjective = game_manager.objectivechanged()

        # If navigating
        if objective["action"] == "navigate":
            # On first round, set targets
            if newobjective:
                navigator.navigate_to(objective["target"], objective["orientation"])
                
            # Navigate from current position until on target 
            ontarget = navigator.navigate_from(odometry.get_position(), odometry.get_orientation())            
            if ontarget:                 
                game_manager.advance_stage()

        # If aligning 
        elif objective["action"] == "align":
            aligned = april_tag_aligner.align_to_tag(objective["tag_id"], odometry.get_orientation())                 
            if aligned:
                game_manager.advance_stage()

        # If waiting
        elif objective["action"] == "wait":            
            if newobjective:                
                controller.reset                   
            elapsed_time = time.time() - game_manager.stage_start_time            
            if elapsed_time >= objective["duration"]:            
                game_manager.advance_stage()
        
        



if __name__ == "__main__":
    main()


