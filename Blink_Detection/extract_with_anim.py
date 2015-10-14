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
import extract
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

axes_ = {}
lines_ = {}
ax1 = fig_.add_subplot(2, 1, 1)
ax2 = ax1.twinx()
ax3 = fig_.add_subplot(2, 1, 2)
ax4 = ax3.twinx()

axes_ = { 'raw' : ax1, 'raw_twin' : ax2, 'blink' : ax3, 'blink_twin' : ax4 }
lines_["rawA"] = ax1.plot([], [], color='blue')[0]
lines_["rawB"] = ax2.plot([], [], color='red')[0]
lines_['blinkA'] = ax3.plot([], [], 's', color = 'blue')[0]
lines_['blinkB'] = ax4.plot([], [], 'p', color = 'red')[0]

time_template_ = 'Time = %.1f s'
time_text_ = fig_.text(0.05, 0.9, '', transform=axes_['blink'].transAxes)
cv2.namedWindow('image')

tvec_ = []
y1_ = []
y2_ = []

def init():
    global data_, axes_, lines_
    global box_, fps_
    global cap_
    videoFile = sys.argv[1]
    cap_ = cv2.VideoCapture(videoFile)
    fps_ = cap_.get(cv2.cv.CV_CAP_PROP_FPS)
    ret, fstFrame = cap_.read()
    box_ = webcam.get_bounding_box(fstFrame)
    try:
        cv2.destroyWindows('Bound_eye')
    except Exception as e:
        pass
    return lines_.values()

def update_axis_limits(ax, x, y):
    xlim = ax.get_xlim()
    if x >= xlim[1]:
        ax.set_xlim(xlim[0], x+10)

    ylims = ax.get_ylim()
    if y >= ylims[1]:
        ax.set_ylim(ylims[0], y+1)

def animate(i):
    global data_
    global time_text_
    global box_
    global tvec_, y1_, y2_
    global cap_

    t = float(i) / fps_
    ret, img = cap_.read()
    (x0, y0), (x1, y1) = box_
    frame = img[y0:y1,x0:x1]
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    # display the whole frame in opencv2. Very cool.
    cv2.imshow("image", frame)
    cv2.waitKey(1)

    inI, outI, edge, pixal = webcam.process_frame(gray)
    tvec_.append(t); y1_.append(edge); y2_.append(pixal)
    update_axis_limits(axes_['raw'], t, edge)
    update_axis_limits(axes_['raw_twin'], t, pixal)

    lines_['rawA'].set_data(tvec_, y1_)
    lines_['rawB'].set_data(tvec_, y2_)
    
    if i % int(fps_) == 0 and i > int(fps_)*5:
        data_ = np.array((tvec_, y1_, y2_)).T
        tA, bA = extract.find_blinks_using_edge(data_)
        tB, bB = extract.find_blinks_using_pixals(data_)
        update_axis_limits(axes_['blink'], t, 1)
        update_axis_limits(axes_['blink_twin'], t, 1)
        lines_['blinkA'].set_data(tA, 0.9*np.ones(len(tA)))
        lines_['blinkB'].set_data(tB, np.ones(len(tB)))

    time_text_.set_text(time_template_ % t)
    return lines_.values(), time_text_

ani_ = anim.FuncAnimation(fig_
        , animate
        , init_func=init
        , blit = False
        , interval = 1
        , repeat = False
        )

plt.show()
cap_.release()
cv2.destroyAllWindows()

outfile = '%s_out.csv' % sys.argv[1]
print("[INFO] Writing to file %s" % outfile)
np.savetxt(outfile, data_, delimiter=',' ,header="time,edge,pixal")
