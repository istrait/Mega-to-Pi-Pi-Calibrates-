import sys
import serial
import datetime
from time import sleep
import time
# import picamera
import subprocess
import math

slope = [22.37, 250, 30.43, 6.825]
intercept = [-22.37, 0, -25.81, 76.29375]
raw_data = []
submit_data = []

# Calculates calibrated values
def calculate(slope, intercept, data):
        Voltage = (data / 1023) * 5.0
        CalibratedReading = intercept + Voltage * slope
        submit_data.append(CalibratedReading) # Add to submit list

def Barometer_Calc(slope, intercept, data, i): # Specifically for Barometer
        Voltage = (data / 1023) * 5.0
        CalibratedReading = 76.29375 + Voltage * 6.825
        CalibratedReading = CalibratedReading * .295 #Convert to Hg
        submit_data.append(CalibratedReading) # Add to submit list

def Anemometer_Calc(slope, intercept, data, i): # Specifically for Anemometer
        Voltage = (data / 1023) * 5.0
        CalibratedReading = intercept + Voltage * slope
        CalibratedReading = CalibratedReading - 2
        submit_data.append(CalibratedReading) # Add to submit list

while True:
        print('Waiting for data.....')
        ser = serial.Serial('/dev/ttyACM0', 9600)

        # Read a line and convert it from b'xxx\r\n' to xxx
        data = ser.readline().decode('utf-8')  #[:-2]
        # Create Date / Time stamp
        now_string = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
        # Print to console
        print(now_string)
        print(data) #Raw data from Arduino
        # Split the data into variables, send to list as floating point variables and start submit_data list
        Int_Temp, Int_humid, Temp_data, Anem, Pyran, Hum, Bar = data.split(',')
        raw_data = [float(Int_Temp), float(Int_humid), float(Temp_data), float(Anem), float(Pyran), float(Hum), float(Bar)]
        submit_data = [float(Int_Temp), float(Int_humid)]

        # Code to calculate calibrated Temperature Sensor vlaue
        Resistance = ( 15000 * raw_data[2] /(1024 - raw_data[2])) # Pull raw Temp sensor value and calc resistance
        Temp_log = math.log(Resistance); # Saving the Log(resistance) so not to calculate  it 4 times later
        Temp = 1 / (0.00102119 + (0.000222468 * Temp_log) + (0.000000133342 * Temp_log * Temp_log * Temp_log))
        Temp = Temp - 273.15                             # Convert Kelvin to Celsius                      
        submit_data.append(Temp) # Add to submit list


        #for loop to iterate values to calculation function (remembering that the slope list does not include the first 43 values
        for i in range(0, len(slope)):
                # Send data to calculation function
                if slope[i] == 6.825:
                        print('Barometer Function Activated')
                        Barometer_Calc(slope[i], intercept[i], raw_data[i+3], i)
                elif slope[i] == 22.37:
                        print('Anemometer Function Activated')
                        Anemometer_Calc(slope[i], intercept[i], raw_data[i+3], i)
                else:
                        calculate(slope[i], intercept[i], raw_data[i+3])

        # Send to PHP file with arguments (Is a test file that shows in terminal for now)
        print('Result from Mohawk:')
        subprocess.call(["php","-f","/var/www/html/db.php", Int_Temp, Int_humid, str(submit_data[2]), str(submit_data[3]), str(submit_data[4]), str(submit_data[5]), str(submit_data[6])])

        print(submit_data)
        
        # Clear data lists
        del raw_data[:]
        del submit_data[:]
