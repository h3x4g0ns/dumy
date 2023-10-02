#include "pico/stdlib.h"
#include "hardware/pwm.h"

// Define the servo parameters
const uint SERVO_PIN = 0; // Change this to your GPIO pin number
const uint PWM_FREQ_HZ = 50; // Standard servo frequency
const uint PWM_MAX_DUTY = (1 << 16) - 1; // 16-bit PWM

// Define the servo pulse width for 0 and 180 degrees
const uint SERVO_MIN_PULSE_WIDTH_US = 1000;
const uint SERVO_MAX_PULSE_WIDTH_US = 2000;

void set_servo_angle(uint pin, float angle) {
    if (angle < 0.0) angle = 0.0;
    if (angle > 180.0) angle = 180.0;

    uint pulse_width = SERVO_MIN_PULSE_WIDTH_US + 
                       (uint)((SERVO_MAX_PULSE_WIDTH_US - SERVO_MIN_PULSE_WIDTH_US) * angle / 180.0);

    uint duty = (uint)((float)PWM_MAX_DUTY * pulse_width / 1e6 * PWM_FREQ_HZ);
    pwm_set_gpio_level(pin, duty);
}

int main() {
    stdio_init_all();

    // Setup PWM for the servo
    gpio_set_function(SERVO_PIN, GPIO_FUNC_PWM);
    uint slice_num = pwm_gpio_to_slice_num(SERVO_PIN);
    pwm_set_wrap(slice_num, PWM_MAX_DUTY);
    pwm_set_clkdiv(slice_num, clock_get_hz(clk_sys) / (PWM_MAX_DUTY * PWM_FREQ_HZ));
    pwm_set_enabled(slice_num, true);

    while (true) {
        for (float angle = 0; angle <= 180; angle += 5) {
            set_servo_angle(SERVO_PIN, angle);
            sleep_ms(50);
        }
        sleep_ms(500);

        for (float angle = 180; angle >= 0; angle -= 5) {
            set_servo_angle(SERVO_PIN, angle);
            sleep_ms(50);
        }
        sleep_ms(500);
    }

    return 0;
}
