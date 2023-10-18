from lib.detect import model, device
from torch.profiler import profile, record_function, ProfilerActivity
import cv2
import torch
from torchvision.transforms import functional as F


img = cv2.imread("dog.jpg")
with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA], record_shapes=True) as prof:
  with record_function("model_inference"):
    with torch.no_grad():
      img_tensor = F.to_tensor(img).unsqueeze(0).to(device)
      _ = model(img_tensor)

print(prof.key_averages().table())
