import numpy as np
from collections import queue

class Trajectory:
    def __init__(self, robot):
        self.robot = robot
        self.l1 = robot.l1
        self.l2 = robot.l2
        self.l3 = robot.l3
        self.prev_cat_pos = None
        self.queue = queue()

    def calculate(self, cat_pos):
        """
        Uses a few different methods to calculate the next position of the robot
        given the current position of the cat. We want to make sure we never blind
        the cat and that we are always moving away from the cat. We can use the 
        previous position of the cat to calculate the next position of the cat since
        we assume the cat travels in a line. We also want to activate taunting mode
        if the cat has not moved enough.

        Args:
            cat_pos (np.array): position of the cat

        Returns:
            np.array: next position of the robot
        """
        # Forward kinematics equations (position of the end effector)
        x, y, z = self.robot.joint2world(self.robot.prev_state)

        # find new desired laser pos
        laserPos = cat_pos + np.linalg.norm(cat_pos - self.prev_cat_pos)*20
        desired_x, desired_y, desired_z = self.robot.endEffectorToWorld(laserPos)

        # calculate cat activation
        if (self.queue.queueSize < 5):
            # send code for piezo buzzer
            self.queue = cat_pos + 10
            self.prev_cat_pos = cat_pos + 10
        elif np.abs(np.std(self.queue)) < 0.5:
            # send code for taunting
            self.prev_cat_pos = cat_pos
            self.queue.push(cat_pos)
            return np.asarray((0, 0, 0))
        else:
            self.prev_cat_pos = cat_pos
        
        # updating history
        if self.queue.queueSize >= 5:
            self.queue.pop()
            self.queue.push(cat_pos)

        # Solve for joint angles
        solution = self.robot.world2joint(np.asarray((desired_x, desired_y, desired_z)))
        return solution
