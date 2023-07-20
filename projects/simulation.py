from matplotlib import pyplot as plt
from lib.robot import Robot
import numpy as np

# testing out inverse kinematics
l1 = 3
l2 = 3
l3 = 1

with Robot(l1, l2, l3, None) as dumy:
    X = np.arange(-4, 4, 0.1)
    Y = np.arange(-4, 4, 0.1)
    for x, y in zip(X, Y):
      xd = np.array([x, y, 0.5])
      q = dumy.world2joint(xd)
      if not np.isnan(q[0]):
          plt.plot(x, y, 'b.', label="world")
          plt.plot(q[1], q[2], 'r.', label="joint")
    plt.show()