import cv2
import torch
import sys
import time
import os
from torchvision.models.detection import ssd300_vgg16
from torchvision.transforms import functional as F

# Load SSD300 with VGG16 backbone
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
model = ssd300_vgg16(pretrained=True)  # Load pretrained weights from COCO
model.to(device)
model.eval()

def get_cat_bounding_boxes(img):
    """
    Returns the bounding boxes of detected cats.

    Args:
      img (np.array): the frame to detect cats in

    Returns:
      List[Tuple[int]]: a list of bounding boxes
    """
    img_tensor = F.to_tensor(img).unsqueeze(0).to(device)
    outputs = model(img_tensor)
    
    detected_boxes = []
    for box, label, score in zip(outputs[0]['boxes'], outputs[0]['labels'], outputs[0]['scores']):
        if label == 17 and score > 0.5:  # '17' is the label for cats in COCO
            detected_boxes.append(box.cpu().detach().numpy())

    return detected_boxes

def draw_boxes(img, boxes):
  """Draws boxes on the img."""
  for box in boxes:
    x1, y1, x2, y2 = map(int, box)
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
  return img

if __name__ == "__main__":
  cap = cv2.VideoCapture(0)
  while True:
    start_time = time.time()

    # Cat Detection
    ret, frame = cap.read()
    boxes = get_cat_bounding_boxes(frame)
    frame_with_boxes = draw_boxes(frame, boxes)

    end_time = time.time()
    fps = 1.0 / (end_time - start_time)
    sys.stdout.write("\rFPS: {:.2f}".format(fps))
    sys.stdout.flush()
    
    if "DISPLAY" in os.environ:
      cv2.imshow("Cat Detection", frame_with_boxes)
      
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break

  cap.release()
  if "DISPLAY" in os.environ:
    cv2.destroyAllWindows()
