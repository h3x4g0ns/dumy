import math

sensor_width = 4.8  # mm
FOV_degrees = 78
FOV_radians = math.radians(FOV_degrees)

pixel_focal_length = (sensor_width * 0.5) / math.tan(FOV_radians * 0.5)

print("Estimated pixel focal length:", pixel_focal_length)
