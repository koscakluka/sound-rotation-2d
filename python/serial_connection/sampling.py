import serial
import matplotlib.pyplot as plot
import numpy as np

DEVICE_ADDRESS = '/dev/ttyACM0'
FILE_PATH = '../data/'


def save_sample(filepath, data):
    try:
        data_file = open(filepath, 'r')
    except IOError:
        data_file = open(filepath, 'w')
        data_file.close()

    with open(filepath, 'a') as data_file:
        for point in data[0]:
            data_file.write('{:3.2f}'.format(point) + ',')
        for point in data[1]:
            data_file.write('{:3.2f}'.format(point) + ',')
        data_file.write(str(label) + '\n')


serial_con = serial.Serial("/dev/ttyACM0", 230400)

while True:
    label = input("Label the sample:")

    while serial_con.read()[0] != ord('S'):  # wait for the start signal
        pass
    batch_size = int(serial_con.read()[0]) * 256 + int(serial_con.read()[0])

    data = [[], [], label]
    for i in range(batch_size):
        data[0].append(serial_con.read()[0])
        data[1].append(serial_con.read()[0])

    if serial_con.read()[0] == ord('E'):

        # center data
        data[0] = np.array(data[0]) - np.mean(data[0])
        data[1] = np.array(data[1]) - np.mean(data[1])

        # display data
        print("Mean of left sensor: " + str(sum(data[0]) / len(data[0])))
        print("Mean of right sensor: " + str(sum(data[1]) / len(data[1])))
        plot.plot(range(batch_size), data[0], range(batch_size), data[1])
        plot.show()

        save_sample(FILE_PATH + '32kHz_' + str(batch_size) + '.csv', data)
    else:
        print("Sample contaminated! Rejecting sample.")

    if input("Continue (y/n):") == 'n':
        break
