import numpy as np
import serial

class Robot(object):
    def __init__(self, l1, l2, l3, momentum=0.9):
        self.l1 = l1
        self.l2 = l2
        self.l3 = l3
        self.momentum = momentum
        self.connec = None
        self.prev_state = None

    def __enter__(self, port):
        """Opens serial connection to robot"""
        self.connec = serial.Serial(port, baudrate=9600)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes serial connection to robot"""
        self.connec.close()

    def ramp(self, prev, pos):
        """
        Calculates the next position of the robot using momentum
        
        Args:
            prev (np.array): previous position
            pos (np.array): desired position
            
        Returns:
            np.array: next position
        """
        return prev + self.momentum*(pos - prev)

    def rik(self, l1, l2, xd):
        """
        Solves inverse kinematics for robot from world coordinates to joint angles
        https://motion.cs.illinois.edu/RoboticSystems/InverseKinematics.html

        Args:
            l1 (float): length of first link
            l2 (float): length of second link
            xd (np.array): world coordinates (x, y)

        Returns:
            dict: solutions for joint angles (q1, q2)
        """
        c2 = (np.linalg.norm(xd)**2 - l1**2 - l2**2)/(2*l1*l2)
        ret = {}
        if c2 > 1:
            ret["0"] = np.arrary([np.inf, np.inf])
        elif c2 == 1:
            ret["1"] = np.arrary([np.arctan2(xd[1], xd[0]), 0])
        elif c2 == -1:
            ret["1"] = np.array([np.arctan2(xd[1], xd[0]), np.pi])
        else:
            q21, q22 = np.arcos(c2), -np.arccos(c2)
            theta = np.arctan2(xd[1], xd[0])
            q11 = theta - np.arctan2(l2*np.sin(q21), l1 + l2*np.cos(q21))
            q12 = theta - np.arctan2(l2*np.sin(q22), l1 + l2*np.cos(q22))
            ret["1"] = np.array([q11, q21])
            ret["2"] = np.array([q12, q22])
        return ret

    def world2joint(self, xd):
        """
        Converts world coordinates to joint angles

        Args:
            xd (np.array): world coordinates (x, y, z)

        Returns:
            np.array: joint angles (q1, q2, q3)
        """
        sols = self.rik(self.l2, self.l3, (np.sqrt(xd[0]**2 + xd[1]**2), -xd[2]+self.l1))
        q1 = np.atan2(xd[1], xd[0])
        q2 = sols["1"][0]
        q3 = sols["1"][1]
        return np.array([q1, q2, q3])
    
    def move(self, xd):
        """
        Moves the robot to the desired world coordinates

        Args:
            xd (np.array): world coordinates (x, y, z)
        """
        q = list(self.world2joint(xd))
        if not self.prev_state:
            self.prev_state = q
        self.prev_state = self.ramp(self.prev_state, q)
        data = ",".join(map(str, self.prev_state)) + "\n"
        self.connec.write(data.encode())