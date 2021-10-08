import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import threading
import time
import datetime
import RPi.GPIO as GPIO


timesplit = 1
time_counter = 0
btn_press = 24
S_rates = [1,5,10]
On = True
startTime = time.time()
GPIO.cleanup()

def test(channel):
    print("press received")


def buttonboi(channel):

    global S_rates
    global timesplit
    global time_counter
    time_counter = time_counter + 1



    if time_counter == 3:
        time_counter = 0

    timesplit = S_rates[time_counter]
    print("Sampling rate changed to " + str(timesplit))


GPIO.setup(btn_press, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.add_event_detect(btn_press, GPIO.FALLING, callback=buttonboi, bouncetime=200) 


#create the spi BUS
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

#create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 2
light_chan = AnalogIn(mcp, MCP.P2)
temp_chan = AnalogIn(mcp, MCP.P1)


def printdata():
    global On
    global timesplit
    global startTime

    while On:
        readTime = time.time()-startTime
        readTime = int(readTime)
        temp = temp_chan.voltage
        tempC = (temp-0.5)*100
        tempC = str(abs(tempC))+"C"
        light = light_chan.value
        print(str(readTime)+ '\t\t' + str(temp_chan.value) + '\t\t' + str(tempC) + '\t\t' + str(light))
        time.sleep(timesplit) 



threadStart = threading.Thread(target = printdata)
threadStart.start()
print("starting \n Press 'q' to quit")
while On:
    end = input("Runtime\t\tTemp Reading\tTemp\t\t\tLight Reading\n")

    if(end == "q"):
        On = False
