#!/usr/bin/env python
"""Extract blink data and visualize it using matplotlib.


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
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import pylab
import sys
from collections import OrderedDict
import cv2
import webcam

window_size_ = 7
# The mean area multiplied by this factor. Anything below this belongs to blink
# zone.
threshold_factor_area_ = 0.5

######################################
# Initialize animation here 

data_ = None
cap_ = None
box_ = []
fig_ = plt.figure()
fps_ = 0.0
ax_ = fig_.add_subplot(2,1,2)
axv_ = fig_.add_subplot(2,1,1)
line1_, = ax_.plot([], [], 'bo', alpha=0.4)
line2_, = ax_.plot([], [], 'bo', alpha=0.4)
time_template_ = 'Time = %.1f s'
time_text_ = ax_.text(0.05, 0.9, '', transform=ax_.transAxes)
cv2.namedWindow('image')

def init():
    global data_, ax_, line1_, line2_, cap_
    global box_, fps_

    videoFile = sys.argv[1]
    cap_ = cv2.VideoCapture(videoFile)
    fps_ = cap_.get(cv2.cv.CV_CAP_PROP_FPS)
    ret, fstFrame = cap_.read()
    box_ = webcam.get_bounding_box(fstFrame)
    try:
        cv2.destroyWindows('Bound_eye')
    except Exception as e:
        pass
    ax_.set_xlim(0, int(cap_.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)/fps_))
    ax_.set_ylim(-10, 100)
    line1_.set_data([], [])
    line2_.set_data([], [])
    return line1_, line2_

def animate(i):
    global data_
    global time_text_, line_
    global box_
    t = float(i) / fps_
    ret, img = cap_.read()
    (x0, y0), (x1, y1) = box_
    frame = img[y0:y1,x0:x1]
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    # display the whole frame in opencv2. Very cool.
    cv2.imshow("image", frame)
    cv2.waitKey(1)

    #axv_.imshow(frame)
    inI, outI, edge, pixal = webcam.process_frame(gray)
    if t >= ax_.get_xlim()[1]:
        ax_.set_xlim(0, 1.5*t)
    ylims = ax_.get_ylim()
    if edge >= ylims[1]:
        ax_.set_ylim(ylims[0], 1.5*edge)
    line1_.set_data(t, edge)
    time_text_.set_text(time_template_ % t)
    return line1_, line2_, time_text_

ani_ = anim.FuncAnimation(fig_, animate
        , init_func=init
        , blit = False
        , interval = 10
        , repeat = False
        )

plt.show()
cap_.release()
cv2.destroyAllWindows()
quit()


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


def get_blink(i, yy, threshold = 10.0):
    # Go left and right and set pixals to 0 as long as they are decreasing on
    # the left and right.
    #print("Using index: %s, %s" % (i, yy[i]))
    start = yy[i]
    left, right = [], []
    x = i+1
    while  x < len(yy) and 0.1 < yy[x] <= start:
        start = yy[x]
        yy[x] = 0
        x += 1
        left.append(start)

    start = yy[i]
    x = i - 1
    while x > 0 and 0.1 < yy[x] <= start:
        start = yy[x]
        yy[x] = 0
        x -= 1
        right.append(start)
    yy[i] = 0.0
    w = left + right
    if len(w) == 0:
        return False, 0
    res = sum(w) / len(w)
    if res < threshold:
        return False, 0.0
    return True, res

def find_blinks_using_edge(data, plot = False, **kwargs):
    """Find location of blinks in data"""
    global window_size_
    records = OrderedDict()
    window = np.ones(window_size_)/window_size_
    t, y = data[:,0], data[:,1]
    # Smooth out the vectors.
    yvec = np.convolve(y, window, 'same')
    records['smooth'] = (t, y)
    newY = 0.5*yvec.mean() - yvec
    newY = newY + np.fabs(newY)
    window = np.ones(window_size_)/(window_size_)
    yy = np.convolve(newY, window, 'same')
    blinks = []
    while yy.max() > 10:
        i = np.argmax(yy)
        isBlink, a = get_blink(i, yy)
        if isBlink:
            blinks.append((i, a))

    xvec, yvec = [], []
    for i, x in sorted(blinks):
        xvec.append(t[i])
        yvec.append(x)
    return xvec, yvec

def find_blinks_using_pixals(data, plot = False):
    t, y, w = data[:,0], data[:,1], data[:,2]
    # must be odd.
    windowSizeSec = 6
    N = windowSizeSec*32.0
    window = np.ones(N)/N
    smoothW = np.convolve(w, window, 'valid')
    if plot:
        pylab.subplot(2, 1, 1)
        pylab.plot(t, w, linewidth=0.5, label = "W")

    # Shift because of convolution.
    x = int(N) / 2
    bT, yy = t[x-1:-x], w[x-1:-x] - smoothW

    if plot:
        pylab.plot(bT, smoothW, linewidth=2, label = "Smooth W")
        pylab.legend()
        pylab.subplot(2, 1, 2)

    win = np.ones(2) / 2.0
    yy = np.convolve(yy, win, 'same')
    yy = (yy + np.fabs(yy))
    if plot:
        pylab.plot(bT, yy, linewidth=1, alpha=0.4, label = "W - Smooth W")
        pylab.legend()

    # Find blink in this data.
    blinks = []
    while yy.max() > 10.0:
        i = np.argmax(yy)
        isBlink, a = get_blink(i, yy, 8.0)
        if isBlink:
            blinks.append((i, a))

    xvec, yvec = [], []
    for i, x in sorted(blinks):
        xvec.append(bT[i])
        yvec.append(x)
    return xvec, yvec

def process_csv(csv_file):
    data = np.genfromtxt(csv_file, skiprows=1, delimiter=",")
    d = data #[:1000,:]
    blinkA = find_blinks_using_edge(d)
    print("Total blink using edges: %s" % len(blinkA[0]))
    blinkB = find_blinks_using_pixals(d)
    print("Total blinks using pixals: %s" % len(blinkB[0]))
    pylab.plot(blinkA[0], 1+np.zeros(len(blinkA[0])), '+', lw = 10)
    pylab.plot(blinkB[0], 0.1+np.ones(len(blinkB[0])), '+', lw = 10)
    pylab.legend()
    pylab.ylim(0.6, 1.5)
    pylab.show()


def main():
    csvFile = sys.argv[1]
    process_csv(csvFile)

if __name__ == '__main__':
    main()
