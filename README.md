# dumy

Control a 3/4 DOF robot arm to track a cat and constantly play laser pointer fetch with her

## design

- We will have the server code running on a Jetson that will capture the environment through a camera
- We want to perform our computations given the environment to control the world coordinates of the robot
- We will then want to pass in the new joint angles into a serial port on the RP2040 which is connected to the laser pointer arm
- This will move the robot arm accordingly so it's always stimulating the cat

**Vision Stack**

- We want to be able to track a bounding box over the moving cat
  - Use something like PyTorch YOLOv5 to get bounding box over entity identified as cat
    - We can use the center point of the cat
    - OR we can find point on boundary of bounding box closest to the laser pointer
- We also want to be able to track the laser pointer
  - Since we know that the laser pointer is a red dot, use image constrasting to get coordinate of the red-most point
- We want to constantly move the laser pointer such that it's moving away from the cat
  - Cat shoudld never catch the laser pointer
  - If we detect that cat has stopped chasing it, we should taunt the cat by moving the pointer in front of cat
- We can use the trajectory of the cat as a hueristic to determine where the cat will be headed

**Control Stack**

- We need calculate the world coordinate of the robot
  - Given goal coordinates we can solve analytical inverse kinematics to ascertain joint angles
- Pass in joint angles to RP2040 for control through serial communication
  - Server code runs on jetson and will connect to RP2040 with USB-C cable

## setup

First installing pico sdk.

```sh
cd ~
git clone -b master https://github.com/raspberrypi/pico-sdk.git
cd pico-sdk
git submodule update --init
```

Add following line to `.bashrc` or `.zshrc`.

```sh
export PICO_SDK=~/pico-sdk
```

Install toolchain for Pico projects

```sh
# DEBIAN
sudo apt update
sudo apt install cmake gcc-arm-none-eabi build-essential

# MACOS
# Install cmake
brew install cmake

# Install the arm eabi toolchain
brew tap ArmMbed/homebrew-formulae
brew install arm-none-eabi-gcc

# The equivalent to build-essential on linux, you probably already have this.
xcode-select --install
```

## notes

MiDaS Model: v3.0 DPTL-384
dpt_large_384
