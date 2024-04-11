#include "Servo.h"
Servo xservo;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  xservo.attach(1);
}

void loop() {
  xservo.write(90);
  // put your main code here, to run repeatedly:

}
