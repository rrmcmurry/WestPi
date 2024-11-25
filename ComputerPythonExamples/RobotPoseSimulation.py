from networktables import NetworkTables
import time
import pygame

# Initialize NetworkTables connection
def initialize_networktables(server_ip='wpilibpi.local'):
    NetworkTables.initialize(server=server_ip)
    return NetworkTables.getTable("NetworkController"), NetworkTables.getTable("Pose"), NetworkTables.getTable("GameManager")


def deadband(value, deadband=0.05):
    """Apply deadband to joystick axis value."""
    if abs(value) < deadband:
        return 0.0
    return value

def simulate_robot(network_controller, pose, xbox_controller=None):
    step = 0.5  # Step size for position change
    rotation_step = 5  # Step size for orientation change

    # Default to NetworkController inputs
    leftJoyX = network_controller.getNumber("leftJoyX", 0.0)
    leftJoyY = network_controller.getNumber("leftJoyY", 0.0)
    rightJoyX = network_controller.getNumber("rightJoyX", 0.0)

    # Override with XboxController inputs if available
    if xbox_controller:
        pygame.event.pump()  # Process events
        leftJoyX = deadband(xbox_controller.get_axis(0), 0.05) or leftJoyX
        leftJoyY = deadband(xbox_controller.get_axis(1), 0.05) or leftJoyY
        rightJoyX = deadband(xbox_controller.get_axis(4), 0.05) or rightJoyX

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


# Main simulation loop
def main():
    networkcontroller, pose, gamemanager = initialize_networktables()
    isconnected = False

    # Initialize XboxController if available
    pygame.init()
    xbox_controller = None
    if pygame.joystick.get_count() > 0:
        xbox_controller = pygame.joystick.Joystick(0)
        xbox_controller.init()

    while True:
        status = NetworkTables.isConnected()
        if status != isconnected:
            isconnected = status
            if isconnected:
                print("Connected")
            else:
                print("Connection lost.")
                time.sleep(10)
                print("Reconnecting...")
                networkcontroller, pose, gamemanager = initialize_networktables()
                continue

        action = gamemanager.getString("Action", "none")

        if action == "navigate":
            simulate_robot(networkcontroller, pose, xbox_controller)

        time.sleep(0.1)  # Update every 100ms

if __name__ == "__main__":
    main()
