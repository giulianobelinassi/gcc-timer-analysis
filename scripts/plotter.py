#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import sys

# Determine if dot1 overlap with dot2
def overlap(dot1, dot2):
    return dot2['start'] <= dot1['end']

# Plot interval
def plot_lines(y, start, end, labels, colors, default_color, on_right):
    Y_WIDTH = 0.20
    X_OFFSET = 0.02
    Y_OFFSET = (3*y.max() + 53)/560 # Linear interpolation with
                                    # values f(8) = 0.10 and f(64) = 0.40
    char = 'A'
    black_label = 'Other Files'

    if on_right:
        centralizer = lambda x, y: y
        ha = 'right'
    else:
        centralizer = lambda x, y: (x + y)/2
        ha = 'center'


    # This is indeed slow when compared to array plot. However, matplotlib
    # seems not to like an array of labels
    for i in range(len(y)):
        if colors[i] != default_color:
            plt.hlines(y[i], start[i] + X_OFFSET,
                       end[i] - X_OFFSET, colors[i],
                       label='[' + char + '] ' + labels[i],
                       lw=3)
            plt.text(centralizer(start[i], end[i]),
                     y[i] + Y_OFFSET,
                     '[' + char + ']',
                     ha=ha)
            char = chr(ord(char) + 1)
        else:
            plt.hlines(y[i],
                       start[i] + X_OFFSET,
                       end[i] - X_OFFSET,
                       default_color,
                       label=black_label,
                       lw=3)
            black_label = ''

    plt.vlines(start + X_OFFSET, y + Y_WIDTH, y - Y_WIDTH, colors, lw=1)
    plt.vlines(end   - X_OFFSET, y + Y_WIDTH, y - Y_WIDTH, colors, lw=1)

# Plot the timeline.
def plot_timeline(data, default_color = 'k', thresh = 30, on_right=False):
    bucket = []
    possible_colors = ('b', 'r', 'y', 'm', 'g', 'c')
    current_color = 0

    y = np.zeros(len(data['start']))
    colors = np.full(len(data['start']), default_color)

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

        if dot['end'] - dot['start'] > thresh:
            colors[j] = possible_colors[current_color]
            current_color = (current_color + 1) % len(possible_colors)

    plot_lines(y,
               data['start'],
               data['end'],
               data['filename'],
               colors,
               default_color,
               on_right)

def print_usage_message():
    print( """
Time analyzer plotter for the GCC project.
Arguments:
    --input-file          File to be read.
    --output-file         File to save the plot
    --threshold           Display the name of file such that its time is greater
                          than the threshold
    --filter              Filter (UNKNOWN) files
    --default-color       Color for which non-relevant information will be print.
                          Default is 'k' (black).
    --on-right            Put label on right-side of the bar.
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
    on_right = False
    default_color = 'k'

    for i in range(argc):
        if sys.argv[i] == "--filter":
            filter = True
        if sys.argv[i] == "--on-right":
            on_right = True
        if i + 1 < argc:
            if sys.argv[i] == "--input-file":
                input_path = sys.argv[i+1]
            elif sys.argv[i] == "--threshold":
                threshold = float(sys.argv[i+1])
            elif sys.argv[i] == "--output-file":
                output_path = sys.argv[i+1]
            elif sys.argv[i] == "--default-color":
                default_color = sys.argv[i+1]

    return input_path, output_path, threshold, filter, default_color, on_right

def do_filter(data):
    mask = []
    for i in range(len(data)):
        if "(UNKNOWN)" not in data[i]['filename']:
            mask.append(i);

    return mask

# Get arguments from argv.
input_path, output_path, threshold, filter, default_color, on_right = parse_args()

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

plt.figure(figsize=(18,10))

plot_timeline(data, default_color, threshold, on_right)
ax = plt.gca()
ax.legend()

plt.xlabel('Time (s)')
plt.ylabel('Makefile Job')
plt.title('Time Interval Graphic of Each File')

if output_path is not None:
    plt.savefig(output_path, dpi=100)
else:
    plt.show()
