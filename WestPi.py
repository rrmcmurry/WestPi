
import ntcore # type: ignore
import time
from NetworkController import NetworkController
from OdometryManager import OdometryManager
from DirectNavigator import DirectNavigator
from AprilTagAligner import AprilTagAligner
from GameManager import GameManager
from CameraManager import CameraManager

serverlocation = '10.96.68.2'
serverlocation = 'localhost'

# Default startup game objectives
autonomousobjectives = [
    {"action": "wait", "duration": 1}
]
    
        
# Main Loop
def main():

    # Initialize class instances
    ntinst = ntcore.NetworkTableInstance.getDefault()    
    ntinst.startClient4("WestPi")
    ntinst.setServer(serverlocation)
    ntinst.setServerTeam(9668)     
    game_manager = GameManager(autonomousobjectives)  
    # camera = CameraManager()      
    odometry = OdometryManager.get_instance()
    navigator = DirectNavigator()
    april_tag_aligner = AprilTagAligner()  
    controller = NetworkController()
    

    print("Entering game logic")
    # Enter main loop to run game logic
    while True:

        # Call periodic functions 
        # camera.periodic()
        controller.periodic()        
        odometry.periodic()
        
        # Get our current objective from the game manager
        objective = game_manager.get_current_objective()
        newobjective = game_manager.objective_has_changed()

        # Let the human drive
        if game_manager.humandriver:
            continue

        # If navigating
        elif objective["action"] == "navigate":
            # On first round, set targets
            if newobjective:
                navigator.navigate_to(objective["target"], objective["orientation"])
                
            # Navigate from current position until on target 
            ontarget = navigator.navigate_from(odometry.get_position(), odometry.get_orientation())            
            if ontarget:                 
                game_manager.advance_stage()

        # If passthrough
        elif objective["action"] == "passthrough":
            if newobjective:
                navigator.set_passthrough(objective["path"])
            passedthrough = navigator.passthrough(odometry.get_position())
            if passedthrough:
                game_manager.advance_stage()

        # If aligning 
        elif objective["action"] == "align":
            # aligned = april_tag_aligner.align_to_tag(objective["tag_id"], odometry.get_orientation())
            aligned = True
            if aligned:
                game_manager.advance_stage()

        # If waiting
        elif objective["action"] == "waitfortime":            
            if newobjective:                
                controller.reset()  
            time.sleep(1)
            elapsed_time = time.time() - game_manager.stage_start_time            
            if elapsed_time >= objective["duration"]:            
                game_manager.advance_stage()

        elif objective["action"] == "wait":            
            if newobjective:                
                controller.reset()  
            time.sleep(1)
            
        
         # If waiting
        elif objective["action"] == "stop":            
            controller.reset()  
            game_manager.stop()

        time.sleep(0.01)


if __name__ == "__main__":
    main()


