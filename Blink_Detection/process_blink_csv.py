#!/usr/bin/env python
"""process_blink_csv.py: 

    Process the csv file and extract the blink data.

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2015, Dilawar Singh and NCBS Bangalore"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import numpy as np
import pylab
import sys
from collections import OrderedDict

window_size_ = 7
# The mean area multiplied by this factor. Anything below this belongs to blink
# zone.
threshold_factor_area_ = 0.5

def plot_data(data, nplots = 4):
    global window_size_
    window = np.ones(window_size_) / window_size_
    tvec, yvec = data[:,0], data[:,1]
    pylab.subplot(nplots, 1, 1)
    pylab.plot(tvec, yvec, label="raw data")
    pylab.legend()

    yvec = np.convolve(yvec, window, 'same')
    pylab.subplot(nplots, 1, 2)
    pylab.plot(tvec, yvec, label='Window size = %s' % window_size_)
    pylab.plot([0, tvec[-1]], [0.5*np.mean(yvec)]*2, label = '0.5*Mean pupil size')
    pylab.legend()

    pylab.subplot(nplots, 1, 4)
    # When area reduces to half of eye pupil, it should be considered.
    newY = 0.5*yvec.mean() - yvec
    newY = newY + np.fabs(newY)
    window = np.ones(3*window_size_)/(3*window_size_)

    yy = np.convolve(newY, window, 'same')
    pylab.plot(tvec, yy, label='Blinks')

    pylab.xlabel("Time (seconds)")
    outfile = 'output.png'
    print("[INFO] Writing to %s" % outfile)
    pylab.savefig(outfile)

def plot_records(records):
    for i, k in enumerate(records):
        pylab.subplot(len(records), 1, i+1)
        d = records[k]
        if len(d) < 3:
            pylab.plot(d[0], d[1], label=str(k))
        else:
            pylab.plot(d[0], d[1], d[2], label=str(k))
        pylab.legend()
    pylab.xlabel("Time (seconds)")
    outfile = "output.png"
    print("[INFO] Writing to %s" % outfile)
    pylab.savefig(outfile)

def is_a_blink(i, tvec, yvec, yvec_diff):
    """Check if there is a blink at the given indices """
    print("|| Checking at %s, time = %s" % (i, tvec[i]))
    print yvec_diff[i-10:i+10]
    return True

def remove_blink(i, yy):
    # Go left and right and set pixals to 0 as long as they are decreasing on
    # the left and right.
    #print("Using index: %s, %s" % (i, yy[i]))
    area, start = yy[i], yy[i]
    x = i+1
    while  x < len(yy) and yy[x] <= start:
        start = yy[x]
        yy[x] = 0
        x += 1
        area += start

    start = yy[i]
    x = i - 1
    while x > 0 and yy[x] <= start:
        start = yy[x]
        yy[x] = 0
        x -= 1
        area += start
    yy[i] = 0.0
    return area

def find_blinks(data, plot = False, **kwargs):
    """Find location of blinks in data"""
    global window_size_
    records = OrderedDict()
    window = np.ones(window_size_)/window_size_
    t, y = data[:,0], data[:,1]
    # Smooth out the vectors.
    yvec = np.convolve(y, window, 'same')
    records['Smooth'] = (t, y)
    newY = 0.5*yvec.mean() - yvec
    newY = newY + np.fabs(newY)
    window = np.ones(window_size_)/(window_size_)
    yy = np.convolve(newY, window, 'same')

    blinks = []
    while yy.max() > 10:
        i = np.argmax(yy)
        a = remove_blink(i, yy)
        blinks.append((i, a))

    xvec, yvec = [], []
    for i, x in sorted(blinks):
        xvec.append(t[i])
        yvec.append(x)
    records['Computed blinks'] = (xvec, yvec, '+')

    if plot:
        plot_records(records)
    

def process_csv(csv_file):
    data = np.genfromtxt(csv_file, skiprows=1, delimiter=",")
    d = data #[:1000,:]
    blinks = find_blinks(d, plot = True)

def main():
    csvFile = sys.argv[1]
    process_csv(csvFile)

if __name__ == '__main__':
    main()
