#include <Servo.h>
#include "servo_control.h"

#define L1_PORT 11
#define L2_PORT 10
#define L3_PORT 12

Servo l1;
Servo l2;
Servo l3;

int i = 0;
volatile char data[16];
volatile bool terminated;

float strlfcopy(const char *src, size_t size) {
    char dst[size];
    int i = 0;
    float res;
    int n = 1;
    if (src[0] == '-') {
        *src++;
        n = -1;
    }
    while (size > 1 && *src) {
        dst[i] = *src++;
        i++;
        size--;
    }
    res = atof(dst);
    //Serial.println(res);
    return res * n;
}

void setup() {
    Serial.begin(9600);
    l1.attach(L1_PORT);
    l2.attach(L2_PORT);
    l3.attach(L3_PORT);
    Serial.println("init");
    terminated = false;
    data[0] = '\0';
}

void loop() {
    //read in serial data until the terminating character
    if (Serial.available()>0) {
        char incoming = Serial.read();
        if (incoming == 'r') {
            terminated = true;
            i = 0;
        } else {
            data[i] = incoming;
            i++;
        }
    }

    if (terminated) {
        Serial.println(data);
        Serial.print('end');
        float angles[3];
        angles[0] = strlfcopy(strtok(data, ", "), 5);
        angles[1] = strlfcopy(strtok(NULL, ", "), 5);
        angles[2] = strlfcopy(strtok(NULL, ", "), 5);
        l1.write(angles[0]);
        l2.write(angles[1]);
        l3.write(angles[2]);
        memset(data, 0, 16);
        terminated = false;
    }
}