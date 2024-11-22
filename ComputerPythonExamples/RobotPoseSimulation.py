from networktables import NetworkTables
import time
import keyboard



# Initialize NetworkTables connection
def initialize_networktables(server_ip='wpilibpi.local'):
    NetworkTables.initialize(server=server_ip)
    return NetworkTables.getTable("NetworkController"), NetworkTables.getTable("Pose"), NetworkTables.getTable("GameManager")

# Control robot movement with networkcontroller
def control_robot_with_pi(network_controller, pose, game_manager):

    step = 0.5  # Step size for position change
    rotation_step = 1  # Step size for orientation change

    leftJoyX = network_controller.getNumber("leftJoyX", 0.0)
    leftJoyY = network_controller.getNumber("leftJoyY", 0.0)
    rightJoyX = network_controller.getNumber("rightJoyX", 0.0)
    action = game_manager.getString("Action","none")
    x = pose.getNumber("X",0)
    y = pose.getNumber("Y",0)
    z = pose.getNumber("Z",0)

    if action != "navigate":
        return

    x += leftJoyY * step
    y += leftJoyX * step
    z += -rightJoyX * rotation_step
    
    # Wrap angle to 0-360 degrees
    z %= 360          

    # Update the NetworkTables with the robot's position
    pose.putNumber("X", round(x,2))
    pose.putNumber("Y", round(y,2))
    pose.putNumber("Z", z)


    return
            
   

def main():
    networkcontroller, pose, gamemanager = initialize_networktables()
    isconnected = False

    while True:
        status = NetworkTables.isConnected()
        if status != isconnected:
            isconnected = status
            if isconnected:
                print("Connected")
            else:
                print("Connection lost. Reconnecting.")
                time.sleep(3)
                networkcontroller, pose, gamemanager = initialize_networktables()
    
        control_robot_with_pi(networkcontroller, pose, gamemanager)
        
        time.sleep(0.1)  # Update every 100ms
    
if __name__ == "__main__":
    main()

