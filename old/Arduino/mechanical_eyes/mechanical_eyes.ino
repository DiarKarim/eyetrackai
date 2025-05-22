#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

int servoMin = 150;  // Calibrate these values
int servoMax = 600;

void setup() {
  Serial.begin(9600);
  pwm.begin();
  pwm.setPWMFreq(50);  // Standard servo frequency
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    int commaIndex = input.indexOf(',');
    if (commaIndex > 0) {
      int xPos = input.substring(0, commaIndex).toInt();
      int yPos = input.substring(commaIndex + 1).toInt();

      xPos = constrain(map(xPos, 75, 105, servoMin, servoMax), servoMin, servoMax);
      yPos = constrain(map(yPos, 75, 105, servoMin, servoMax), servoMin, servoMax);

      pwm.setPWM(0, 0, xPos);  // Motor X
      pwm.setPWM(1, 0, yPos);  // Motor Y
    }
  }
}
