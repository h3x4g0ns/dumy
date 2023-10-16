import cv2
import torch
import sys
import time
import os
from torchvision.models.segmentation import deeplabv3_mobilenet_v3_large
from torchvision.transforms import functional as F
import numpy as np

# Load DeepLabV3 with MobileNetV3-Large backbone
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
model = deeplabv3_mobilenet_v3_large(pretrained=True, progress=True)  # Load pretrained weights
model.to(device)
model.eval()

def get_cat_mask(img):
    """
    Returns the mask of detected cats.

    Args:
      img (np.array): the frame to detect cats in

    Returns:
      np.array: a mask with cats highlighted
    """
    # Convert the image to tensor
    img_tensor = F.to_tensor(img).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(img_tensor)
        output = output['out'][0]
    output_predictions = torch.argmax(output, 0).cpu().numpy()

    # '17' is usually the label for cats in COCO, '8' for VOC. Please verify this index from your dataset.
    cat_label = 8
    cat_mask = (output_predictions == cat_label)

    return cat_mask

def apply_mask_to_image(img, mask):
  """Applies a mask to the image."""
  overlay_color = [0, 255, 0]  # Green color for the mask
  segmentation_overlay = np.zeros((*mask.shape, 3))
  segmentation_overlay[mask] = overlay_color
  masked_image = cv2.addWeighted(img, 1, segmentation_overlay.astype(np.uint8), 0.5, 0)
  return masked_image

if __name__ == "__main__":
  cap = cv2.VideoCapture(0)
  while True:
    start_time = time.time()

    # Cat Detection
    ret, frame = cap.read()
    cat_mask = get_cat_mask(frame)
    # frame_with_mask = apply_mask_to_image(frame, cat_mask)

    end_time = time.time()
    fps = 1.0 / (end_time - start_time)
    sys.stdout.write("\rFPS: {:.2f}".format(fps))
    sys.stdout.flush()

    # if "DISPLAY" in os.environ:
    #   cv2.imshow("Cat Detection", frame_with_mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  cap.release()
  # if "DISPLAY" in os.environ:
  #   cv2.destroyAllWindows()
