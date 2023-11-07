#include <Servo.h>
#include "servo_control.h"

#define L1_PORT 10
#define L2_PORT 11
#define L3_PORT 12

Servo l1;
Servo l2;
Servo l3;

float strlfcopy(const char *src, size_t size) {
    char dst[size];
    int i = 0;
    float res;
    while (size > 1 && *src) {
        dst[i] = *src++;
        i++;
        size--;
    }
    res = atof(dst);
    return res;
}

void setup() {
    Serial.begin(9600);
    l1.attach(L1_PORT);
    l2.attach(L2_PORT);
    l3.attach(L3_PORT);
    Serial.println("init");
}

void loop() {
    //Serial input
    int incoming = Serial.available();
    if (incoming==9) {
        char data[incoming];
        float angles[3];
        //read in serial data
        Serial.readBytesUntil("\n", data, incoming);
        //split string and convert to float
        angles[0] = strlfcopy(strtok(data, ","), 5);
        angles[1] = strlfcopy(strtok(data, ","), 5);
        angles[2] = strlfcopy(strtok(data, ","), 5);
        Serial.println(angles[0]);
        l1.write(angles[0]);
        l2.write(angles[1]);
        l3.write(angles[2]);
    }
}