#!/usr/bin/env python3

__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2019-, Dilawar Singh"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"

import sys
import os
import matplotlib as mpl
# mpl.use( 'pgf' )
import matplotlib.pyplot as plt
mpl.style.use( ['bmh', 'fivethirtyeight'] )
import numpy as np
import pickle
import scipy.stats as stats
from collections import Counter
from datetime import datetime
import pandas as pd

def parse_date(date):
    date = date.split('to')[0].strip()
    return datetime.strptime(date, '%Y-%m-%d')

def reformat(xs):
    xs[0] = xs[0].split('to')[0].strip()
    return xs

def plot_together(df, outfile):
    plt.figure(figsize=(12, 10))
    gridSize = (3, 2)
    ax1 = plt.subplot2grid( gridSize, (0,0), colspan = 1 )
    axt = plt.subplot2grid( gridSize, (1,0), colspan = 2 )
    ax2 = plt.subplot2grid( gridSize, (0,1), colspan = 1 )
    ax3 = plt.subplot2grid( gridSize, (2,0), colspan = 1 )
    ax4 = plt.subplot2grid( gridSize, (2,1), colspan = 1 )

    # distribution by day.
    data = df['datetime']
    days = [int(x.strftime('%w')) for x in data]
    hist = Counter(days)
    xs = range(7)
    ys = [hist[x] for x in xs]
    N = sum(ys)
    ysn = [hist[x]/N for x in xs]
    ax11 = ax1.twinx()
    ax11.plot(xs, ysn, '-o', color='red')
    ax11.set_ylim(bottom=0)
    ax11.set_ylabel('frac', fontsize='small')
    ax1.set_title('a) By Day')
    ax1.bar(xs, ys)
    ax1.set_xticks(xs)
    ax1.set_xticklabels(['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            , fontsize=10
            )

    # distribution by time.
    hours = [int(x.strftime('%H')) for x in data]
    hist = Counter(hours)
    xs = range(24)
    ys = [hist[x] for x in xs]
    N = sum(ys)
    axt.plot(xs, ys, label='Avg')
    # day wise
    for day in range(7):
        print( f"[INFO ] Plotting for {day}" )
        ddata = [ x for x in data if int(x.strftime('%w')) == day]
        hours = [int(x.strftime('%H')) for x in ddata]
        hist = Counter(hours)
        xs = range(24)
        ys = [hist[x] for x in xs]
        axt.plot(xs, ys, marker=f'${day}$', lw=1, linestyle='--', alpha=0.6, label=f'Day {day}')
    axt.set_title('c) By time')
    axt.set_xticks(xs)
    axt.set_xlabel( 'Hour')
    axt.legend(loc='upper left', bbox_to_anchor=(1,1))

    # distribution by month.
    temps = [20.8,22.9,25.5,27.1,26.9,24.4,23.3,23.4,23.2,23.1,21.8,20.7]
    months = [int(x.strftime('%m')) for x in data]
    hist = Counter(months)
    xs = range(1, 13)
    ys = [hist.get(x, 0) for x in xs]
    ax2.bar(xs, ys)
    ax2.set_xticks(xs)
    ax2.set_title('b) By Month')
    ax22 = ax2.twinx()
    ax22.plot(xs, temps, color='red', alpha=0.5)
    ax22.set_ylim(bottom=17)
    ax22.set_ylabel('Avg Temp of Bangalore')
    # correlation between temp and labnotes.
    slope, intercept, r_value, p_value, std_err = stats.linregress(temps, ys)
    line = slope*np.array(temps)+intercept
    ax3.scatter(temps, ys)
    ax3.plot(temps, line) 
    ax3.set_title(f'd) p={p_value:.2g}, R-sqr={r_value**2:.2f}')
    ax3.set_xlabel('Bangalore Avg Temp')
    ax3.set_ylabel('#Labnotes')

    # Average rate of users.
    users = df['user'].unique()
    boxes = []
    print( f"[INFO ] Total users {len(users)}" )
    X = []
    for i, u in enumerate(users):
        v = df[df['user'] == u]['datetime']
        v = sorted(v)
        # if the latest labenote is less than a month old, ignore.
        #  if (datetime.now() - v[-1]).days > 30:
            #  print( f"[INFO ] User {u} is ignored." )
            #  continue
        X.append(u)
        vdiff = [x.days for x in np.diff(v)]
        boxes.append(vdiff)
    #  ax4.boxplot(boxes, whis='range')
    Y = [np.mean(v) for v in boxes]
    Yerr = [ np.std(v) for v in boxes]
    ax4.errorbar(range(len(Y)), Y, yerr=Yerr, label='User')
    ili = np.mean(Y)
    ax4.axhline(ili, color='red', label='Lab mean')
    ax4.legend()
    ax4.set_title(f'e) Inter Labnote Interval. Mean={ili:.1f} day', fontsize=10)
    ax4.set_ylabel('Days')

    plt.tight_layout()
    plt.savefig(outfile)
    print( f"[INFO ] Saved to {outfile}" )
    plt.close()


def main():
    with open('data.pickle', 'rb') as f:
        d = pickle.load(f)

    data = []
    for u, v in d.items():
        for vv in v:
            vv.insert(0, u)
            vv[-1] = vv[-1].replace(' ', '')
            data.append(vv)

    data = [reformat(x) for x in data]
    df = pd.DataFrame(data, columns=['user', 'title', 'datetime'])
    df = df.dropna()
    df['datetime'] = pd.to_datetime(df['datetime'], format='%a,%d/%m/%Y-%H:%M')
    df.sort_values(by='datetime', inplace=True)
    plot_together(df, 'all.png')

    users = df['user'].unique()
    for u in users:
        d = df[df['user'] == u]
        plot_together(d, f'{u}.png')
        print( f"[INFO ] Done for user {u}" )

if __name__ == '__main__':
    main()
