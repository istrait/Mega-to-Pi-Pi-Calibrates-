// Version of the program that just pulls the sensor voltages to to the Pi

// Add required libraries
#include <Adafruit_Sensor.h>
#include <DHT.h>

// Setup DHT22
#define DHTPIN 4   
#define DHTTYPE DHT22  // #define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

//Defining ports for inputs
  int sensor1Port = A0; //Thermometer
  int sensor2Port = A1; //Anemometer
  int sensor3Port = A2; //Pyranometer
  int sensor4Port = A3; //Humidity
  int sensor5Port = A4; //Barometer
  int sensor6Port = A5; //
  int sensor7Port = A6; //
  int sensor8Port = A7; //
  int sensor9Port = A8; //
  int sensor10Port = A9; //
  int sensorwindvane = A9;

// Create the dataString
  String dataString;

void setup() {
  // put your setup code here, to run once:
   Serial.begin(9600);
   pinMode(13, OUTPUT);
}

void loop() {
    //DHT22 readings
  float h = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();

    // Create the String to send to the Pi and send it
    dataString = (String(t) + ',' + String(h) + ',' + String(analogRead(sensor1Port)) + ',' + String(analogRead(sensor2Port)) + ',' + String(analogRead(sensor3Port)) + ',' + String(analogRead(sensor4Port)) + ',' + String(analogRead(sensor5Port)) + ',' + String(analogRead(sensor6Port)) + ',' + String(analogRead(sensor7Port)) + ',' + String(analogRead(sensor8Port)) + ',' + String(analogRead(sensor9Port)) + ',' + String(analogRead(sensor10Port)) '+' + String(analogRead(sensorwindvane)));
    Serial.println(dataString); 
    
    // Delay for 5 minutes
    delay(300000);
}
