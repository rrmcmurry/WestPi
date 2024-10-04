class FlowField:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cost_field = [[9999 for _ in range(width)] for _ in range(height)]  # Initialize with high cost
        self.initialize_cost_field()

    # Initialize the cost field with a goal and spreading costs
    def initialize_cost_field(self):
        # Set the goal's position (e.g., bottom-right corner)
        goal_x, goal_y = self.width - 1, self.height - 1
        self.cost_field[goal_y][goal_x] = 0

        # Spread costs from the goal
        self.spread_costs_from_goal(goal_x, goal_y)

    # Spread costs from the goal using Manhattan distance
    def spread_costs_from_goal(self, goal_x, goal_y):
        for distance in range(1, max(self.width, self.height)):
            for y in range(self.height):
                for x in range(self.width):
                    cost = abs(goal_x - x) + abs(goal_y - y)  # Manhattan distance
                    if self.cost_field[y][x] > cost:
                        self.cost_field[y][x] = cost

    # Add a static obstacle by marking cells with a high cost
    def add_obstacle(self, start_x, start_y, obstacle_width, obstacle_height):
        for y in range(start_y, start_y + obstacle_height):
            for x in range(start_x, start_x + obstacle_width):
                self.cost_field[y][x] = 9999  # High cost for obstacles

    # Display the cost field (for debugging)
    def print_cost_field(self):
        for row in self.cost_field:
            print(" ".join(f"{cell:4}" for cell in row))

    # Determine the best direction to move based on the current position
    def get_best_direction(self, current_x, current_y):
        best_cost = 9999
        best_direction = None

        # Check all 4 possible directions (up, down, left, right)
        if current_y > 0 and self.cost_field[current_y - 1][current_x] < best_cost:
            best_cost = self.cost_field[current_y - 1][current_x]
            best_direction = "up"
        if current_y < self.height - 1 and self.cost_field[current_y + 1][current_x] < best_cost:
            best_cost = self.cost_field[current_y + 1][current_x]
            best_direction = "down"
        if current_x > 0 and self.cost_field[current_y][current_x - 1] < best_cost:
            best_cost = self.cost_field[current_y][current_x - 1]
            best_direction = "left"
        if current_x < self.width - 1 and self.cost_field[current_y][current_x + 1] < best_cost:
            best_cost = self.cost_field[current_y][current_x + 1]
            best_direction = "right"

        return best_direction

    
field = FlowField(20, 10)  # 20x10 grid
field.add_obstacle(9, 4, 2, 2)  # Add 2x2 obstacle in the center
field.print_cost_field()  # Print the field for debugging

current_x, current_y = 0, 0  # Robot's current position
direction = field.get_best_direction(current_x, current_y)
print(f"Move {direction}")
