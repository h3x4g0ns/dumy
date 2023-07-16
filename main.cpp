#include <libfreenect/libfreenect.hpp>
#include <opencv2/opencv.hpp>
#include <iostream>

#define HEIGHT (720)
#define WIDTH (1280)

class MyFreenectDevice : public Freenect::FreenectDevice {
public:
    MyFreenectDevice(freenect_context *_ctx, int _index)
        : Freenect::FreenectDevice(_ctx, _index), m_buffer_depth(FREENECT_DEPTH_11BIT),
          m_buffer_rgb(FREENECT_VIDEO_RGB), m_gamma(2048), depthMat(cv::Size(WIDTH,HEIGHT),CV_16UC1),
          rgbMat(cv::Size(WIDTH,HEIGHT), CV_8UC3, cv::Scalar(0)), ownMat(cv::Size(WIDTH,HEIGHT),CV_8UC3,cv::Scalar(0)) {

        for(unsigned int i = 0 ; i < 2048 ; i++) {
            float v = i/2048.0;
            v = std::pow(v, 3) * 6;
            m_gamma[i] = v*6*256;
        }
    }
    
    // Do not call directly even in child
    void VideoCallback(void* _rgb, uint32_t timestamp) {
        std::cout << "RGB callback" << std::endl;
        m_rgb_mutex.lock();
        uint8_t* rgb = static_cast<uint8_t*>(_rgb);
        rgbMat.data = rgb;
        m_rgb_mutex.unlock();
    };

    // Do not call directly even in child
    void DepthCallback(void* _depth, uint32_t timestamp) {
        std::cout << "Depth callback" << std::endl;
        m_depth_mutex.lock();
        uint16_t* depth = static_cast<uint16_t*>(_depth);
        depthMat.data = (uchar*) depth;
        m_depth_mutex.unlock();
    }

    bool getVideo(cv::Mat& output) {
        m_rgb_mutex.lock();
        cv::cvtColor(rgbMat, output, cv::COLOR_RGB2BGR);
        m_rgb_mutex.unlock();
        return true;
    }

    bool getDepth(cv::Mat& output) {
            m_depth_mutex.lock();
            depthMat.copyTo(output);
            m_depth_mutex.unlock();
        return true;
    }

private:
    std::vector<uint8_t> m_buffer_depth;
    std::vector<uint8_t> m_buffer_rgb;
    std::vector<uint16_t> m_gamma;
    cv::Mat depthMat;
    cv::Mat rgbMat;
    cv::Mat ownMat;
    std::mutex m_rgb_mutex;
    std::mutex m_depth_mutex;
};

int main(int argc, char **argv) {
    bool die(false);
    std::string filename("snapshot");
    std::string suffix(".png");
    int i_snap(0),iter(0);

    cv::namedWindow("rgb",cv::WINDOW_AUTOSIZE);
    cv::namedWindow("depth",cv::WINDOW_AUTOSIZE);
    Freenect::Freenect freenect;
    MyFreenectDevice& device = freenect.createDevice<MyFreenectDevice>(0);
    device.startVideo();
    device.startDepth();
    while (!die) {
        cv::Mat depthMat(cv::Size(WIDTH,HEIGHT),CV_16UC1);
        cv::Mat rgbMat(cv::Size(WIDTH,HEIGHT),CV_8UC3,cv::Scalar(0));
        device.getDepth(depthMat);
        device.getVideo(rgbMat);

        cv::imshow("rgb", rgbMat);
        cv::imshow("depth",depthMat);
        char k = cv::waitKey(5);
        if( k == 27 ){
            cv::destroyWindow("rgb");
            cv::destroyWindow("depth");
            break;
        }
    }

    device.stopVideo();
    device.stopDepth();
    return 0;
}

