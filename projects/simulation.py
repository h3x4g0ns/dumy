from matplotlib import pyplot as plt
from lib.hardware.robot import Robot
import numpy as np

# testing out inverse kinematics
l1 = 3
l2 = 3
l3 = 1

with Robot(l1, l2, l3, None) as dumy:
    q2 = np.arange(-np.pi/2, np.pi/2, 0.1)
    q3 = np.arange(-np.pi/2, np.pi/2, 0.1)
    for x, y in zip(q2, q3):
        q = np.array([0, x, y])
        xd = dumy.joint2world(q)
        if not np.isnan(xd[0]):
            plt.plot(xd[0], xd[2], 'b.', label="world")
            # plt.plot(q[1], q[2], 'r.', label="joint")
    plt.show()
