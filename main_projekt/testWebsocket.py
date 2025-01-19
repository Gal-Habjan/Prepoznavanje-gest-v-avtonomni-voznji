import serial
import struct

ser = serial.Serial('COM8', 9600, timeout=1)

command = 4

data = struct.pack('B', command)

ser.write(data)