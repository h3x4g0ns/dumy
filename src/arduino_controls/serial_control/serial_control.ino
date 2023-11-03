#include <Servo.h>
#include "servo_control.h"

#define L1_PORT 10
#define L2_PORT 11
#define B_PORT 12

Servo l1;
Servo l2;
Servo b;

char data[6];
struct node_p
{
    float data[3];
    node_p* next;
} root;


struct node_p *first;
struct node_p *last;

void addLast(node_p* n) {
    last->next = n;
    last = n;
}

node_p popFirst() {
    node_p tmp = *first;
    if (first->next != NULL) {
        first = first->next;
    } else {
        first = NULL;
    }
    return tmp;
}

void setup() {
    Serial.begin(115200);
    l1.attach(L1_PORT);
    l2.attach(L2_PORT);
    b.attach(B_PORT);
    Serial.println("", first);
    Serial.println("init");
}

void loop() {
    //Serial input
    if (Serial.available()) {
        struct node_p tmp;
        Serial.readBytesUntil("\n", data, 6);
        tmp.data[0] = (float)*strtok(data, ","); 
        tmp.data[1] = (float)*strtok(data, ","); 
        tmp.data[2] = (float)*strtok(data, ",");
        Serial.println(tmp.data);
        if () {
            first = malloc(sizeof(root));
            first
            last = first;
        } else {

        }
    }
    //serve first data element in queue
    if (first != NULL) {
        b.write(first->data[0]);
        l1.write(first->data[1]);
        l2.write(first->data[2]);
        first = first->next;
    }
}