import numpy as np
import viser

class World:
  def __init__(self, height, width, camera="c920", render=False):
    self.height = height
    self.width = width
    self.render = render
    match camera:
      case "c920":
        # focal length was ripped from a repo online
        # TODO: need to validate that the measurements are correct
        self.FX = 1394.6027293299926
        self.FY = 1394.6027293299926
      case _:
        raise ValueError(f"{camera} not supported")
    self.__setup()

  def __setup(self):
    # vision computation variables
    intrinsic = [self.FX, 0, self.width/2, 0, self.FY, self.height/2, 0, 0, 1]
    self.intrinsic = np.asarray(intrinsic, dtype=np.float32).reshape((3, 3))
    self.i2c = np.linalg.inv(self.intrinsic).T
    # TODO: calculate extrinsic matrix
    extrinsic = np.eye(4, dtype=np.float32)
    self.c2w = np.linalg.inv(extrinsic).T
    x, y = np.meshgrid(np.arange(self.width), np.arange(self.height))
    self.x = x.flatten().astype(np.float32)
    self.y = y.flatten().astype(np.float32)

    # render view variables
    self.server = viser.ViserServer(share=True)
    self.wxyz = viser.transforms.SO3.from_matrix(self.c2w[:3, :3]).wxyz
    self.position = self.c2w[:3, 3]

  def __render_view(self, img_frame, world_pts):
    """
    Renders camera and world coordinates in viser
    """
    self.server.add_camera_frustum(
      "/view",
      fov=2 * np.arctan2(self.height / 2, self.intrinsic[0, 0]),
      aspect=self.width/self.height,
      scale=0.4,
      image=img_frame,
      wxyz=self.wxyz,
      position=self.position,
    )

    self.server.add_point_cloud(
      "/reconstruction",
      points=world_pts,
      colors=np.zeros_like(world_pts, dtype=np.uint8),
      point_size=0.01,
      wxyz=self.wxyz,
      position=self.position,
    )

  def to_cam(self, depth_frame, step_size=16):
    """
    Given monocular estimation of depth we want to take out coordinates in the 
    image space and project them to the camera space.

    Args:
      depth_frame (ndarray): H x W matrix representing pixel depth for the scene
      step_size (int): projects (H X W) / step_size rays

    Returns:
      camera_pts (ndarray): N by 3 points projected in camera space
    """
    depth_values = depth_frame.flatten()
    x = np.multiply(self.x, depth_values)
    y = np.multiply(self.y, depth_values)
    points = np.vstack((x, y, depth_values)).T
    camera_pts = self.im2cam(points[::step_size, :])
    return camera_pts
 
  def im2cam(self, points):
    """
    Multiply pixel coordinates with transpose of inverse of intrinsic matrix to 
    get camera coordinates.

    Args:
      points (ndarray): N x 3 image coordinates with depth

    Returns:
      camera_pts (ndarray): N x 3 camera points
    """
    return points @ self.i2c
  
  def to_world(self, depth_frame, step_size=16):
    """
    Reconstruct entire world view from img -> camera -> world. This should give 
    us a 3d reprojection of the scene. We want to pass in a `step_size` to limit the
    number of rays being projected in order to save bandwith.

    Args:
      depth_frame (ndarray): H x W matrix representing pixel depth for the scene
      step_size (int): projects (H X W) / step_size rays

    Returns:
      world_pts (ndarray): N by 3 points projected in world space
    """
    camera_pts = self.to_cam(depth_frame, step_size)
    world_pts = self.cam2world(camera_pts)
    if self.render:
      self.__render_view(depth_frame, world_pts)
    return world_pts

  def cam2world(self, points):
    """
    Multiply camera points with inverse of extrinsic matrix to get world coordinates.

    Args:
      points (ndarray): N x 3 camera coordinates

    Returns:
      world_pts (ndarray): N x 3 world coordinates
    """
    ones = np.ones((points.shape[0], 1), dtype=np.float32)
    points = np.hstack((points, ones))
    world_pts = (points @ self.c2w)[:, :3]
    return world_pts
  
  def transform(self, pixel_coords, depth_frame, img_frame):
    """
    Take the pixel coordinates and transforms them into world coordinates

    Args:
      pixel_coords (ndarray): N x 2 pixel coordinates
      depth_frame (ndarray): H x W depth estimation array

    Returns:
      world_pts (ndarray): N x 3 world coordinates
    """
    depth = depth_frame[pixel_coords[:, 1], pixel_coords[:, 0]]
    pixel_coords = np.concatenate((pixel_coords, depth.reshape(-1, 1)), axis=1)
    camera_pts = self.im2cam(pixel_coords)
    world_pts = self.cam2world(camera_pts)
    if self.render:
      self.__render_view(img_frame, world_pts)
    return world_pts


if __name__ == "__main__":
  from depth import get_depth
  import cv2
  import time
  import sys

  # TODO: need to add the extrinsic matrix for proper pose
  cap = cv2.VideoCapture(-1)
  world = World(height=480, width=640, render=True)
  step_size = 16

  # here we transform all pixels coordinates from the image
  # in production, we only need to project the points of the bounding box of the cat
  while True:
    start = time.time()
    ret, frame = cap.read()
    depth = get_depth(frame) * 0.005
    world.to_world(depth, step_size)
    fps = 1.0 / (time.time() - start)
    sys.stdout.write("\rFPS: {:.2f}".format(fps))
    sys.stdout.flush()

    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
  cap.release()
  