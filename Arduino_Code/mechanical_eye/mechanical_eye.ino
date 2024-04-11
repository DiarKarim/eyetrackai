#include <Wire.h> // Include Wire library for I2C communication
#include <Adafruit_PWMServoDriver.h> // Include Adafruit PWM Servo Driver Library

// Create Adafruit PWM Servo Driver instance
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Define minimum and maximum pulse lengths for servos
#define XSERVOMIN  140 
#define XSERVOMAX  400
#define YSERVOMIN  280 
#define YSERVOMAX  430

// Define minimum and maximum angles for x and y directions
// #define XANGLEMAX 75
// #define XANGLEMIN 150
// #define YANGLEMAX -30
// #define XANGLEMIN 30


// Camera Characteristics

// Resolution
const int cameraWidth = 640;
const int cameraHeight = 480;

const float FOV_x = 60.0;
const float FOV_y= 45.0;

const float angularDistancePerPixelX = FOV_x/cameraWidth;
const float angularDistancePerPixelY = FOV_y/cameraHeight;

// Offset for the new origin
float originOffsetX = 0.0;
float originOffsetY = 0.0;

// Used to return angular distance to the monitor
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
  // Takes x and y values from Serial Monitor for now, could connect with python for example?
  // float x = readSerialFloat();
  // float y = readSerialFloat();

  Coordinates coords = readCoordinates();
  float x = coords.x;
  float y = coords.y;

  AngularDistance angularDistance = calculateAngularDistance(x, y);
  
  // Map angular distances to servo pulse lengths
  int xServoValue = map(angularDistance.xAD, -180, 180, XSERVOMIN, XSERVOMAX);
  int yServoValue = map(angularDistance.yAD, -180, 180, YSERVOMIN, YSERVOMAX);

  pwm.setPWM(1, 0, xServoValue);
  pwm.setPWM(0, 0, yServoValue);
  
  delay(10);
  Serial.println("New eye movement!");
}


// Theoretically take an X and Y coordinate (pixel?) and convert it into angular distance depending on the camera specification
AngularDistance calculateAngularDistance(int x, int y) {
  AngularDistance result;

  x += originOffsetX;
  y += originOffsetY;

  // Use the calculated ADPP to convert pixel coordinates to angular distance per components
  result.xAD = x * angularDistancePerPixelX;
  Serial.print(x);
  Serial.print(" in x angular distance is ");
  Serial.println(result.xAD);

  result.yAD = y * angularDistancePerPixelY;
  
  Serial.print(y);
  Serial.print(" in y angular distance is ");
  Serial.println(result.yAD);

  // The prints gives out the new position that the eyes are looking at and their angular distance.

//  originOffsetX = x;
//  originOffsetY = y;

  return result;
}

// Takes inputs from the Serial Monitor
// float readFloat() {
//   while (!Serial.available()); // Wait for data
//   return Serial.parseFloat();   // Read the float
// }

Coordinates readCoordinates() {
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
  Coordinates result = {x, y};
  return result;
}
