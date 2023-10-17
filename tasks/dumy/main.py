from lib.depth import get_depth
from lib.detect import get_cat_mask, apply_mask_to_image
import cv2
import threading
import time
import sys
import os
import numpy as np

def depth_stub(buffer, frame):
  """
  Takes frame and sends inference to model to get pixel-wise depth
  """
  buffer["depth"] = get_depth(frame)

def detect_stub(buffer, frame):
  """
  Takes frame and sends inference to model to get cat segmentation
  """
  buffer["detect"] = get_cat_mask(frame)

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
  cap = cv2.VideoCapture(-1)
  if "BIG" in os.environ:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

  while True:

    ret, frame = cap.read()
    result = {}
    start_time = time.time()

    # individual threading for each model inference
    # NOTE: this is useless because of GIL
    depth_thread = threading.Thread(target=depth_stub, args=(result, frame), daemon=True)
    detect_thread = threading.Thread(target=detect_stub, args=(result, frame), daemon=True)
    depth_thread.start()
    detect_thread.start()
    depth_thread.join()
    detect_thread.join()

    # timing fps and printing w/ carriage return
    end_time = time.time()
    fps = 1.0 / (end_time - start_time)
    sys.stdout.write("\rFPS: {:.2f}".format(fps))
    sys.stdout.flush()

    # only showing concated frames with proper env var
    if "DISPLAY" in os.environ:
      depth = result["depth"]
      detect = result["detect"]
      detect = apply_mask_to_image(frame, detect)
      depth = cv2.cvtColor(depth, cv2.COLOR_GRAY2BGR)
      frame = combine_frames(depth, detect)
      cv2.imshow("detect and depth", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  cap.release()

  if "DISPLAY" in os.environ:
    cv2.destroyAllWindows()

if __name__ == "__main__":
  main()

