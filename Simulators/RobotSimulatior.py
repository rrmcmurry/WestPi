import ntcore
import time
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

# Initialize NetworkTables connection
def initialize_networktables(server_ip='localhost'):
    """Initializing NetworkTables"""
    ntinst = ntcore.NetworkTableInstance.getDefault()      
    ntinst.setServer(server_ip)
    ntinst.startServer() 
    
    return ntinst.getTable("NetworkController"), ntinst.getTable("Pose"), ntinst.getTable("GameManager")


def deadband(value, deadband=0.05):
    """Apply deadband to joystick axis value."""
    if abs(value) < deadband:
        return 0.0
    return value

def simulate_robot(network_controller, pose, gamemanager, xbox_controller=None):
    step = 0.5  # Step size for position change
    rotation_step = 5  # Step size for orientation change

    HumanDriver = False

    # Default to NetworkController inputs
    leftJoyX = network_controller.getNumber("leftJoyX", 0.0) * 10
    leftJoyY = network_controller.getNumber("leftJoyY", 0.0) * 10
    rightJoyX = network_controller.getNumber("rightJoyX", 0.0) 


    

    # Override with XboxController inputs if available
    if xbox_controller:
        pygame.event.pump()  # Process events
        XBoxleftJoyX = deadband(xbox_controller.get_axis(0), 0.2) 
        XBoxleftJoyY = deadband(-xbox_controller.get_axis(1), 0.2) 
        XBoxrightJoyX = deadband(xbox_controller.get_axis(2), 0.2)

        if XBoxleftJoyX or XBoxleftJoyY or XBoxrightJoyX:
            HumanDriver = True
            leftJoyX = XBoxleftJoyX
            leftJoyY = XBoxleftJoyY
            rightJoyX = XBoxrightJoyX

    gamemanager.putBoolean("HumanDriver", HumanDriver)
    

    # Update position based on inputs
    x = pose.getNumber("X", 0)
    y = pose.getNumber("Y", 0)
    z = pose.getNumber("Z", 0)

    x += leftJoyY * step
    y += leftJoyX * step
    z += -rightJoyX * rotation_step

    # Wrap angle to 0-360 degrees
    z %= 360

    # Update the NetworkTables with the robot's position
    pose.putNumber("X", round(x, 2))
    pose.putNumber("Y", round(y, 2))
    pose.putNumber("Z", z)


# Main loop
def main():
    # Initializing
    networkcontroller, pose, gamemanager = initialize_networktables()
    pygame.init()
    xbox_controller = None
    if pygame.joystick.get_count() > 0:        
        xbox_controller = pygame.joystick.Joystick(0)
        xbox_controller.init()

    # Running
    print("Simulation running...")
    while True:
        simulate_robot(networkcontroller, pose, gamemanager, xbox_controller)
        time.sleep(0.1)  # Update every 100ms

if __name__ == "__main__":
    main()
