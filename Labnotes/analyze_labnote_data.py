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

def plot_together(df):
    plt.figure(figsize=(10, 6))
    gridSize = (2, 2)
    ax1 = plt.subplot2grid( gridSize, (0,0), colspan = 1 )
    ax2 = plt.subplot2grid( gridSize, (0,1), colspan = 1 )
    ax3 = plt.subplot2grid( gridSize, (1,0), colspan = 1 )
    ax4 = plt.subplot2grid( gridSize, (1,1), colspan = 1 )

    # distribution by day.
    data = df['date']
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
    ax1.set_title('By Day')
    ax1.bar(xs, ys)
    ax1.set_xticks(xs)
    ax1.set_xticklabels(['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            , fontsize=10
            )

    # distribution by month.
    temps = [20.8,22.9,25.5,27.1,26.9,24.4,23.3,23.4,23.2,23.1,21.8,20.7]
    months = [int(x.strftime('%m')) for x in data]
    hist = Counter(months)
    xs = range(1, 13)
    ys = [hist.get(x, 0) for x in xs]
    ax2.bar(xs, ys)
    ax2.set_xticks(xs)
    ax2.set_title('By Month')
    ax22 = ax2.twinx()
    ax22.plot(xs, temps, color='red')
    ax22.set_ylim(bottom=17)
    ax22.set_ylabel('Avg Temp of Bangalore')

    # correlation between temp and labnotes.
    slope, intercept, r_value, p_value, std_err = stats.linregress(temps, ys)
    line = slope*np.array(temps)+intercept
    ax3.scatter(temps, ys)
    ax3.plot(temps, line) 
    ax3.set_title(f'p={p_value:.2g}, R-sqr={r_value**2:.2f}')
    ax3.set_xlabel('Bangalore Avg Temp')
    ax3.set_ylabel('#Labnotes')

    # Average rate of users.
    users = df['user'].unique()
    boxes = []
    print( f"[INFO ] Total users {len(users)}" )
    X = []
    for i, u in enumerate(users):
        v = df[df['user'] == u]['date']
        v = sorted(v)
        # if the latest labenote is less than a month old, ignore.
        if (datetime.now() - v[-1]).days > 60:
            print( f"[INFO ] User {u} is ignored." )
            continue
        X.append(u)
        vdiff = [x.days for x in np.diff(v)]
        boxes.append(vdiff)
    #  ax4.boxplot(boxes, whis='range')
    Y = [np.mean(v) for v in boxes]
    Yerr = [ np.std(v) for v in boxes]
    ax4.errorbar(range(len(Y)), Y, yerr=Yerr, label='User')
    ax4.axhline(np.mean(Y), color='red', label='Lab mean')
    ax4.legend()
    ax4.set_title( 'Inter Labnote Interval')
    ax4.set_ylabel('Days')
    #  ax4.set_xticklabels(X, rotation=90)
    plt.tight_layout()
    plt.savefig( f'results.png')
    plt.close()

def plot_users(data):
    # Average rate of users.
    users = set([x[-1] for x in data])
    boxes = []
    print( f"[INFO ] Total users {len(users)}" )
    X = []
    for i, u in enumerate(users):
        v = [x[0] for x in data if x[-1] == u]
        v = sorted(v)
        # if the latest labenote is less than a month old, ignore.
        if (datetime.now() - v[-1]).days > 60:
            print( f"[INFO ] User {u} is ignored." )
            continue
        X.append(u)
        vdiff = [x.days for x in np.diff(v)]
        boxes.append(vdiff)
    ax4.boxplot(boxes, whis='range')
    ax4.set_xticklabels(X, rotation=90)


def main():
    with open('data.pickle', 'rb') as f:
        data = pickle.load(f)
    data = [reformat(x) for x in data]
    df = pd.DataFrame(data, columns=['date', 'title', 'user'])
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values(by='date', inplace=True)
    plot_together(df)

if __name__ == '__main__':
    main()
