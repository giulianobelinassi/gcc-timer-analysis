#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import sys

PARSER_LABEL        = 0
IPA_LABEL           = 1
GIMPLE_IPA_LABEL    = 2
GIMPLE_LABEL        = 3
RTL_LABEL           = 4
REAL_LABEL          = 5
USER_LABEL          = 6
SYS_LABEL           = 7

NUM_LABELS          = SYS_LABEL + 1

FOLDER_PREFIX = "/home/giulianob/data_new/"

ALPHA = 0.95
Z_ALPHA = -scipy.stats.norm.ppf((1 - ALPHA)/2.)

def parse_file(thread, num):
    filename = FOLDER_PREFIX + "time_gcc_{}_{}.dat".format(thread, num)

    try:
        input_file = open(filename, "r")
    except:
        return None

    times = [0.]*NUM_LABELS

    line = input_file.readline()
    while line:
        splitted = line.split()

        label = splitted[0]
        time  = 0

        if len(splitted) >= 4:
            time = splitted[3]
        else:
            time = splitted[1]


        idx = 0

        if   label == "PARSER:":
            idx = PARSER_LABEL
        elif label == "IPA:":
            idx = IPA_LABEL
        elif label == "GIMPLE_IPA:":
            idx = GIMPLE_IPA_LABEL
        elif label == "GIMPLE:":
            idx = GIMPLE_LABEL
        elif label == "RTL:":
            idx = RTL_LABEL
        elif label == "real":
            idx = REAL_LABEL
        elif label == "user":
            idx = USER_LABEL
        elif label == "sys":
            idx = SYS_LABEL

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

def plot_time_bars(to_plot, data, labels):

    _, ax = plt.subplots()

    x_label = "Number of Threads"
    y_label = "Time (s)"
    title = "Time in Parallel GIMPLE Intra Procedural Analysis"

    y_shift = 0.10

    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_title(title)

    seq_time = 0

    speedups = [1]

    for i in range(len(data)):
        d = data[i]
        label = labels[i]

        gimple_mean = np.mean(d[to_plot])
        gimple_sem = scipy.stats.sem(d[to_plot])

        h = gimple_sem * Z_ALPHA

        x_data = label
        y_data = gimple_mean

        if i == 0:
            seq_time = gimple_mean
        else:
            speedup = seq_time/gimple_mean
            ax.text(label, y_data + y_shift, "x{:.2f}".format(speedup), ha='center')
            speedups.append(speedup)

        ax.bar(x_data, y_data, color = 'blue', align = 'center')
        ax.errorbar(label, y_data, yerr = h, color = '#297083', ls = 'none', lw = 2, capthick = 2)

    return speedups

def plot_estimate_speedups(speedups, data, labels):

    _, ax = plt.subplots()

    x_label = "Number of Threads"
    y_label = "Time (s)"
    title = "Estimative of Time in Parallel RTL Analysis"

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
        ax.text(label, y_data + y_shift, "x{:.2f}".format(speedup), ha='center')

        ax.bar(x_data, y_data, color = 'darkgoldenrod', align = 'center')
        ax.errorbar(label, y_data, yerr = h, color = '#297083', ls = 'none', lw = 2, capthick = 2)

    return speedups


def plot_expected_time_after_rtl_bars(gimple_speedups, data, labels, estimate_rtl=False):

    _, ax = plt.subplots()

    x_label = "Number of Threads"
    y_label = "Time (s)"
    title = "GCC Time and Speedups"

    if estimate_rtl:
        title = title + " (Estimate)"


    y_shift = 0.15

    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_title(title)

    seq_time = 0

    parser_mean = np.mean(data[0][PARSER_LABEL])
    ipa_mean = np.mean(data[0][IPA_LABEL])
    rtl_mean = np.mean(data[0][RTL_LABEL])


    print(parser_mean)
    print(ipa_mean)
    print(rtl_mean)


    real_means = []
    real_means_estimate = []

    gimple_means = []
    rtl_means = []

    for i in range(len(data)):
        d = data[i]
        label = labels[i]

        real_mean = np.mean(d[REAL_LABEL])
        real_sem = scipy.stats.sem(d[REAL_LABEL])

       # h = gimple_sem * Z_ALPHA

        time = real_mean
        real_means.append(time)

        if not estimate_rtl:
            x_data = label
            y_data = time
            if i == 0:
                seq_time = time
            else:
                speedup = seq_time/time
                ax.text(x_data, y_data + y_shift, "x{:.2f}".format(speedup), ha='center')

            rtl_means.append(np.mean(d[RTL_LABEL]))

        #ax.bar(x_data, y_data, color = 'blue', align = 'center', label = 'Parallel GIMPLE')


        time = real_mean + (-1 + 1./(gimple_speedups[i]))*rtl_mean

        if estimate_rtl:
            x_data = label
            y_data = time
            if i == 0:
                seq_time = time
            else:
                speedup = seq_time/time
                ax.text(x_data, y_data + y_shift, "x{:.2f}".format(speedup), ha='center', color='black')
            rtl_means.append(np.mean(d[RTL_LABEL]/gimple_speedups[i]))

        real_means_estimate.append(time)
        gimple_means.append(np.mean(d[GIMPLE_LABEL]))


    real = None
    if estimate_rtl:
        real = np.array(real_means_estimate)
    else:
        real = np.array(real_means)

    gimple = np.array(gimple_means)
    rtl    = np.array(rtl_means)
    ipa    = ipa_mean
    parser = parser_mean

    plt_gimple = real
    plt_rtl    = real - gimple
    plt_ipa    = real - gimple - rtl
    plt_parser = real - gimple - rtl - ipa
    plt_others = real - gimple - rtl - ipa - parser

    rtl_label = ""
    if estimate_rtl:
        rtl_label = "Parallel RTL (estimate)"
    else:
        rtl_label = "RTL"

    ax.bar(labels, plt_gimple, color = 'blue', align = 'center', label = 'Parallel GIMPLE')
    ax.bar(labels, plt_rtl, color = 'darkgoldenrod', align = 'center', label = rtl_label)
    ax.bar(labels, plt_ipa, color = 'red', align = 'center', label = 'Inter Process Analysis')
    ax.bar(labels, plt_parser, color = 'green', align = 'center', label = 'Parser')
    ax.bar(labels, plt_others, color = 'black', align = 'center', label = 'Others')
    ax.legend(loc="upper right")

    ax.set_ylim(0, 70)

        #ax.errorbar(label, y_data, yerr = h, color = '#297083', ls = 'none', lw = 2, capthick = 2)


def plot_pie(data):

    _, ax = plt.subplots()

    labels = 'Parser', 'IPA', 'GIMPLE IPA', 'GIMPLE', 'RTL', 'Others'
    colors = 'green', 'red', 'yellow', 'blue', 'darkgoldenrod', 'black'
    #text_c = dict(color = ['black', 'black', 'black', 'white', 'black', 'white'])
    text_c = dict(color = 'w')
    explode = (0, 0, 0, .1, .1, 0)

    title = "GCC Profile"

    y_shift = 0.15

    ax.set_title(title)

    seq_time = 0

    parser_mean = np.mean(data[0][PARSER_LABEL])
    gimple_mean = np.mean(data[0][GIMPLE_LABEL])
    gimple_ipa_mean = np.mean(data[0][GIMPLE_IPA_LABEL])
    ipa_mean = np.mean(data[0][IPA_LABEL])
    rtl_mean = np.mean(data[0][RTL_LABEL])
    real_mean = np.mean(data[0][REAL_LABEL])
    others = real_mean - parser_mean - gimple_mean - ipa_mean  -rtl_mean

    plt_data = [parser_mean, ipa_mean, gimple_ipa_mean, gimple_mean, rtl_mean, others]
    wedges, texts, autotexts = ax.pie(plt_data, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90, textprops=text_c)
    ax.legend(wedges, labels, loc='upper right', bbox_to_anchor=(1, 0, .3, 1))




def main():
    data_list = parse_files([1, 2, 4, 8])

    speedups = plot_time_bars(GIMPLE_LABEL, data_list, ["1", "2", "4", "8"])
    #plot_estimate_speedups(speedups, data_list[0], ["1", "2", "4", "8"])
    plot_expected_time_after_rtl_bars(speedups, data_list, ["1", "2", "4", "8"])
    plot_expected_time_after_rtl_bars(speedups, data_list, ["1", "2", "4", "8"], True)
    plot_pie(data_list)

    plt.show()

main()
