# dumy

Control a 3/4 DOF robot arm to track a cat and constantly play laser pointer fetch with her.

## design

- We will have the server code running on a Jetson that will capture the environment through a camera.
- We want to perform our computations give the environment to control the world coordinates of the robot.
- We will then want to pass in the new joint angles into a serial port on the RP2040 which is connected to the laser pointer arm.
- This will move the robot arm accordingly.

**Vision Stack**

- We want to be able to track a bounding box over the moving cat.
  - Use something like PyTorch YOLOv5 to get bounding box over entities measured at cat
- We also want to be able to track the laser pointer.
  - Since we know that the laser pointer is a red dot, use image constrasting to get coordinate of the red most point
- We want to constantly move the laser pointer such that it's moving away from the cat.
- We can use the trajectory of the cat as a hueristic to determine where the cat will be headed.

**Control Stack**

- We need calculate the world coordinate of the robot
  - Given goal coordinates we can solve analytical inverse kinematics to ascertain joint angles
- Pass in joint coordinates to RP2040 for control through serial communication
  - Server code runs on jetson and will connect to RP2040 with USB-C cable

## notes

MiDaS Model: v3.0 DPTL-384
dpt_large_384