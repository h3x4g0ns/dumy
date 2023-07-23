import cv2
import torch

model_type = "MiDaS_small"
midas = torch.hub.load("intel-isl/MiDaS", model_type)
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
midas.to(device)
midas.eval()
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
transform = midas_transforms.small_transform

def get_depth(img):
  """
  Returns the depth map of the img through MiDaS.

  Args:
    img (np.array): the frame to get the depth map from

  Returns:
    np.array: the depth map
  """
  input_batch = transform(img).to(device)
  with torch.no_grad():
    prediction = midas(input_batch)

    prediction = torch.nn.functional.interpolate(
      prediction.unsqueeze(1),
      size=img.shape[:2],
      mode="bicubic",
      align_corners=False,
    ).squeeze()

  output = prediction.cpu().numpy()
  return output

if __name__ == "__main__":
  cap = cv2.VideoCapture(0)
  while True:
    ret, frame = cap.read()
    depth = get_depth(frame)
    norm_array = cv2.normalize(depth, None, alpha = 0, beta = 255, norm_type = cv2.NORM_MINMAX, dtype = cv2.CV_8U)
    rgb_array = cv2.cvtColor(norm_array, cv2.COLOR_GRAY2RGB)
    cv2.imshow("frame", rgb_array)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  cap.release()
  cv2.destroyAllWindows()