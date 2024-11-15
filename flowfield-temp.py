import math

class FlowField:
    def __init__(self, width, height, goal_x, goal_y):
        self.width = width
        self.height = height
        self.cost_field = [[99 for _ in range(width)] for _ in range(height)]
        self.cost_field[goal_y-1][goal_x-1] = 0
        self.spread_costs_from_goal(goal_x, goal_y)

    def spread_costs_from_goal(self, goal_x, goal_y):
        for distance in range(1, max(self.width, self.height)):
            for y in range(self.height):
                for x in range(self.width):
                    if self.cost_field[y][x] == distance - 1:
                        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < self.height and 0 <= nx < self.width:
                                if self.cost_field[ny][nx] > distance:
                                    self.cost_field[ny][nx] = distance


    def add_obstacle(self, start_x, start_y, obstacle_width, obstacle_height):
        for y in range(start_y-1, start_y + obstacle_height-1):
            for x in range(start_x-1, start_x + obstacle_width-1):
                self.cost_field[y][x] = 99

    def print_flowfield(self):
        # Format and print the cost field as a grid
        for row in self.cost_field:
            print(" ".join(f"{cell:2}" for cell in row))

    # Calculate the best direction in degrees
    def getdirections(self, current_x, current_y):
        current_x = current_x-1
        current_y = current_y-1
        vectors = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        weights = []

        
        # Check all 8 neighbors (including diagonals)
        for dy, dx in directions:
            neighbor_x = current_x + dx
            neighbor_y = current_y + dy

            # Only calculate if within bounds
            if 0 <= neighbor_x < self.width and 0 <= neighbor_y < self.height:
                cost = self.cost_field[neighbor_y][neighbor_x]
                if cost == 99:
                    continue

                weight = 1 / cost if cost != 0 else 1  # Inverse of cost, lower cost = stronger pull
                angle = math.atan2(dy, dx)  # Angle in radians
                angleindegrees = math.degrees(angle)
                # print(f"{neighbor_x},{neighbor_y}:{cost}:{angleindegrees}{weight}")
                
                # Store the weighted vector (angle and weight)
                weights.append((math.cos(angle) * weight, math.sin(angle) * weight))

        # Sum the weighted vectors
        sum_x = sum(v[0] for v in weights)
        sum_y = sum(v[1] for v in weights)

        
        # Calculate the resultant angle
        resultant_angle = math.atan2(sum_y, sum_x)  # Angle in radians

        # Convert to degrees (0 degrees is north)
        degrees = math.degrees(resultant_angle)
        return (degrees + 360) % 360  # Ensure the angle is between 0 and 360 degrees



centerField = FlowField(21,21,11,11)
centerField.add_obstacle(14,5,4,3)
centerField.print_flowfield()


currentx = 14
currenty = 4

direction = centerField.getdirections(currentx,currenty)


print(f"From {currentx},{currenty} you want to move in {direction} degrees")

