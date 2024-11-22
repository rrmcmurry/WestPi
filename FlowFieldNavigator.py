import math
from NetworkController import NetworkController

# A class for defining a field with obstacles that can give directions
class FlowFieldNavigator:
    def __init__(self):
        self.controller = NetworkController()


    def spread_costs_from_goal(self, goal_x, goal_y):
        for distance in range(1, max(self.width, self.height)):
            for y in range(self.height):
                for x in range(self.width):
                    if self.cost_field[y][x] == distance - 1:
                        for dy, dx in [(-1, 0), (-1,-1), (0,-1), (1,-1), (1, 0), (1, 1), (0, 1), (-1,1)]:
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < self.height and 0 <= nx < self.width:
                                if self.cost_field[ny][nx] > distance:
                                    self.cost_field[ny][nx] = distance


    def generate_flowfield(self, goal, orientation):
        self.goal_x, self.goal_y = goal
        self.goal_z = orientation
        self.width = 21
        self.height = 12
        self.cost_field = [[99 for _ in range(self.width)] for _ in range(self.height)]
        self.cost_field[self.goal_y][self.goal_x] = 0
        self.spread_costs_from_goal(self.goal_x, self.goal_y)
        # self.add_obstacle(10,5,2,2) # a 2x2 block right in the middle 
        # self.print_flowfield()
        
     
    def add_obstacle(self, start_x, start_y, obstacle_width, obstacle_height):
        for y in range(start_y, start_y + obstacle_height):
            for x in range(start_x, start_x + obstacle_width):
                self.cost_field[y][x] = 99

    def print_flowfield(self):
        # Format and print the cost field as a grid
        formatted_rows = []
        for row in self.cost_field:
            formatted_row = " ".join(f"{cell:2}" for cell in row).strip()
            formatted_rows.append(formatted_row)
            print(formatted_row)

    def aligned_to_target(self, currentorientation):
        aligned = False
        targetorientation = self.goal_z 
        
        
        # Force our angle values to be between 0 and 360
        targetorientation = targetorientation % 360
        currentorientation = currentorientation % 360

        # Calculate the angular difference
        outofalignment = (targetorientation - currentorientation + 180) % 360 -180

        # Check alignment threshhold
        if abs(outofalignment) > 5:             
            z = -(outofalignment / abs(outofalignment)) * 0.3 # Limit our speed to -0.3 or +0.3        
        else:
            z = 0
            aligned = True
 
        self.controller.setRightJoyX(z)
        return aligned

    # Calculate the best direction in degrees
    def get_directions(self, current_position, current_alignment):
        current_x_float, current_y_float = current_position

        # Adjusting for the zero based table and rounding to an integer
        current_x = round(current_x_float)
        current_y = round(current_y_float)        

        ontarget = False

        aligned = self.aligned_to_target(current_alignment)

        if current_x == self.goal_x and current_y == self.goal_y:
            ontarget = True
        

        # A set of directions for neighboring cells
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        # An array to store x and y values multiplied by their cost
        weights = []

        # Check all 8 neighbors (including diagonals)
        for dy, dx in directions:
            neighbor_x = current_x + dx
            neighbor_y = current_y + dy

            # Only calculate if within bounds
            if 0 <= neighbor_x < self.width and 0 <= neighbor_y < self.height:
                # Grab the cost of this field
                cost = self.cost_field[neighbor_y][neighbor_x]
                # Skip it if the cost is 99
                #if cost == 99:
                #    continue

                # Weight is the inverse of cost, lower cost = stronger pull
                weight = 1 / cost if cost != 0 else 1  

                # Convert direction into an angle in radians
                angle = math.atan2(dy, dx)  

                # Store the weighted vector (angle and weight)
                """ x value = math.cos(angle) """
                """ y value = math.sin(angle) """
                """ Weighted x value = math.cos(angle) * weight """
                """ Weighted y value = math.sin(angle) * weight """
                weights.append((math.cos(angle) * weight, math.sin(angle) * weight))

        # Add up the weighted vectors
        sum_x = sum(v[0] for v in weights)
        sum_y = sum(v[1] for v in weights)

        # Convert this to an angle in Radians
        resultant_angle = math.atan2(sum_y, sum_x)  

        # Use resulting angle to calculate controller values between -1 and 1
        forward = math.cos(resultant_angle)
        strafe = math.sin(resultant_angle)

        forward = round(forward * 100)/100
        strafe = round(strafe * 100)/100

        # Set controller values
        # If you're on target, stop
        if ontarget and aligned:
            self.controller.stop()
        elif ontarget:
            self.controller.setLeftJoyY(0)
            self.controller.setLeftJoyX(0)
        # If you're outside of the field bring it back in the field
        elif 0 > current_x or current_x > self.width or 0 > current_y or current_y > self.height:
            if 0 > current_x or current_x > self.width:
                self.controller.setLeftJoyY((-current_x / current_x) * 0.3)
            if 0 > current_y or current_y > self.height:
                self.controller.setLeftJoyX((current_y / current_y) * 0.3)
        # Otherwise use the calculated values
        else:
            self.controller.setLeftJoyY(forward)
            self.controller.setLeftJoyX(strafe)
        
        

        return (ontarget and aligned)

