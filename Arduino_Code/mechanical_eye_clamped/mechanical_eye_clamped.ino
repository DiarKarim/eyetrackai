#include <Wire.h> // Include Wire library for I2C communication
#include <Adafruit_PWMServoDriver.h> // Include Adafruit PWM Servo Driver Library

// Create Adafruit PWM Servo Driver instance
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Define minimum and maximum pulse lengths for servos
#define XSERVOMIN  140 
#define XSERVOMAX  400
#define YSERVOMIN  280 
#define YSERVOMAX  430

// Camera Characteristics
const int cameraWidth = 480;
const int cameraHeight = 640;
const float FOV_x = 60.0;
const float FOV_y= 45.0;
const float angularDistancePerPixelX = FOV_x/cameraWidth;
const float angularDistancePerPixelY = FOV_y/cameraHeight;

// Offset for the new origin
float originOffsetX = 0.0;
float originOffsetY = 0.0;

struct AngularDistance {
  float xAD;
  float yAD;
};

struct Coordinates {
  float x;
  float y;
};

void setup() {
  Serial.begin(115200); // Start serial communication at 9600 baud rate
  Serial.println("Simplified Eye Mechanism Test");

  pwm.begin(); // Initialize PWM servo driver
  pwm.setPWMFreq(60); // Set PWM frequency for analog servos (~60 Hz)

  pwm.setPWM(1, 0, 0);
  pwm.setPWM(0, 0, 0);

  delay(10);
}

void loop() {
  Coordinates coords = readCoordinates();
  AngularDistance angularDistance = calculateAngularDistance(coords.x, coords.y);
  
  // Map angular distances to servo pulse lengths
  int xServoValue = clampValue(map(angularDistance.xAD, -180, 180, XSERVOMIN, XSERVOMAX), XSERVOMIN, XSERVOMAX);
  int yServoValue = clampValue(map(angularDistance.yAD, -180, 180, YSERVOMIN, YSERVOMAX), YSERVOMIN, YSERVOMAX);

  pwm.setPWM(1, 0, xServoValue);
  pwm.setPWM(0, 0, yServoValue);
  
  delay(10);
  Serial.println("New eye movement!");
}

// Clamping function to make sure values are within servo range
int clampValue(int value, int minVal, int maxVal) {
  if (value < minVal) return minVal;
  if (value > maxVal) return maxVal;
  return value;
}

AngularDistance calculateAngularDistance(int x, int y) {
  AngularDistance result;
  x += originOffsetX;
  y += originOffsetY;
  result.xAD = x * angularDistancePerPixelX;
  result.yAD = y * angularDistancePerPixelY;
  originOffsetX = x;
  originOffsetY = y;
  return result;
}

Coordinates readCoordinates() {
  while (!Serial.available()); // Wait for data
  String input = Serial.readStringUntil('\n');
  input.trim();
  int commaIndex = input.indexOf(',');
  String xString = input.substring(0, commaIndex);
  String yString = input.substring(commaIndex + 1);
  float x = xString.toFloat();
  float y = yString.toFloat();
  Coordinates result = {x, y};
  return result;
}
