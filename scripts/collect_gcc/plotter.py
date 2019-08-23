#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import sys

GIMPLE_IPA_LABEL = 0
GIMPLE_LABEL = 1
RTL_LABEL = 2

FOLDER_PREFIX = "/home/giulianob/data/"

ALPHA = 0.95
Z_ALPHA = -scipy.stats.norm.ppf((1 - ALPHA)/2.)

def parse_file(thread, num):
    filename = FOLDER_PREFIX + "time_gcc_{}_{}.dat".format(thread, num)

    try:
        input_file = open(filename, "r")
    except:
        return None

    times = [0.0, 0.0, 0.0]

    line = input_file.readline()
    while line:
        splitted = line.split()

        label = splitted[0]
        time  = splitted[3]

        idx = 0

        if      label == "GIMPLE_IPA:":
            idx = GIMPLE_IPA_LABEL
        elif label == "GIMPLE:":
            idx = GIMPLE_LABEL
        elif label == "RTL:":
            idx = RTL_LABEL

        times[idx] = float(time)

        line = input_file.readline()

    return times

def parse_files(threads):
    data = []

    for thread in threads:
        data_for_thread = []
        for i in range(1, 100000):
            times = parse_file(thread, i)

            if times is None:
                break

            data_for_thread.append(times)

        data_for_thread_np = np.transpose(np.array(data_for_thread))
        data.append(data_for_thread_np)

    return data

def plot_time_bars(data, labels):

    _, ax = plt.subplots()

    x_label = "Number of Threads"
    y_label = "Time (s)"
    title = "GIMPLE Intra Procedural Analysis"

    y_shift = 0.10

    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_title(title)

    seq_time = 0

    speedups = [1]

    for i in range(len(data)):
        d = data[i]
        label = labels[i]

        n = len(d[GIMPLE_LABEL])
        gimple_mean = np.mean(d[GIMPLE_LABEL])
        gimple_sem = scipy.stats.sem(d[GIMPLE_LABEL])

        h = gimple_sem * Z_ALPHA

        x_data = label
        y_data = gimple_mean

        if i == 0:
            seq_time = gimple_mean
        else:
            speedup = seq_time/gimple_mean
            ax.text(label, y_data + y_shift, "Speedup = {:.2f}".format(speedup), ha='center')
            speedups.append(speedup)

        ax.bar(x_data, y_data, color = 'blue', align = 'center')
        ax.errorbar(label, y_data, yerr = h, color = '#297083', ls = 'none', lw = 2, capthick = 2)

    return speedups

def plot_estimate_speedups(speedups, data, labels):

    _, ax = plt.subplots()

    x_label = "Number of Threads"
    y_label = "Time (s)"
    title = "RTL Intra Procedural Analysis"

    y_shift = 0.10

    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_title(title)

    seq_time = np.mean(data[RTL_LABEL])
    n = len(data[RTL_LABEL])
    gimple_sem = scipy.stats.sem(data[RTL_LABEL])
    h = gimple_sem * Z_ALPHA

    for i in range(len(labels)):
        label = labels[i]
        speedup = speedups[i]

        this_time = seq_time/speedup

        x_data = label
        y_data = this_time

        speedup = seq_time/this_time
        ax.text(label, y_data + y_shift, "Speedup = {:.2f}".format(speedup), ha='center')

        ax.bar(x_data, y_data, color = 'blue', align = 'center')
        ax.errorbar(label, y_data, yerr = h, color = '#297083', ls = 'none', lw = 2, capthick = 2)

    return speedups


def plot_speedup_bars(data, labels):

    _, ax = plt.subplots()

    x_label = "Number of Threads"
    y_label = "Speedup"
    title = "GIMPLE Intra Procedural Analysis"

    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_title(title)

    gimple_seq_mean = np.mean(data[0][GIMPLE_LABEL])

    for i in range(1, len(data)):
        d = data[i]
        label = labels[i]

        n = len(d[GIMPLE_LABEL])
        gimple_mean = np.mean(d[GIMPLE_LABEL])
        gimple_sem = scipy.stats.sem(d[GIMPLE_LABEL])

        speedup = gimple_seq_mean/gimple_mean

        h = gimple_sem * Z_ALPHA

        x_data = label
        y_data = speedup

        ax.bar(x_data, y_data, color = 'blue', align = 'center')
        ax.errorbar(label, y_data, yerr = h, color = '#297083', ls = 'none', lw = 2, capthick = 2)


def main():
    data_list = parse_files([1, 8])

    speedups = plot_time_bars(data_list, ["1", "8"])
    plot_estimate_speedups(speedups, data_list[0], ["1", "8"])

    plt.show()

main()
