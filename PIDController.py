import math

class PIDController:
    def __init__(self, kp, ki, kd, outputrange=(-1,1)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0
        self.min, self.max = outputrange

    def compute(self, setpoint, measured_value):
        error = setpoint - measured_value
        self.integral += error
        derivative = error - self.prev_error
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        output = max(self.min, min(self.max, output))
        return output

class AnglePIDController:
    def __init__(self, kp, ki, kd, outputrange=(-1, 1)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min, self.max = outputrange
        self.prev_error = 0
        self.integral = 0

    def compute(self, target_angle, current_angle):        
        error = ((target_angle - current_angle + 180) % 360) - 180
        self.integral += error
        derivative = error - self.prev_error
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        output = max(self.min, min(self.max, -output))
        return output