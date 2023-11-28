// copy this file into the libraries directory in the Arduino install path
const unsigned int SERVO_PIN = 0;// GPIO pin connected to the servo signal wire
const unsigned int PWM_FREQ_HZ = 50;// Servo motor standard frequency (50 Hz)
const unsigned int PWM_PERIOD_US = 20000;// 20 ms (standard servo period)
const unsigned int SERVO_MIN_US = 1000;// Minimum pulse width (0 degrees)
const unsigned int SERVO_MAX_US = 2000;// Maximum pulse width (180 degrees)

unsigned short angle_to_duty_cycle(float angle) {
    if (angle < 0.0) angle = 0.0;
    if (angle > 180.0) angle = 180.0;

    // Calculate the pulse width based on the angle
    unsigned int pulse_width_us = SERVO_MIN_US + (unsigned int)((SERVO_MAX_US - SERVO_MIN_US) * angle / 180.0);

    // Calculate the PWM duty cycle from the pulse width
    unsigned short duty_cycle = (unsigned short)(pulse_width_us * PWM_FREQ_HZ * PWM_PERIOD_US / 1000000);

    return duty_cycle;
}
