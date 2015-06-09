#!/usr/bin/env python
import os 
import sys
import time
import serial

ttyName = '/dev/ttyACM1'
baudRate = 9600
if len(sys.argv[1]) < 2:
	outfile = None
else:
	outfile = sys.argv[1]


tty = serial.Serial(ttyName, baudRate, timeout = 1)
with open(outfile, 'w') as f:
print("Writing to file %s" % outfile)
	while(True):
		line = tty.readline()
		f.write("%s" % line)
		print line.strip(' '),

