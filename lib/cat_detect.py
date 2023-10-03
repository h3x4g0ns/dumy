import cv2
import torch
import torchvision

# Loading Faster R-CNN for cat detection
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
faster_rcnn = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
# faster_rcnn = torchvision.models.detection.fasterrcnn_resnet50_fpn_v2(pretrained=True)
faster_rcnn.compile()
faster_rcnn.to(device)
faster_rcnn.eval()

def get_cat_bounding_boxes(img):
  """
  Returns the bounding boxes of detected cats.

  Args:
    img (np.array): the frame to detect cats in

  Returns:
    List[Tuple[int]]: a list of bounding boxes
  """
  transform = torchvision.transforms.Compose([torchvision.transforms.ToTensor()])
  input_tensor = transform(img).unsqueeze(0).to(device)
  with torch.no_grad():
      prediction = faster_rcnn(input_tensor)

  boxes = prediction[0]['boxes']
  labels = prediction[0]['labels']
  scores = prediction[0]['scores']

  # Filter only cat detections with scores above a threshold (let's say 0.5)
  # COCO dataset labels cats as 17
  cat_boxes = [box for box, label, score in zip(boxes, labels, scores) if label == 17 and score > 0.5]

  return cat_boxes

def draw_boxes(img, boxes):
  """Draws boxes on the img."""
  for box in boxes:
    cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
  return img

if __name__ == "__main__":
  cap = cv2.VideoCapture(0)
  while True:
    ret, frame = cap.read()

    # Cat Detection
    boxes = get_cat_bounding_boxes(frame)
    frame_with_boxes = draw_boxes(frame, boxes)
    
    cv2.imshow("Cat Detection", frame_with_boxes)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

  cap.release()
  cv2.destroyAllWindows()
