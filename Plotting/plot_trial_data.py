import os
import sys
import pylab
import csv
import numpy as np
from collections import defaultdict

files_ = defaultdict(set)

#data_dir_ = '_plots'
#if not os.path.isdir(data_dir_):
#    os.makedirs(data_dir_)

def partition_data(mat):
    blinkVec, timeVec = mat[:,0], mat[:,1]
    i = 0
    result = []
    xvec, yvec = [], []
    for i, t in enumerate(timeVec):
        if t == 11:
            result.append((xvec, yvec))
            xvec, yvec = [], []
            xvec.append(timeVec[i])
            yvec.append(blinkVec[i])
        else:
            xvec.append(timeVec[i])
            yvec.append(blinkVec[i])
    result.append((xvec, yvec))
    return result[1:]

def plot_dir(d, files):
    data = {}
    print("In directory %s total csv files %s" % (d, len(files)))
    for f in files:
        filepath = os.path.join(d, f)
        try:
            x = np.genfromtxt(filepath, delimiter=',', skiprows=3)
            data[filepath] = x
        except:
            print("[WARN] Failed to load %s" % filepath)
        
    for i, k in enumerate(data):
        print("Processing %s" % k)
        pylab.figure()
        d = data[k]
        chunks = partition_data(d)
        length = 0
        i = 0
        for xv, yv in chunks:
            i += 1
            new_xv = [ x + length for x in xv]
            pylab.plot(new_xv, yv, label="%s" % i)
            length += xv[-1]
        pylab.legend(loc='best', framealpha=0.4)
        # baseline 
        baseX, baseY = chunks[0]
        baseline = np.mean(baseY)
        std = np.std(baseY)
        pylab.plot([0, length], [baseline, baseline])
        pylab.plot([baseX[-1], length], [baseline+2*std]*2)
        pylab.plot([baseX[-1], length], [baseline-2*std]*2)
        outfile = os.path.join("%s.png" % k)
        print("[INFO] Saving to %s" % outfile)
        pylab.savefig(outfile)


def plot(**kwargs):
    global files_

    if not os.path.exists('_data'):
        os.makedirs('_data')

    for d in files_:
        files = files_[d]
        plot_dir(d, files)

def main():
    for d, sd, fs in os.walk('.'):
        for f in fs:
            if ".csv" in f:
                files_[d].add(f)
    plot()

if __name__ == '__main__':
    main()
