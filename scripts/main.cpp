#include <iostream>
#include <libfreenect/libfreenect.h>
#include <opencv2/opencv.hpp>

freenect_context *f_ctx;
freenect_device *f_dev;
cv::Mat depthMat(480, 640, CV_16UC1);
cv::Mat rgbMat(480, 640, CV_8UC3, cv::Scalar(0));
bool die = false;

void depth_cb(freenect_device *dev, void *v_depth, uint32_t timestamp) {
  cv::Mat depth(480, 640, CV_16UC1, v_depth);
  cv::Mat depth_f(480, 640, CV_8UC1);
  depth.convertTo(depth_f, CV_8UC1, 255.0 / 2048.0); // Kinect's depth is in the range 0-2047
  depth_f.copyTo(depthMat);
}

void rgb_cb(freenect_device *dev, void *rgb, uint32_t timestamp) {
  cv::Mat rgb_frame(480, 640, CV_8UC3, rgb);
  cv::cvtColor(rgb_frame, rgbMat, cv::COLOR_RGB2BGR);
}

int main() {
  if (freenect_init(&f_ctx, NULL) < 0) {
    std::cout << "freenect_init() failed" << std::endl;
    return 1;
  }

  freenect_set_log_level(f_ctx, FREENECT_LOG_DEBUG);

  int nr_devices = freenect_num_devices(f_ctx);
  std::cout << "Number of devices found: " << nr_devices << std::endl;

  if (nr_devices < 1) {
    freenect_shutdown(f_ctx);
    return 1;
  }

  if (freenect_open_device(f_ctx, &f_dev, 0) < 0) {
    std::cout << "Could not open device" << std::endl;
    freenect_shutdown(f_ctx);
    return 1;
  }

  freenect_set_depth_callback(f_dev, depth_cb);
  freenect_set_video_callback(f_dev, rgb_cb);
  freenect_set_video_mode(f_dev, freenect_find_video_mode(FREENECT_RESOLUTION_MEDIUM, FREENECT_VIDEO_RGB));
  freenect_start_depth(f_dev);
  freenect_start_video(f_dev);

  while (!die && freenect_process_events(f_ctx) >= 0) {
    cv::imshow("Depth Image", depthMat);
    cv::imshow("RGB Image", rgbMat);

    if (cv::waitKey(1) == 27) {
      std::cout << "esc key is pressed by user" << std::endl;
      die = true;
    }
  }

  freenect_stop_depth(f_dev);
  freenect_stop_video(f_dev);
  freenect_close_device(f_dev);
  freenect_shutdown(f_ctx);

  return 0;
}
