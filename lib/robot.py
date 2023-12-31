import numpy as np
import serial
from time import sleep

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
    
    def endEffectorToWorld(self, baseAngle, endToFloor):
        """
        Given end effector coordinates, length of arm 2, and end effector to floor distance,
        we want to project the end effector onto the floor and then calculate the world 
        coordinates of the end effector.
        """

        #translate from 3d coords to uv
        U = np.dot(np.array((0,0,1)), np.dot(np.linalg.norm(endToFloor), np.array((0,0,1))))
        V = np.dot(U, np.linalg.norm(endToFloor))

        M = np.dot(np.linalg.inv(np.array([[0, U[0], V[0], endToFloor[0]],
                                    [0, U[1], V[1], endToFloor[1]],
                                    [1, U[2], V[2], endToFloor[2]],
                                    [1, 1, 1, 1]])), 
                                    np.array([[0,1,0,0],
                                              [0,0,1,0],
                                              [0,0,0,1],
                                              [1,1,1,1]]))
        
        coord2D = np.dot(M, endToFloor)

        x_c, z_c = (0, 0)
        x_t, z_t = coord2D[0], coord2D[1]

        # Assuming baseAngle is the angle at which the base of the robotic arm is rotated
        # Assuming the rotation is around the z-axis
        rotation_matrix = np.array([[np.cos(baseAngle), -np.sin(baseAngle), 0],
                                    [np.sin(baseAngle), np.cos(baseAngle), 0],
                                    [0, 0, 1]])

        # Distance from circle center to the point on the tangent line
        # Length from the tangent point to the point on the tangent line
        # Ratio to find the tangent point
        dist = np.sqrt((x_t - x_c)**2 + (z_t - z_c)**2)
        l = np.sqrt(dist**2 - self.l1**2)
        ratio = l / dist

        # Coordinates of the tangent point
        x = x_c + ratio * (x_t - x_c)
        z = z_c + ratio * (z_t - z_c)

        #translate back into 3d coords
        res = np.dot(np.linalg.inv(M), np.array((x,z)))
        return res

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
        if np.abs(c2) > 1:
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
        q1 = np.rad2deg(np.arctan2(xd[1], xd[0]))
        q2 = np.rad2deg(sols[key][0])
        q3 = np.rad2deg(sols[key][1])
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
        if self.prev_state is None:
            self.prev_state = q
        self.prev_state = self.ramp(self.prev_state, q)
        data = ",".join(map(str, q)) + "r"
        self.connec.write(data.encode())
        print(data)
        return True

    def move_base(self, xd):
        """
        Moves base of the robot given a destination coordinate

        Args:
            xd (np.array): world coordinates (x, y, z)
        """
        q = np.arctan2(xd[1], xd[0])/np.pi*180
        q = str(int(q)) + ",0,0r"
        print("moving", q)
        self.connec.write(q.encode())

# Rough Measurements from arm:
# l1 = 4.13cm
# l2 = 12cm
# l3 = 12cm

class Dumy(Robot):
    def __init__(self, port):
        """Configures 3DOF robot for Dummy"""
        super().__init__(l1=4.13, l2=12, l3=12, port=port)

if __name__ == "__main__":
    port = "COM3"
    coords = [0, -90, 0, 90, 0]
    with Dummy(port) as d:
        for coord in coords:
            d.move_base(coord)
            sleep(1)
