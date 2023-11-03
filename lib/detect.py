import cv2
import torch
import sys
import time
import os

model = torch.hub.load("ultralytics/yolov5", "yolov5s")

def get_cat_mask(img, threshold=0.4):
  """
  Returns the bounding of detected cats.

  Args:
    img (np.array): the frame to detect cats in
    threshold (int): confidence threshold for detecting cat

  Returns:
    bboxs: (list) list of bounding boxes with cat in it
  """
  with torch.no_grad():
    results = model(img)
    output = results.pred[0]
  bboxs = []
  for det in output:
    class_id = int(det[5])
    conf = float(det[4])
    x1, y1, x2, y2 = map(int, det[:4])
    if model.names[class_id] == "cat" and conf >= threshold:
      bboxs.append(x1, y1, x2, y2)
  return bboxs

def apply_mask_to_image(img, bboxs):
  """
  Draws bounding boxes on image
  
  Args: 
    img (np.array): the frame to draw on
    bbox (list): list of bounding boxes
    
  Returns:
    img (np.array): annotate frame
  """
  for x1, y1, x2, y2 in bboxs:
    color = (0, 255, 0)  # Green color
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
  return img

if __name__ == "__main__":
  cap = cv2.VideoCapture(0)
  while True:
    start_time = time.time()

    # Cat Detection
    ret, frame = cap.read()
    cat_mask = get_cat_mask(frame)
    frame_with_mask = apply_mask_to_image(frame, cat_mask)
    
    if "SHOW" in os.environ:
      cv2.imshow("Cat Detection", frame_with_mask)

    end_time = time.time()
    fps = 1.0 / (end_time - start_time)
    sys.stdout.write("\rFPS: {:.2f}".format(fps))
    sys.stdout.flush()


    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  cap.release()
  if "SHOW" in os.environ:
    cv2.destroyAllWindows()
