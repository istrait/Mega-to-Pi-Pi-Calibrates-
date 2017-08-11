import sys
import serial
import datetime
from time import sleep
import time
# import picamera
import subprocess
import math
import csv


with open('calibrations.csv', 'rU') as f:  #opens PW file
    reader = csv.reader(f)
    # Print every value of every row and convert the strings to floats.
    calib_data = list(list(rec) for rec in csv.reader(f, delimiter=',')) #reads csv into a list of lists
    calib_data[1] = list(map(float, calib_data[1]))
    calib_data[2] = list(map(float, calib_data[2]))
print(calib_data)

# Initialize and clear the lists needed for the program.
raw_data = []
submit_data = []

# Calculates calibrated values
def Calculate(slope, intercept, data): # For generic calculations
        Voltage = (data / 1023) * 5.0
        CalibratedReading = intercept + Voltage * slope
        submit_data.append(CalibratedReading) # Add to submit list

def Barometer_Calc(slope, intercept, data): # Specifically for Barometer
        Voltage = (data / 1023) * 5.0
        CalibratedReading = 76.29375 + Voltage * 6.825
        CalibratedReading = CalibratedReading * .295 #Convert to Hg
        submit_data.append(CalibratedReading) # Add to submit list

def Anemometer_Calc(slope, intercept, data): # Specifically for Anemometer
        Voltage = (data / 1023) * 5.0
        CalibratedReading = intercept + Voltage * slope
        CalibratedReading = CalibratedReading - 2 # To bring it closer to 0 when still
        submit_data.append(CalibratedReading) # Add to submit list

def Thermister_Calc(data):
        Resistance = ( 15000 * data /(1024 - data) ) # Pull raw Temp sensor value and calc resistance
        Temp_log = math.log(Resistance); # Saving the Log(resistance) so not to calculate  it 4 times later
        Temp = 1 / (0.00102119 + (0.000222468 * Temp_log) + (0.000000133342 * Temp_log * Temp_log * Temp_log))
        Temp = Temp - 273.15                             # Convert Kelvin to Celsius
        submit_data.append(Temp) # Add to submit list

while True:
        print('Waiting for data.....')
        ser = serial.Serial('/dev/ttyACM0', 9600)

        # Read a line and convert it from b'xxx\r\n' to xxx
        data = ser.readline().decode('utf-8').strip('\r\n')  #[:-2]
        # Create Date / Time stamp
        now_string = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
        # Print to console
        print(now_string)
        print(data) #Raw data from Arduino
        raw_data = [int(e) if e.isdigit() else e for e in data.split(',')] # Splits data into a list of numbers
        print(raw_data) # Shows raw numbers
        submit_data = [float(raw_data[0]), float(raw_data[1])] #Ad the first two values to the data_submit string as they are already calibrated


        #for loop to iterate values to calculation function (remembering that the slope list does not include the first 3 values)
        for i in range(0, len(calib_data[1])):  
                        # Send data to calculation function
                        if calib_data[1][i] == 6.825:
                                print('Barometer Function Activated')
                                Barometer_Calc(calib_data[1][i], calib_data[2][i], raw_data[i+2])
                        elif calib_data[1][i] == 22.37:
                                print('Anemometer Function Activated')
                                Anemometer_Calc(calib_data[1][i], calib_data[2][i], raw_data[i+2])
                        elif calib_data[1][i] == 0 and calib_data[2][i] == 0:
                                print('Thermister Function Activated')
                                Thermister_Calc(raw_data[i+2])
                        else:
                                print('Normal Calibration Function Activated')
                                Calculate(calib_data[1][i], calib_data[2][i], raw_data[i+2])


        # Send to PHP file with arguments (Is a test file that shows in terminal for now)
        print('Result from Mohawk:')
        print(submit_data)
        subprocess.call(["php","-f","/var/www/html/db.php", str(submit_data[0]), str(submit_data[1]), str(submit_data[2]), str(submit_data[3]), str(submit_data[4]), str(submit_data[5]), str(submit_data[6])])

        # Clear data lists
        del raw_data[:]
        del submit_data[:]
