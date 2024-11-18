from networktables import NetworkTables
import time
import keyboard

# Initialize NetworkTables connection
def initialize_networktables(server_ip='wpilibpi.local'):
    NetworkTables.initialize(server=server_ip)
    return NetworkTables.getTable("Pose")

# Control robot movement with keyboard
def control_robot_with_keyboard(robot_table):
    x, y, z = 0.0, 0.0, 0.0  # Initial position: x, y, orientation (theta in degrees)
    step = 0.1  # Step size for position change
    rotation_step = 5.0  # Step size for orientation change

    try:
        while True:
            # Detect key presses and update values
            if keyboard.is_pressed("up"):
                x += step
            if keyboard.is_pressed("down"):
                x -= step
            if keyboard.is_pressed("left"):
                y -= step
            if keyboard.is_pressed("right"):
                y += step
            if keyboard.is_pressed("a"):
                z -= rotation_step
            if keyboard.is_pressed("d"):
                z += rotation_step

            # Wrap theta to 0-360 degrees
            z %= 360

            # Update the NetworkTables with the robot's position
            robot_table.putNumber("X", x)
            robot_table.putNumber("Y", y)
            robot_table.putNumber("Z", z)

            # Print for debugging
            # print(f"Position -> X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}")

            time.sleep(0.1)  # Update every 100ms
    except KeyboardInterrupt:
        print("\nSimulation stopped.")

if __name__ == "__main__":
    
    robot_table = initialize_networktables('wpilibpi.local')
    print("Connected to NetworkTables server. Use arrow keys to control position and 'A'/'D' to rotate.")
    control_robot_with_keyboard(robot_table)
