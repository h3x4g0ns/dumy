import cv2
import torch

# The MiDaS code expects the `utils` module to be in the Python path
# The following line adds it to the Python path
import sys
sys.path.append('../MiDaS')

from midas.midas_net import MidasNet
from midas.transforms import Resize, NormalizeImage, PrepareForNet
from torchvision.transforms import Compose

# Load pre-trained model
model_path = "model-f6b98070.pt"
model = MidasNet(model_path, non_negative=True).eval()
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

transform = Compose(
    [
        Resize(
            384,
            384,
            resize_target=None,
            keep_aspect_ratio=True,
            ensure_multiple_of=32,
            resize_method="upper_bound",
            image_interpolation_method=cv2.INTER_CUBIC,
        ),
        NormalizeImage(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        Totensor(),
    ]
)

# Open webcam
cap = cv2.VideoCapture(0)

while True:
    # Read frame from webcam
    ret, frame = cap.read()
    if not ret:
        break

    # Estimate depth
    img_input = transform(frame)
    with torch.no_grad():
        prediction = model.forward(img_input)
        prediction = (
            torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=frame.shape[:2],
                mode="bicubic",
                align_corners=False,
            )
            .squeeze()
            .cpu()
            .numpy()
        )

    # Display depth
    cv2.imshow('Depth', prediction)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
