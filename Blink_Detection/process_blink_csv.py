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

def plot_data(data, nplots = 3):
    tvec, yvec = data[:,0], data[:,1]
    pylab.subplot(nplots, 1, 1)
    pylab.plot(tvec, yvec, label = 'Pupil size (raw)')
    pylab.legend()

    window_size = 7
    yvec = np.convolve(yvec, np.ones(window_size)/window_size, 'same')
    pylab.subplot(nplots, 1, 2)
    pylab.plot(tvec, yvec, label='Window size = %s' % window_size)
    pylab.plot([0, tvec[-1]], [np.mean(yvec)]*2, label = 'Mean pupil size')
    pylab.legend()


    pylab.subplot(nplots, 1, 3)
    pylab.plot(tvec[1:], np.diff(yvec), label = "First diff")
    pylab.legend()

    pylab.xlabel("Time (seconds)")
    pylab.show()

def find_blinks(data, threshold = None, **kwargs):
    """Find location of blinks in data"""
    tvec, yvec = data[:,0], data[:,1]
    yvecDiff = np.diff(yvec)
    

def process_csv(csv_file):
    data = np.genfromtxt(csv_file, skiprows=1, delimiter=",")
    plot_data(data)
    blinks = find_blinks(data)
    print blinks

def main():
    csvFile = sys.argv[1]
    process_csv(csvFile)

if __name__ == '__main__':
    main()
