import ntcore
import time
import json

# A class for defining the stages of the game and the objectives in that stage
class GameManager:
    def __init__(self, gameobjectives):
        self.ntinst = ntcore.NetworkTableInstance.getDefault()            
        self.GameTable = self.ntinst.getTable('GameManager') 
        self.ObjectiveTable = self.ntinst.getTable('Objectives')
        self.objectivechanged = True
        self.stage = 0
        self.stage_start_time = time.time()
        self.objectives = gameobjectives
        self.print_current_objective()
        self.GameTable.putNumber('Stage', 0.0)

    def get_current_objective(self): 
        self.periodic()
        return self.objectives[self.stage]
    


    def print_current_objective(self):
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
        if len(self.objectives) == 1 and self.stage == 1:
            self.objectives = [{"action": "wait", "duration": 3}]
        if self.stage >= len(self.objectives):
            self.stage = 0   

        self.objectivechanged = True
        self.stage_start_time = time.time()
        print(f"Advancing to stage {self.stage}")
        self.print_current_objective()

    def stop(self):
        self.objectives = [{"action": "wait", "duration": 3}]
        self.stage = 0

    def objective_has_changed(self):
        changed = self.objectivechanged
        self.objectivechanged = False
        return changed

    def periodic(self):        
        # Check if a new set of objectives has been provided by FieldCommander
        self.humandriver = self.GameTable.getBoolean("HumanDriver", False)
        objectives_json = self.ObjectiveTable.getString("NewObjectives", "")
        if objectives_json:
            try:
                new_objectives = json.loads(objectives_json)
                
                # Overwrite or extend objectives
                overwrite = self.ObjectiveTable.getBoolean("Overwrite", True)
                if overwrite:
                    # Overwrite objectives and reset to the first stage
                    print(f"Current Objectives: {self.objectives}")
                    print(f"New Objectives: {new_objectives}")
                    self.objectives = new_objectives
                    self.stage = 0  
                    self.stage_start_time = time.time()
                else:
                    self.objectives.extend(new_objectives)
                
                # Fallback to wait if the objectives are empty
                if not self.objectives:
                    self.objectives = [{"action": "wait", "duration": 3}]
                
                # Reset action 
                self.objectivechanged = True

                # Clear the input
                self.ObjectiveTable.putString("NewObjectives", "")  
                print("Objectives updated from NetworkTables.")
            except Exception as e:
                print(f"Failed to parse objectives: {e}")
