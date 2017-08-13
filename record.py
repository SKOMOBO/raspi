
import pyaudio
import numpy as np
import audioop

CHUNK = 4096 # number of data points to read at a time
RATE = 44100 # time resolution of the recording device (Hz)

import socket

def pretty_hex(num):
    hex_num = hex(num)[2:]
    
    if hex_num[-1] == 'L': hex_num = hex_num[:-1]
    return hex_num
    
    
def encode(ID, time_sent, DB, Distances):
    
    data = [ID, time_sent, DB] + Distances
    return '_'.join(data)

import time

def get_time():
    return time.strftime("%Y-%m-%d-%H-%M-%S")

import errno
def transmit(data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 81))
        s.send(data)
    
        while(s.recv(2048) != "ack"):

            print "waiting for acknowledgment"
    
    except socket.error as error:
#         print error.errno
        print "tcp error"
        if error.errno == errno.WSAECONNRESET:
            
#         reconnect()
#         retry_action()
            print "not connected to server"
    
    finally:
#     else:
#         raise
        s.close()
    
def store(ID, data):
    the_file = open("Raspi" + ID + ".csv", "a+")
    the_file.write(data)
    the_file.close()

def record_db():
    p=pyaudio.PyAudio() # start the PyAudio class
    stream=p.open(format=pyaudio.paInt16,channels=2,rate=RATE,input=True,
              frames_per_buffer=CHUNK, input_device_index = 1) #uses default input device

    data = np.fromstring(stream.read(CHUNK),dtype=np.int16).astype(np.float)

    # omit outliers
    data[data <= 0.0000000001] = 0

    
    # the rms gives us the power from the amplitude?
    # for proper val compared to background noise need to get samples from mic2 and divide by it

    db = 20 * np.log10(audioop.rms(data, 2))
#     DB.append(db)
   
    stream.stop_stream()
    stream.close()
    p.terminate()
    return db

def get_Box_ID():
    f = open("Box_ID.txt", 'r')
    return f.read()


## just in case Im stuck with HTTP
import urllib2
def http_transmit(data):
    urllib2.urlopen("http://seat-skomobo.massey.ac.nz/raspi/" + data)


def style(time_sent, DB, Distances):
    data = [time_sent, DB] + Distances
    return ','.join(data)

# Run the code


# fetch box ID 

ID = get_Box_ID()
hex_ID = pretty_hex(int(ID))

store(ID, "Time,Decibels,Distance1,Distance2,Distance3,Distance4,Distance5,Distance6,Distance7")

while(True):

    db = record_db()
    hex_db = pretty_hex(db)

# get real distance values

    hex_distances = map(pretty_hex, [41, 23, 12, 20, 1, 49, 100])
    packet = encode(hex_ID, get_time(), hex_db, hex_distances, '_')

    store(ID, style(get_time(), db, distances, ','))
    http_transmit(packet)

    print packet