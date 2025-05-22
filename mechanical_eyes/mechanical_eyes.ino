// Sunfounder PCA9685 servo driver - Controlled via serial from Python
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm;

#define NUM_SERVOS 2
#define SERVO_DELAY 500

int servoPins[NUM_SERVOS] = {0, 1}; // 0 = Y-axis, 1 = X-axis
int servoMin[NUM_SERVOS] = {100, 100};
int servoMax[NUM_SERVOS] = {200, 300};

int xMid = 150;
int yMid = 200;

String inputString = "";
bool stringComplete = false;

void setup() {
  randomSeed(analogRead(0));
  Serial.begin(9600);
  Serial.println("Arduino ready. Waiting for 'y,x' input from Python...");

  pwm.begin();
  pwm.setPWMFreq(50);

  // Move to initial positions
  pwm.setPWM(servoPins[0], 0, yMid);
  pwm.setPWM(servoPins[1], 0, xMid);

  inputString.reserve(32);
}

void loop() {
  if (stringComplete) {
    int yVal, xVal;
    if (parseInput(inputString, yVal, xVal)) {
      yVal = constrain(yVal, servoMin[0], servoMax[0]);
      xVal = constrain(xVal, servoMin[1], servoMax[1]);

      pwm.setPWM(servoPins[0], 0, yVal); // Y
      pwm.setPWM(servoPins[1], 0, xVal); // X

      Serial.print("Moved to -> Y: ");
      Serial.print(yVal);
      Serial.print(" | X: ");
      Serial.println(xVal);
    } else {
      Serial.println("Invalid format. Use: y,x");
    }

    inputString = "";
    stringComplete = false;
  }
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}

bool parseInput(String input, int &y, int &x) {
  int commaIndex = input.indexOf(',');
  if (commaIndex == -1) return false;

  String yStr = input.substring(0, commaIndex);
  String xStr = input.substring(commaIndex + 1);

  y = yStr.toInt();
  x = xStr.toInt();

  return true;
}
