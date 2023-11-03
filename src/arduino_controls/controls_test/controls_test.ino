#include <Servo.h>
#include "servo_control.h"

#define L1_PORT 10
#define L2_PORT 11
#define B_PORT 12

Servo l1;
Servo l2;
Servo b;

void setup() {
    Serial.begin(115200);
    l1.attach(L1_PORT);
    l2.attach(L2_PORT);
    b.attach(B_PORT);
}

void loop() {
    while (true) {
        // Move the servo from 0 to 180 degrees in steps of 15 degrees
        for (float angle = 0; angle <= 180; angle += 15) {
            l1.write(angle);
            delay(1000);
        }

        // Move the servo back from 180 to 0 degrees in steps of 15 degrees
        for (float angle = 180; angle >= 0; angle -= 15) {
            l1.write(angle);
            delay(1000);
        }
    }
}
