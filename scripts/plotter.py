#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import sys

# Determine if dot1 overlap with dot2
def overlap(dot1, dot2):
    return dot2['start'] <= dot1['end']

# Plot interval
def plot_lines(y, start, end):
    Y_WIDTH = 0.20
    X_OFFSET = 0.02
    plt.hlines(y, start + X_OFFSET, end - X_OFFSET, 'b', label='test', lw=1)
    plt.vlines(start + X_OFFSET, y + Y_WIDTH, y - Y_WIDTH, 'b', lw=1)
    plt.vlines(end   - X_OFFSET, y + Y_WIDTH, y - Y_WIDTH, 'b', lw=1)

# Plot the file name right above its interval
def plot_labels(y_pos, start, end, label, thresh):
    Y_OFFSET = 0.10
    for i in range(len(end)):
        if end[i] - start[i] > thresh:
            plt.text((start[i] + end[i])/2,
                     y_pos[i] + Y_OFFSET,
                     label[i],
                     ha='center')

# Plot the timeline.
def plot_timeline(data):
    bucket = []
    y = np.zeros(len(data['start']))

    for j in range(len(data)):
        dot = data[j]
        touched = False
        i = 0

        # This is basically the interval graph coloring problem.
        # It may be faster to replace this for with a priority queue.
        for i in range(len(bucket)):
            if not overlap(bucket[i], dot):
                bucket[i] = dot
                touched = True
                break

        if not touched:
            bucket.append(dot)

        #store its bucket.
        y[j] = i

    plot_lines(y, data['start'], data['end'])
    plot_labels(y, data['start'], data['end'], data['filename'], 30)

def print_usage_message():
    print( """
Time analyzer plotter for the GCC project.
Arguments:
    --input-file          File to be read.
    --output-file         File to save the plot
    --threshold           Display the name of file such that its time is greater
                          than the threshold
    --filter              Filter (UNKNOWN) files
    Any other argument will be ignored

This program is Free Software and is distributed under the GNU Public License
version 2. There is no warranty; not even from MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.""")


def parse_args():
    argc = len(sys.argv)
    input_path = None
    output_path = None
    threshold = 30
    filter = False

    for i in range(argc):
        if sys.argv[i] == "--filter":
            filter = True
        if i + 1 < argc:
            if sys.argv[i] == "--input-file":
                input_path = sys.argv[i+1]
            elif sys.argv[i] == "--treshold":
                threshold = float(sys.argv[i+1])
            elif sys.argv[i] == "--output-file":
                output_path = sys.argv[i+1]

    return input_path, output_path, threshold, filter

def do_filter(data):
    mask = []
    for i in range(len(data)):
        if "(UNKNOWN)" not in data[i]['filename']:
            mask.append(i);

    return mask

# Get arguments from argv.
input_path, output_path, threshold, filter = parse_args()

# No input file given.
if input_path == None:
    print_usage_message()
    sys.exit()

input_file = open(input_path, "rb")

# Read data frame from file.
data = np.genfromtxt(input_file,
                     usecols=(1, 3, 5),
                     names=('filename', 'start', 'end'),
                     converters={1: lambda x: x.decode('utf-8').split('/')[-1]},
                     dtype=('U64', float, float))

if filter:
    mask = do_filter(data)
    data = data[mask]

# Sort the data. Required by the greedy interval graph coloring algorithm
data.view('U64,float,float').sort(order=['f1', 'f2'], axis=0)

start_min = data['start'].min()

# Set the smallest start as ground zero.
data['start'] = data['start'] - start_min
data['end']   = data['end']   - start_min

plt.figure(figsize=(18,7))

plot_timeline(data)
ax = plt.gca()

plt.xlabel('Time (s)')
plt.ylabel('Makefile Job')
plt.title('Time Interval Graphic of Each File')

if output_path is not None:
    plt.savefig(output_path, dpi=100)
else:
    plt.show()
