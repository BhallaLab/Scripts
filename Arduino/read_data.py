#!/usr/bin/env python
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
    outfile = "%s/raw_data" % stamp
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
    if "End of Trial:" in line:
        newTrialFile = os.path.join(stamp, "Trial_%s" % runningTrial)
        print("[INFO] Wrting trial to %s" % newTrialFile)
        with open(newTrialFile, "w") as tf:
            tf.write("\n".join(trialsDict[runningTrial]))
        runningTrial = line.replace("End of Trial:", "").strip()
    else:
        trialsDict[runningTrial].append(line)
    
print("Connecting to %s" % ttyName)
with open(outfile, 'w') as f:
    print("Writing to file %s" % outfile)
    while(True):
        line = tty.readline()
        print line.strip(' '),
        f.write("%s" % line)
        writeToTrialFile(line)
