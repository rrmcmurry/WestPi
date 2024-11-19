from networktables import NetworkTables
import time
import keyboard

# Initialize NetworkTables connection
def initialize_networktables(server_ip='wpilibpi.local'):
    NetworkTables.initialize(server=server_ip)
    return NetworkTables.getTable("NetworkController"), NetworkTables.getTable("Pose"), NetworkTables.getTable("GameManager")

# Control robot movement with networkcontroller
def control_robot_with_pi(network_controller, robot_table, game_manager):
    x, y, z = 0.0, 0.0, 0.0  # Initial position: x, y, z
    step = 0.1  # Step size for position change
    rotation_step = 5  # Step size for orientation change

     

    try:
        while True:
            leftJoyX = network_controller.getNumber("leftJoyX", 0.0)
            leftJoyY = network_controller.getNumber("leftJoyY", 0.0)
            rightJoyX = network_controller.getNumber("rightJoyX", 0.0)
            action = game_manager.getString("Action","none")

            if action != "navigate":
                continue
            
            
            # Detect key presses and update values
            if leftJoyY > 0:
                x += step
            if leftJoyY < 0:
                x -= step
            if leftJoyX > 0:
                y += step
            if leftJoyX < 0:
                y -= step
            if rightJoyX > 0:
                z += rotation_step
            if rightJoyX < 0:
                z -= rotation_step

            # Wrap angle to 0-360 degrees
            z %= 360

            # Update the NetworkTables with the robot's position
            robot_table.putNumber("X", x)
            robot_table.putNumber("Y", y)
            robot_table.putNumber("Z", z)

            # Print for debugging
            # print(f"Position -> X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}")

            time.sleep(0.3)  # Update every 100ms
    except KeyboardInterrupt:
        print("\nSimulation stopped.")

if __name__ == "__main__":
    
    network_controller, robot_table, game_manager = initialize_networktables('wpilibpi.local')
    print("Connected to NetworkTables server. Use arrow keys to control position and 'A'/'D' to rotate.")
    control_robot_with_pi(network_controller, robot_table, game_manager)
