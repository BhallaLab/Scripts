#!/usr/bin/env python
from __future__ import print_function 

import os 
import sys
import time
import serial
from collections import defaultdict

import datetime
stamp = datetime.datetime.now().isoformat()

if not os.path.isdir(stamp):
    os.makedirs(stamp)

acmports = range(5)
ttyoptions = [ "/dev/ttyACM%s" % x for x in acmports ]
ttyName = '/dev/ttyACM0'

runningTrial = "1"
trialsDict = defaultdict(list)
trialsDict[runningTrial] = []

mouseName = None

if len(sys.argv) <= 2:
    outfile = os.path.join(stamp, "raw_data")
else:
    outfile = sys.argv[1]

tty = None
baudRate = 9600
for t in ttyoptions:
    try:
        tty = serial.Serial(t, baudRate, timeout = 1)
    except Exception as e:
        print("[WARN] Failed to connect to %s with error %s" % (t, e))
        continue

def writeToTrialFile(line):
    global newTrialFile
    global runningTrial 
    if "end of trial:" in line.lower():
        newTrialFile = os.path.join(stamp, "Trial_%s" % runningTrial)
        print("[INFO] Writing trial %s to %s" % (runningTrial, newTrialFile))
        with open(newTrialFile, "w") as tf:
            tf.write("".join(trialsDict[runningTrial]))
    elif "trial no." in line.lower():
        runningTrial = line.lower().replace("trial no.", "").strip()
        print("---------------------------------")
        print("[INFO] New trial %s has started" % runningTrial)
    else:
        trialsDict[runningTrial].append(line)
    
print("[INFO] Connecting to %s" % ttyName)
with open(outfile, 'w') as f:
    print("[INFO] Writing to file %s" % outfile)
    while(True):
        line = tty.readline()
        print("\t%s" % line.strip(' '), end='')
        f.write("%s" % line)
        writeToTrialFile(line)
