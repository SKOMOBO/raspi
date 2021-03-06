#!/usr/bin/python

# basic bluetooth script copied from http://blog.whatgeek.com.pt/2015/09/bluetooth-communication-between-raspberry-pi-and-arduino/

# change the bd_addr and get rid of try except if  Ican
import bluetooth


def get_Box_ID():
    f = open("/home/pi/Desktop/raspi/BOX_ID.txt", 'r')
    return f.read()

ID = get_Box_ID()

def store(data):
    the_file = open("/home/pi/Desktop/raspi/Arduino" + ID + ".csv", "a+")
    the_file.write(data)
    the_file.close()


import urllib2
def http_transmit(data):
    url = "http://seat-skomobo.massey.ac.nz/" + data

    print url

    try:
        
        urllib2.urlopen(url)
    # catch all exceptions cus cant afford to have it break in production
    # find out all possible exceptions later
    except:
        print "URL not found / server down / different error"


# checks if the bluetooth connection still exists
def check_connection():
    try:
        sock.getpeername()
        return True
    except:
        return False
    
def http_format(data):

    # from [ hour, minute, second, day, month, year ], PIR, temperature, humidity, CO2, PM1, PM25, PM10

    # to with underscores and the ID

    # [ year, month, day, hour, minute, second ], PM1, PM25, PM10, temperatur, humidity, CO2, PIR

    tokens = data.split(',')

    
    date_time = tokens[0]

    time, date = date_time.split(' ')

    time = time.replace(':', '-')

    day, month, year = date.split('/')

    date = [year, month, day]
    date = '-'.join(date)
    
    reformatted_tokens = [ID, date + '-' + time, tokens[5], tokens[6], tokens[7], tokens[2], tokens[3], tokens[4], tokens[1]]
    return '_'.join(reformatted_tokens)

bd_addr = "98:D3:31:F6:06:9F" #The address from the HC-05 sensor
port = 1
sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)

import sys
import time
# infinitely tries to connect and if it doesnt it just retries
def connect():

    global sock
    
    while(1):
        try:
            print "Connecting to " + bd_addr
            sock.connect((bd_addr,port))
            break
        except:
            print "Connection failed "
            print "Reconnecting to " + bd_addr

            try:
                sock.close()
                sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
                sock.connect((bd_addr,port))
                break
            except KeyboardInterrupt:
                sock.close()
                sys.exit(1)    
            except:
                print "OS error? sleeping for 3 seconds"
                time.sleep(3)
                continue
    return

connect()

# create column headings
print "Initalizing SD card"
store("Time,Moving,Temp,Humid,CO2,Dust 1.0,Dust 2.5,Dust 10\n")


data = ""
while 1:
    print "Collecting data from bluetooth"
    try:

        data += sock.recv(1024)
        data_end = data.find('\n')

        if data_end != -1:
            rec = data[:data_end]
            print "Storing data in sd card " + data
            store(data)

            data = data[data_end+1:]

            print "Transmitting data to server"            
            http_transmit(http_format(rec))
       

    except KeyboardInterrupt:
        break

    # assuming all other errors are caused by bluetooth so try to reconnect
    except:
        print "Some other error occured"

        try:
            connect()
            continue

        # continue doing things anyways
        except:
            continue
    
sock.close()
