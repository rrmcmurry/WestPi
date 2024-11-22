
import ntcore      

# A class for tracking current position
class OdometryManager:
    _instance = None

    @staticmethod
    def get_instance():
        if OdometryManager._instance is None:
            OdometryManager()
        return OdometryManager._instance

    def __init__(self):
        if OdometryManager._instance is not None:
            raise Exception("This class is a singleton!")
        OdometryManager._instance = self

        # Initialize NetworkTables and the Pose table
        ntinst = ntcore.NetworkTableInstance.getDefault()
        self.pose_table = ntinst.getTable("Pose")

        # Default position and orientation
        self.current_position = (0.0, 0.0)  # X, Y coordinates
        self.current_orientation = 0.0     # Z orientation (angle in degrees or radians)

    def periodic(self):
        """Fetch the latest position and orientation from the NetworkTables Pose table."""
        x = self.pose_table.getNumber("X", 0.0)
        y = self.pose_table.getNumber("Y", 0.0)
        z = self.pose_table.getNumber("Z", 0.0)

        self.current_position = (x, y)
        self.current_orientation = z

    def get_position(self):
        """Return the current X, Y coordinates."""
        return self.current_position

    def get_orientation(self):
        """Return the current orientation (Z value)."""
        return self.current_orientation

    def adjust_for_error(self, correction):
        """
        Apply a correction to the position.
        :param correction: Tuple (dx, dy, dz) for X, Y, and orientation corrections.
        """
        dx, dy, dz = correction
        x, y = self.current_position
        self.current_position = (x + dx, y + dy)
        self.current_orientation += dz

