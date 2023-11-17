import numpy as np
import serial

class Robot(object):
    """Robot class for controlling and defining robot arm"""
    def __init__(self, l1, l2, l3, port, momentum=0.9):
        self.l1 = l1
        self.l2 = l2
        self.l3 = l3
        self.port = port
        self.momentum = momentum
        self.connec = None
        self.prev_state = None

    def __enter__(self):
        """Opens serial connection to robot"""
        self.connec = serial.Serial(self.port, baudrate=9600)
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
        See: https://motion.cs.illinois.edu/RoboticSystems/InverseKinematics.html

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
            ret["0"] = np.array([np.nan, np.nan])
        elif c2 == 1:
            ret["1"] = np.array([np.arctan2(xd[1], xd[0]), 0])
        elif c2 == -1:
            ret["1"] = np.array([np.arctan2(xd[1], xd[0]), np.pi])
        else:
            q21 = np.arccos(c2)
            q22 = -np.arccos(c2)
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
        key = "1" if "1" in sols else "0"
        q1 = np.arctan2(xd[1], xd[0])
        q2 = sols[key][0]
        q3 = sols[key][1]
        return np.array([q1, q2, q3])

    def joint2world(self, q):
        """
        Converts joint angles to world coordinates

        Args:
            theta (np.array): joint angles (q1, q2, q3)

        Returns:
            np.array: world coordinates (x, y, z)
        """
        cq = np.cos(q)
        sq = np.sin(q)
        x = cq[0]*(cq[1]*(self.l2+cq[2]*self.l3)-sq[1]*sq[2]*self.l3)
        y = sq[0]*(cq[1]*(self.l2+cq[2]*self.l3)-sq[1]*sq[2]*self.l3)
        z = self.l1-sq[1]*(self.l2+cq[2]*self.l3)-cq[1]*sq[2]*self.l3
        return np.array([x, y, z])
    
    def move(self, xd):
        """
        Moves the robot to the desired world coordinates

        Args:
            xd (np.array): world coordinates (x, y, z)

        Returns:
            bool: True if successful, False otherwise
        """
        q = self.world2joint(xd)
        if np.isnan(q[0]) or np.isnan(q[1]) or np.isnan(q[2]):
            return False
        if not self.prev_state:
            self.prev_state = q
        self.prev_state = self.ramp(self.prev_state, q)
        data = ",".join(map(str, self.prev_state)) + "\n"
        self.connec.write(data.encode())
        print(data + "\n")
        return True

# Rough Measurements from arm:
# l1 = 4.13cm
# l2 = 12cm
# l3 = 12cm

class Dummy(Robot):
    def __init__(self, port):
        """Configures 3DOF robot for Dummy"""
        super().__init__(l1=4.13, l2=12, l3=12, port=port)

def main():
    port = "COM3"
    angles = np.array([[45,45,45],[0,0,0],[90,30,90],[0,45,90]])
    with Dummy(port) as d:
        for i in angles:
            xd = angles[i]
            d.move(xd)
            print("Moved to: " + xd)

if __name__ == "__main__":
    main()