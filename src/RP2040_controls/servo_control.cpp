#include "pico/stdlib.h"
#include "hardware/pwm.h"

const uint SERVO_PIN = 0;           // GPIO pin connected to the servo signal wire
const uint PWM_FREQ_HZ = 50;        // Servo motor standard frequency (50 Hz)
const uint PWM_PERIOD_US = 20000;   // 20 ms (standard servo period)
const uint SERVO_MIN_US = 1000;     // Minimum pulse width (0 degrees)
const uint SERVO_MAX_US = 2000;     // Maximum pulse width (180 degrees)

void set_servo_angle(uint slice_num, float angle) {
    if (angle < 0.0) angle = 0.0;
    if (angle > 180.0) angle = 180.0;

    // Calculate the pulse width based on the angle
    uint pulse_width_us = SERVO_MIN_US + (uint)((SERVO_MAX_US - SERVO_MIN_US) * angle / 180.0);

    // Calculate the PWM duty cycle from the pulse width
    uint16_t duty_cycle = (uint16_t)(pulse_width_us * PWM_FREQ_HZ * PWM_PERIOD_US / 1000000);

    // Set the PWM channel level
    pwm_set_chan_level(slice_num, PWM_CHAN_A, duty_cycle);
}

int main() {
    stdio_init_all();

    // Initialize PWM
    gpio_set_function(SERVO_PIN, GPIO_FUNC_PWM);
    uint slice_num = pwm_gpio_to_slice_num(SERVO_PIN);
    pwm_set_wrap(slice_num, PWM_PERIOD_US);
    pwm_set_clkdiv(slice_num, 16); // 125 MHz / 16 = 7.8125 MHz

    // Enable PWM slice
    pwm_set_enabled(slice_num, true);

    while (true) {
        // Move the servo from 0 to 180 degrees in steps of 15 degrees
        for (float angle = 0; angle <= 180; angle += 15) {
            set_servo_angle(slice_num, angle);
            sleep_ms(1000);
        }

        // Move the servo back from 180 to 0 degrees in steps of 15 degrees
        for (float angle = 180; angle >= 0; angle -= 15) {
            set_servo_angle(slice_num, angle);
            sleep_ms(1000);
        }
    }

    return 0;
}
