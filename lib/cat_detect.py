import cv2
import torch

# Load YOLOv5 for cat detection
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
yolov5 = torch.hub.load('ultralytics/yolov5', 'yolov5n')  # for smaller/faster model you can use 'yolov5s'
yolov5.to(device)
yolov5.eval()

def get_cat_bounding_boxes(img):
  """
  Returns the bounding boxes of detected cats.

  Args:
    img (np.array): the frame to detect cats in

  Returns:
    List[Tuple[int]]: a list of bounding boxes
  """
  results = yolov5(img)
  detected_boxes = []
  for label, name in enumerate(results.names):
    if name == 'cat':
      cat_idx = label
      for *box, conf, cls in results.pred[0]:
        if cls == cat_idx and conf > 0.5:  # You can adjust the confidence threshold
          detected_boxes.append(box)

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
    ret, frame = cap.read()

    # Cat Detection
    boxes = get_cat_bounding_boxes(frame)
    frame_with_boxes = draw_boxes(frame, boxes)
    
    cv2.imshow("Cat Detection", frame_with_boxes)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

  cap.release()
  cv2.destroyAllWindows()
