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
    camera_pts = (self.intrinsic_inv @ points).T
    if render:
      self.__update_voxel_grid(camera_pts)
    return camera_pts

  def __update_voxel_grid(self, camera_points):
    """
    We update the voxel grid with the given camera points. We first calculate 
    the voxel indices for each camera point, clip them to fit in the bounds and 
    update the voxel values if a point exists.
    """
    print(camera_points.min(), camera_points.max())
    voxel_indices = ((camera_points / self.voxel_size) + (self.grid_shape[0] / 2)).astype(int)
    voxel_indices = np.clip(voxel_indices, 0, self.grid_shape[0]-1)
    self.grid.fill(False)
    self.grid[voxel_indices] = True

  def visualize_voxel_grid(self):
    """
    Visualized 3D voxel grid
    """
    ax = plt.figure().add_subplot(projection='3d')
    ax.voxels(self.grid, edgecolor='k')
    plt.show()

if __name__ == "__main__":
  from depth import get_depth
  import cv2

  cap = cv2.VideoCapture(-1)
  world = World(height=480, width=640)
  # while True:
  ret, frame = cap.read()
  depth = get_depth(frame)
  pts = world.im2cam(depth, render=True)
  fig = plt.figure()
  ax = fig.add_subplot(111, projection='3d')
  ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=1)
  ax.set_xlabel('X Coordinate')
  ax.set_ylabel('Y Coordinate')
  ax.set_zlabel('Z Coordinate')
  plt.show()

  # TODO:
  # use pyvista or vtk for proper scene rendering


  # world.visualize_voxel_grid()
  # # if cv2.waitKey(1) & 0xFF == ord('q'):
  #   break
  cap.release()
  