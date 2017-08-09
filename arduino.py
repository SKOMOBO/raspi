
# basic bluetooth script copied from http://blog.whatgeek.com.pt/2015/09/bluetooth-communication-between-raspberry-pi-and-arduino/

# change the bd_addr and get rid of try except if  Ican
import bluetooth


def get_Box_ID():
    f = open("Box_ID.txt", 'r')
    return f.read()

ID = get_Box_ID()

def store(data):
    the_file = open("Data" + ID + ".csv", "a+")
    the_file.write(data)
    the_file.close()


import urllib2
def http_transmit(data):
    urllib2.urlopen("http://seat-skomobo.massey.ac.nz/_" + data)

def http_format(data):

	# from hour, minute, second, day, month, year, PIR, temperature, humidity, CO2, PM1, PM25, PM10

	# to with underscores and the ID

	# year, month, day, hour, minute, second, PM1, PM25, PM10, temperatur, humidity, CO2, PIR


bd_addr = "98:D3:31:50:0A:CE" #The address from the HC-05 sensor
port = 1
sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
sock.connect((bd_addr,port))

# create column headings
store("Time,Moving,Temp,Humid,CO2,Dust 1.0,Dust 2.5,Dust 10\n")

data = ""
while 1:
	try:
		data += sock.recv(1024)
		data_end = data.find('\n')
		if data_end != -1:
			rec = data[:data_end]
			print data
			data = data[data_end+1:]
			store(data)
			http_transmit(http_format(data))


	except KeyboardInterrupt:
		break
sock.close()