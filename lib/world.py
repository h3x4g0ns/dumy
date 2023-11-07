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
    # general vision variables
    self.intrinsic = [self.FX, 0, self.width/2, 0, self.FY, self.height/2, 0, 0, 1]
    self.intrinsic = np.asarray(self.intrinsic).reshape((3, 3)).astype(float)
    self.intrinsic_inv = np.linalg.inv(self.intrinsic)
    self.x, self.y = np.meshgrid(np.arange(self.width), np.arange(self.height))
    self.x = self.x.flatten()
    self.y = self.y.flatten()
    
    # render variables
    self.voxel_size = 0.01
    self.grid_shape = np.asarray((20, 20, 20))
    self.grid = np.zeros(self.grid_shape, dtype=bool)

  def im2cam(self, depth_frame):
    """
    Given monocular estimnation of depth we want to take out coordinates in the 
    image space and project them to the camera space. This should give us a 3d 
    reprojection of the scene. Only populate voxel scene if we chose to render
    the scene.
    """
    depth_values = depth_frame.flatten()
    x = np.multiply(self.x, depth_values)
    y = np.multiply(self.y, depth_values)
    points = np.vstack((x, y, depth_values))
    camera_pts = (self.intrinsic_inv @ points).T
    return camera_pts

if __name__ == "__main__":
  from depth import get_depth
  import cv2
  import viser

  cap = cv2.VideoCapture(-1)
  world = World(height=480, width=640)
  server = viser.ViserServer(share=True)
  samples = 16

  while True:
    ret, frame = cap.read()
    depth = get_depth(frame) * 0.005
    pts = world.im2cam(depth)
    H, W, K = world.height, world.width, world.intrinsic
    pts = pts[::samples, :]
    colors = np.transpose(frame, axes=(1, 0, 2)).reshape(-1, 3)
    colors = colors[::samples, :]

    server.add_camera_frustum(
      "/view",
      fov=2 * np.arctan2(H / 2, K[0, 0]),
      aspect=W/H,
      scale=0.25,
      image=frame,
    )

    server.add_point_cloud(
      "/reconstruction",
      points=pts,
      colors=colors,
      point_size=0.01,
    )

    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
  cap.release()
  