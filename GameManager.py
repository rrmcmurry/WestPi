import ntcore


# A class for defining the stages of the game and the objectives in that stage
class GameManager:
    def __init__(self, gameobjectives):
        self.ntinst = ntcore.NetworkTableInstance.getDefault()            
        self.GameTable = self.ntinst.getTable('GameManager') 
        self.objectivechanged = True
        self.stage = 0
        self.wait_start_time = None
        self.objectives = gameobjectives
        self.print_current_objective()
        self.GameTable.putNumber('Stage', 0.0)

    def get_current_objective(self):
        if self.stage < len(self.objectives):
            return self.objectives[self.stage]
        return None  # Game is complete
    
    def restart(self):
        self.stage = 0
        return

    def print_current_objective(self):
        if self.stage < len(self.objectives):
            self.GameTable.putNumber('Stage', self.stage)
            objective = self.objectives[self.stage]
            action = objective["action"]
            self.GameTable.putString("Action",action)     
            try:
                targetx, targety = objective["target"]
                targetorientation = objective["orientation"]
                self.GameTable.putString("Target",f"({targetx},{targety})")
                self.GameTable.putString("Target Orientation",f"{targetorientation} degrees")
            except:
                self.GameTable.putString("Target",f"None")
            try:
                targettag = objective["tag_id"]
                self.GameTable.putString("Target Apriltag", f"{targettag}")
            except:
                self.GameTable.putString("Target Apriltag", f"None")
            print(f"Objective: {self.objectives[self.stage]}")

    def advance_stage(self):        
        self.stage += 1
        if self.stage >= len(self.objectives):
            self.stage = 0
        self.objectivechanged = True
        self.wait_start_time = None 
        print(f"Advancing to stage {self.stage}")
        self.print_current_objective()
        
        
    def objective_has_changed(self):
        changed = self.objectivechanged
        self.objectivechanged = False
        return changed