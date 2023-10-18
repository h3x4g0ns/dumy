import torch
import time
import sys
import cv2
import numpy as np

# Model
model = torch.hub.load("ultralytics/yolov5", "yolov5s")

# Images
cap = cv2.VideoCapture(-1)
while True:

  # Inference
  ret, frame = cap.read()
  start = time.time()
  results = model(frame)
  end = time.time()
  fps = 1.0 / (end - start)
  sys.stdout.write("\rFPS: {:.2f}".format(fps))
  sys.stdout.flush()

  # Draw bounding boxes on the image
  output = results.pred[0]  # Get bounding box predictions
  for det in output:
    class_id = int(det[5])
    conf = float(det[4])
    x1, y1, x2, y2 = map(int, det[:4])

    # Draw bounding box and label on the image
    label = f"{model.names[class_id]}: {conf:.2f}"
    color = (0, 255, 0)  # Green color
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

  # Show the annotated image
  cv2.imshow("detect and depth", frame)

  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

# Release the video capture and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
