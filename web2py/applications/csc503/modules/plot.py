# -*- coding: utf-8 -*-

from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties
import datetime


def plot_results(bases, procs_list, algorithm_name, pngfilename):
    font_mono = FontProperties()
    font_mono.set_family('monospace')
    bar_labels = procs_list                                 # y-axis labels
    plt.figure(figsize=(10, 8))                             # 10" x 8"
    y_pos = xrange(len(bases))                              # position of y-axis labels
    plt.yticks(y_pos, bar_labels, fontsize=16)              # tick-marks on y-axis
    bars = plt.barh(y_pos, bases,                           # horizontal bar-plot
                    align='center',
                    alpha=0.4,
                    color='b')
    # annotation and labels for speedup of parallel vs serial
    ts = bars[0].get_width()
    for ba, be, bl in zip(bars[1:], bases[1:], bar_labels[1:]):
        p = int(bl)
        tp = be
        speedup = ts / tp
        bar_width = ba.get_width()
        plt.text(bar_width + (.0005/bar_width * bar_width),
                 ba.get_y() + ba.get_height() / 2,
                 'wall time : {0:.4}s\n'.format(tp) +
                 'overhead  : {0:.4}s\n'.format(p * tp - ts) +
                 'speedup   : {0:.4}\n'.format(speedup) +
                 'efficiency: {0:.4}'.format(speedup / p),
                 # '{0:.2} Seconds\n'.format(be) + '{0:.2} X Serial'.format(bases[0] / be),
                 ha='left', va='center', fontsize=10, fontproperties=font_mono)
    bar_width = bars[0].get_width()
    plt.text(bar_width + (.0005/bar_width * bar_width),
                 bars[0].get_y() + bars[0].get_height() / 2,
                 'wall time : {0:.4}s'.format(bases[0]),
                 ha='left', va='center', fontsize=10, fontproperties=font_mono)
    plt.annotate('Created by psim2web2py at %s' % datetime.datetime.today(),
                 xy=(1,0), xycoords='axes fraction', xytext=(50, -50),
                 textcoords='offset points', ha='right', va='top', fontsize=8)
    plt.xlabel("\nTime", fontsize=14)
    plt.ylabel("Number of Processes", fontsize=14)
    plt.title('Serial vs. Parallel [%s]\n' %
              str.replace(algorithm_name, '_', ' '),
              fontsize=18)
    plt.ylim([-1, len(bases)])
    plt.xlim([0, max(bases) * 1.1])
    plt.vlines(bases[0], -1,
               len(bases) + 0.5,
               linestyles='dashed')
    # plt.grid()
    # get the current frame to be saved
    fig = plt.gcf()
    fig.savefig(pngfilename)

