from lib.depth import get_depth
from lib.detect import get_cat_mask, apply_mask_to_image
from lib.world import World
from lib.robot import Dumy
from lib.trajectory import Trajectory
import cv2
import time
import sys
import os
import numpy as np

def combine_frames(frame1, frame2):
  """
  Takes 2 frames and stiches them side by side
  """
  if frame1.shape[0] != frame2.shape[0]:
    raise ValueError("Frames must have the same height")
  combined_width = frame1.shape[1] + frame2.shape[1]
  combined_frame = np.zeros((frame1.shape[0], combined_width, 3), dtype=np.uint8)
  combined_frame[:, :frame1.shape[1], :] = frame1
  combined_frame[:, frame1.shape[1]:, :] = frame2
  return combined_frame

def main():
  # loading in camera
  cap = cv2.VideoCapture(-1)
  if "BIG" in os.environ:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

  # setting up world
  world = World(height=480, width=640, render="SHOW" in os.environ)
  step_size = 16

  # setting up robot and engine
  PORT = "COM3"
  with Dumy(PORT) as d:
    engine = Trajectory(d)
    while True:

      ret, frame = cap.read()
      start_time = time.time()

      # get depth and cat bounding boxes
      detect = get_cat_mask(frame)
      depth = get_depth(frame) * 0.005

      if "SHOW" in os.environ:
        # only showing concated frames with proper env var
        detect = apply_mask_to_image(frame, detect)
        depth = cv2.cvtColor(depth, cv2.COLOR_GRAY2BGR)
        frame = combine_frames(depth, detect)
        cv2.imshow("detect and depth", frame)
        
        # we can also show the world view
        world.to_world(depth, step_size)

      # get world coordinate for cat which is middle of bounding box
      if len(detect) > 0:
        x1, y1, x2, y2 = detect[0]
        x = (x1 + x2) // 2
        y = (y1 + y2) // 2
        cat_pos = world.transform(np.array([[x, y]]), depth, frame)

      # timing fps and printing w/ carriage return
      end_time = time.time()
      fps = 1.0 / (end_time - start_time)
      sys.stdout.write("\rFPS: {:.2f}".format(fps))
      sys.stdout.flush()

      # move robot to world coordinate
      if len(cat_pos) > 0:
        joint_angles = engine.calculate(cat_pos)
        d.move(joint_angles)

      if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    cap.release()

    if "SHOW" in os.environ:
      cv2.destroyAllWindows()

if __name__ == "__main__":
  main()

