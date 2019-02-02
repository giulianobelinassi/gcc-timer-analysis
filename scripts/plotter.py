#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np

def in_between(dot1, dot2):
    return dot2['start'] <= dot1['end']

def plot_lines(y, start, end):
    plt.hlines(y, start, end, 'b', lw=4)
    #plt.vlines(start, y+0.03, y-0.03, 'b', lw=2)
    #plt.vlines(end, y+0.03, y-0.03, 'b', lw=2)

def plot_timeline(data):
    bucket = []
    y = np.zeros(len(data['start']))

    for j in range(len(data)):
        dot = data[j]
        touched = False
        i = 0

        for i in range(len(bucket)):
            if not in_between(bucket[i], dot):
                bucket[i] = dot
                touched = True
                break

        if not touched:
            bucket.append(dot)

        y[j] = i

    plot_lines(y, data['start'], data['end'])

input_file = open("/tmp/time_results-1.txt", "rb")

# Read data frame from file
data = np.genfromtxt(input_file,
                     usecols=(1, 3, 5),
                     names=('filename', 'start', 'end'),
                     dtype=('U64', float, float))

start_min = data['start'].min()

# Set the smallest start as ground zero
data['start'] = data['start'] - start_min
data['end']   = data['end']   - start_min

print(len(data))

plot_timeline(data)

plt.show()
