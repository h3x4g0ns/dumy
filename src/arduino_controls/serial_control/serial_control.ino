#include <Servo.h>
#include "servo_control.h"

#define L1_PORT 12
#define L2_PORT 11
#define B_PORT 10

Servo l1;
Servo l2;
Servo b;

char data[6];
struct node_p
{
    float data[3];
} root;

void setup() {
    Serial.begin(115200);
    l1.attach(L1_PORT);
    l2.attach(L2_PORT);
    b.attach(B_PORT);
    root.data[0] = 0;
    root.data[1] = 0;
    root.data[2] = 0;
    Serial.println("init");
}

void loop() {
    //Serial input
    if (Serial.available()) {
        Serial.readBytesUntil("\n", data, 6);
        root.data[0] = (float)*strtok(data, ",");
        root.data[1] = (float)*strtok(data, ",");
        root.data[2] = (float)*strtok(data, ",");
        //Serial.println("data: %f %f %f \n", root.data[0], root.data[1], root.data[2]);
        b.write(root.data[0]);
        l1.write(root.data[1]);
        l2.write(root.data[2]);
    }
}