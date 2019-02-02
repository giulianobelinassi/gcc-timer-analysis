#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np

def in_between(dot1, dot2):
    return dot2['start'] <= dot1['end']

def plot_lines(y, start, end):
    plt.hlines(y, start+0.01, end-0.01, 'b', label='test', lw=1)
    plt.vlines(start+0.01, y+0.20, y-0.20, 'b', lw=1)
    plt.vlines(end-0.01, y+0.20, y-0.20, 'b', lw=1)

def plot_labels(y_pos, start, end, label, thresh):
    for i in range(len(end)):
        if end[i] - start[i] > thresh:
            plt.text((start[i]+end[i])/2, y_pos[i]+0.10, label[i], ha='center')


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
    plot_labels(y, data['start'], data['end'], data['filename'], 30)

input_file = open("/tmp/time_results-1.txt", "rb")

# Read data frame from file
data = np.genfromtxt(input_file,
                     usecols=(1, 3, 5),
                     names=('filename', 'start', 'end'),
                     converters={1: lambda x: x.decode('utf-8').split('/')[-1]},
                     dtype=('U64', float, float))

start_min = data['start'].min()

# Set the smallest start as ground zero
data['start'] = data['start'] - start_min
data['end']   = data['end']   - start_min

print(len(data))


plt.figure(figsize=(18,7))

plot_timeline(data)
ax = plt.gca()

plt.xlabel('Time (s)')
plt.ylabel('Makefile Job')
plt.title('Time Interval Graphic of Each File')
plt.show()
