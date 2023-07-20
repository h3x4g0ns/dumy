#include <opencv2/opencv.hpp>
#include <iostream>

int main() {
    cv::Mat image;
    cv::VideoCapture cap(0);

    if (!cap.isOpened()) {
        std::cout << "Failed to open the webcam" << std::endl;
        return -1;
    }

    while (true) {
        cap.read(image);
        cv::imshow("Webcam", image);
        if (cv::waitKey(1) == 'q') {
            break;
        }
    }

    cap.release();
    cv::destroyAllWindows();

    return 0;
}

