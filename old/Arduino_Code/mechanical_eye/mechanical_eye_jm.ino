#include <Wire.h> // Include Wire library for I2C communication
#include <Adafruit_PWMServoDriver.h> // Include Adafruit PWM Servo Driver Library

// Create Adafruit PWM Servo Driver instance
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Define minimum and maximum pulse lengths for servos
#define XSERVOMIN  140 
#define XSERVOMAX  400
#define YSERVOMIN  280 
#define YSERVOMAX  430

struct Angles {
  float x;
  float y;
};

void setup() {
  Serial.begin(115200); // Start serial communication at 9600 baud rate
  Serial.println("Mechanical Eye Movements");

  pwm.begin(); // Initialize PWM servo driver
  pwm.setPWMFreq(60); // Set PWM frequency for analog servos (~60 Hz)

  delay(10);
}

void loop() {
  Angles angles = readAngles();
  float x = angles.x;
  float y = angles.y;

  // Map angular distances to servo pulse lengths and clamps the values
  int xServoValue = clampValue(x, XSERVOMIN, XSERVOMAX);
  int yServoValue = clampValue(y, YSERVOMIN, YSERVOMAX);

  pwm.setPWM(1, 0, x);
  pwm.setPWM(0, 0, y);
  
  delay(10);
  Serial.println("New eye movement!");
}

// Clamping function to make sure values are within servo range
int clampValue(int value, int minVal, int maxVal) {
  if (value < minVal) return minVal;
  if (value > maxVal) return maxVal;
  return value;

Angles readAngles() {
  while (!Serial.available()); // Wait for data

  // Read the input in the format "(x,y)"
  String input = Serial.readStringUntil('\n');

  // Remove the parentheses and split the string into two parts
  input.trim();
  int commaIndex = input.indexOf(',');
  
  // Extract x and y components
  String xString = input.substring(0, commaIndex);
  String yString = input.substring(commaIndex + 1);

  // Convert strings to floats
  float x = xString.toFloat();
  float y = yString.toFloat();

  // Create and return a Coordinates struct
  Angles result = {x, y};
  return result;
}
