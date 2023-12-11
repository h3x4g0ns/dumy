from sympy import symbols, cos, sin, pi, simplify, solve

# Define symbolic variables
# theta1, theta2, theta3 = symbols('theta1 theta2 theta3')

# Robot arm parameters (lengths of the links)
# L1, L2, L3 = symbols('L1 L2 L3')

class Trajectory:
    def __init__(self, robot):
        self.robot = robot
        self.l1 = robot.l1
        self.l2 = robot.l2
        self.l3 = robot.l3
        self.prev_cat_pos = None

    def trajectory_engine(self):
        # Forward kinematics equations (position of the end effector)
        x, y, z = self.robot.joint2world(self.robot.prev_state)
        desired_x, desired_y = self.robot.endEffectorToWorld()

        # Solve inverse kinematics equations to find joint angles
        inverse_kinematics_equations = [
            simplify(x - desired_x),
            simplify(y - desired_y)
        ]

        # Solve for joint angles
        solutions = solve(inverse_kinematics_equations, [self.l1, self.l2, self.l3])


def __main__():
    # read positions from the vision stack
    # while True:
    #     desired_x = 
    #     desired_y = 
    #     movement_angle = trajectory_engine(desired_x, desired_y)
    # 
    pass

