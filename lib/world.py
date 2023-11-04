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
    # general vision computation
    self.intrinsic = [self.FX, 0, self.height/2, 0, self.FY, self.width/2, 0, 0, 1]
    self.intrinsic = self.intrinsic.reshape((3, 3)).astype(float)
    self.intrinsic_inv = np.linalg.inv(self.intrinsic)
    self.x, self.y = np.meshgrid(np.arange(self.width), np.arange(self.height))
    self.x = self.x.flatten()
    self.y = self.y.flatten()
    
    # render variables
    self.voxel_size = 0.01
    self.grid_shape = (512, 512, 512)
    self.voxel_grid = np.zeros(self.grid_shape, dtype=np.uint8)

  def im2cam(self, depth_frame, render=False):
    """
    Given monocular estimnation of depth we want to take out coordinates in the 
    image space and project them to the camera space. This should give us a 3d 
    reprojection of the scene. Only populate voxel scene if we chose to render
    the scene.
    """
    depth_values = depth_frame.flatten()
    x = np.multiply(self.x, depth_values)
    y = np.multiply(self.x, depth_values)
    points = np.vstack((x, y, depth_values))
    camera_pts = self.intrinsic_inv @ points
    if render:
      self.__update_voxel_grid(camera_pts)

  def __update_voxel_grid(self, camera_points):
    """
    We update the voxel grid with the given camera points. We first calculate 
    the voxel indices for each camera point, clip them to fit in the bounds and 
    update the voxel values if a point exists.
    """
    voxel_indices = ((camera_points / self.voxel_size) + (self.grid_shape / 2)).astype(int)
    voxel_indices = np.clip(voxel_indices, 0, self.grid_shape - 1)
    self.voxel_grid[voxel_indices[0], voxel_indices[1], voxel_indices[2]] = 255

  def visualize_voxel_grid(self):
    """
    Visualized 3D voxel grid
    """
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.voxels(self.voxel_grid, facecolors='b', edgecolor='k')
    plt.show()

if __name__ == "__main__":
  from .depth import get_depth
  import cv2

  cap = cv2.VideoCapture(0)
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
  world = World(height=720, width=12080)
  while True:
    ret, frame = cap.read()
    depth = get_depth(frame)
    world.im2cam(depth, render=True)
    world.visualize_voxel_grid()
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
  cap.release()