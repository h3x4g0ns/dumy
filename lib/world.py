import numpy as np
import matplotlib.pyplot as plt

class World:
  def __init__(self, height, width, camera="c920"):
    self.height = height
    self.width = width
    match camera:
      case "c920":
        self.FX = 1394.6027293299926
        self.FY = 1394.6027293299926
      case _:
        raise ValueError(f"{camera} not supported")
    self.__setup()

  def __setup(self):
    intrinsic = [self.FX, 0, self.width/2, 0, self.FY, self.height/2, 0, 0, 1]
    self.intrinsic = np.asarray(intrinsic, dtype=np.float32).reshape((3, 3))
    self.i2c = np.linalg.inv(self.intrinsic).T
    extrinsic = np.eye(4, dtype=np.float32)
    self.c2w = extrinsic
    x, y = np.meshgrid(np.arange(self.width), np.arange(self.height)).astype(np.float32)
    self.x = x.flatten()
    self.y = y.flatten()

  def to_cam(self, depth_frame, step_size=16):
    """
    Given monocular estimation of depth we want to take out coordinates in the 
    image space and project them to the camera space. This should give us a 3d 
    reprojection of the scene.
    """
    depth_values = depth_frame.flatten()
    x = np.multiply(self.x, depth_values)
    y = np.multiply(self.y, depth_values)
    points = np.hstack((x, y, depth_values))[::step_size, :]
    camera_pts = self.im2cam(points)
    return camera_pts

  def im2cam(self, points):
    """
    Multiply image points by inverse of intrinsic matrix to get camera coordinates.
    """
    return points @ self.i2c
  
  def to_world(self, depth_frame, step_size=16):
    """
    Reconctruct entire world view img -> camera -> world
    We take ever coordinate from the depth frame and reconstruct the scene.
    """
    camera_pts = self.to_cam(depth_frame, step_size)
    world_pts = self.cam2world(self, camera_pts)
    return world_pts

  def cam2world(self, points):
    """
    Multiple camera points by inverse of extrinsic matrix to get world coordinates.
    """
    ones = np.ones((points.shape[0], 1), dtype=np.float32)
    points = np.hstack((points, ones))
    world_pts = (points @ self.c2w)[:, :3]
    return world_pts

if __name__ == "__main__":
  from depth import get_depth
  import cv2
  import viser
  import time
  import sys

  cap = cv2.VideoCapture(-1)
  world = World(height=480, width=640)
  H, W, K, c2w = world.height, world.width, world.intrinsic, world.c2w
  server = viser.ViserServer(share=True)
  step_size = 16
  wxyz = viser.transforms.SO3.from_matrix(c2w[:3, :3]).wxyz
  position = c2w[:3, 3],

  # here we transform all pixels coordinates from the image
  # in production, we only need to project the points of the bounding box of the cat
  while True:
    start = time.time()
    ret, frame = cap.read()
    depth = get_depth(frame) * 0.005
    pts = world.im2cam(depth, step_size=16)
    colors = np.transpose(frame, axes=(1, 0, 2)).reshape(-1, 3)
    colors = colors[::step_size, :]
    fps = 1.0 / (time.time() - start)
    sys.stdout.write("\rFPS: {:.2f}".format(fps))
    sys.stdout.flush()

    # adds viewport
    # TODO: need to add the extrinsic matrix for proper pose
    server.add_camera_frustum(
      "/view",
      fov=2 * np.arctan2(H / 2, K[0, 0]),
      aspect=W/H,
      scale=0.25,
      image=frame,
      wxyz=wxyz,
      position=position,
    )

    server.add_point_cloud(
      "/reconstruction",
      points=pts,
      colors=colors,
      point_size=0.01,
      wxyz=wxyz,
      position=position,
    )

    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
  cap.release()
  