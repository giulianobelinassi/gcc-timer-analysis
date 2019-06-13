#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import sys

def plot_sensors_data(data):
    current_color = 0
    num_sensors = 4

    for i in range(num_sensors):
        data_sensor = data[np.where(data['sensor'] == i)]

        x = data_sensor['timestamp']
        y = data_sensor['value']

        lower_int = int(np.floor(lower_bound(y, x)))
        upper_int = int(np.ceil(upper_bound(y, x)))

        sensor_label = "Socket " + str(i) + " Total in [" + str(lower_int) + ", " + str(upper_int) + "]"
        plt.plot(x,
                 y,
                 label=sensor_label)

def print_usage_message():
    print( """
Time analyzer plotter for the GCC project.
Arguments:
    --input-file          File to be read.
    --output-file         File to save the plot.
    --dpi                 Dots per inch of output image.
    Any other argument will be ignored.

This program is Free Software and is distributed under the GNU Public License
version 2. There is no warranty; not even from MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.""")


def lower_bound(y, x):
    integral = 0
    for i in range(len(y) - 1):
        delta_x = x[i+1] - x[i]
        mi = min(y[i], y[i+1])
        integral = integral + mi*delta_x

    return integral

def upper_bound(y, x):
    integral = 0
    for i in range(len(y) - 1):
        delta_x = x[i+1] - x[i]
        mi = max(y[i], y[i+1])
        integral = integral + mi*delta_x

    return integral

def check_timevals(x):
    for i in range(len(x) - 1):
        if (x[i+1] < x[i]):
            print("ERROR: Timeval is not ordered!", x[i+1], x[i])
            sys.exit()

def parse_args():
    argc = len(sys.argv)
    input_path = None
    output_path = None
    dpi = 300

    for i in range(argc):
        if i + 1 < argc:
            if sys.argv[i] == "--input-file":
                input_path = sys.argv[i+1]
            elif sys.argv[i] == "--output-file":
                output_path = sys.argv[i+1]
            elif sys.argv[i] == "--dpi":
                dpi = int(sys.argv[i+1])

    return (input_path, output_path, dpi)


# Get arguments from argv.
(input_path, output_path, dpi) = parse_args()

# No input file given.
if input_path == None:
    print_usage_message()
    sys.exit()

input_file = open(input_path, "rb")

# Read data frame from file.
data = np.genfromtxt(input_file,
                     #usecols=(1, 3, 5),
                     names=('sensor', 'value', 'timestamp'),
                     dtype=(int, float, float))

data['value'] = data['value']/1e6 #convert from uW to W

# Sort the data. Required by the greedy interval graph coloring algorithm
check_timevals(data['timestamp']);
# data.view('U64,float,float').sort(order=['f1', 'f2'], axis=0)

start_min = data['timestamp'].min()

# Set the smallest timestamp as ground zero.
data['timestamp'] = data['timestamp'] - start_min

plt.figure(figsize=(18,10))

plot_sensors_data(data)
ax = plt.gca()
ax.legend()

plt.xlabel('Time (s)')
plt.ylabel('Energy Consumption (W)')
plt.title('Energy Consuption for each CPU Socket')

# Set minimum and maximum values for y axis
plt.ylim(max(data['value'].min() - 2, 0), data['value'].max())

if output_path is not None:
    plt.savefig(output_path, dpi=dpi)
else:
    plt.show()
