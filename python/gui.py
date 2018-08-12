import sys
import serial

from PyQt4 import QtGui

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from python.plotting import plot_data
from python.serial_connection.sampling import save_sample, sample

import numpy as np

DEVICE_ADDRESS = '/dev/ttyACM0'
BAUD_RATE = 57600

FILE_PATH = "data/"

BATCH_SIZE = 400


class SamplingWidget(QtGui.QWidget):

    def __init__(self):
        super(SamplingWidget, self).__init__()

        self.serial_con = serial.Serial(DEVICE_ADDRESS, BAUD_RATE)

        self.batch_size = None
        self.data = None

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)

        self.left_mean_label = None
        self.left_std_label = None
        self.right_mean_label = None
        self.right_std_label = None
        self.batch_size_label = None

        self.label_edit = None

        self.accept_btn = None
        self.reject_btn = None

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar())
        self.setLayout(layout)

        self.get_sample()

        self.canvas.draw()

    def toolbar(self):
        self.left_mean_label = QtGui.QLabel("0.00000")
        self.left_std_label = QtGui.QLabel("0.00000")
        self.right_mean_label = QtGui.QLabel("0.00000")
        self.right_std_label = QtGui.QLabel("0.00000")
        self.batch_size_label = QtGui.QLabel("0")

        self.label_edit = QtGui.QLineEdit()

        self.accept_btn = QtGui.QPushButton("Accept")
        self.accept_btn.clicked.connect(self.accept_sample)
        self.reject_btn = QtGui.QPushButton("Reject")
        self.reject_btn.clicked.connect(self.get_sample)

        layout = QtGui.QVBoxLayout()
        info_widget = QtGui.QWidget()

        info_layout = QtGui.QGridLayout()
        info_widget.setLayout(info_layout)

        info_layout.addWidget(QtGui.QLabel("Batch size: "), 1, 1)
        info_layout.addWidget(QtGui.QLabel("Left mean: "), 2, 1)
        info_layout.addWidget(QtGui.QLabel("Left std: "), 3, 1)
        info_layout.addWidget(QtGui.QLabel("Right mean: "), 4, 1)
        info_layout.addWidget(QtGui.QLabel("Right std: "), 5, 1)
        info_layout.addWidget(self.batch_size_label, 1, 2)
        info_layout.addWidget(self.left_mean_label, 2, 2)
        info_layout.addWidget(self.left_std_label, 3, 2)
        info_layout.addWidget(self.right_mean_label, 4, 2)
        info_layout.addWidget(self.right_std_label, 5, 2)

        layout.addWidget(info_widget)
        layout.addSpacerItem(QtGui.QSpacerItem(1, 10, QtGui.QSizePolicy.Expanding,
                                               QtGui.QSizePolicy.Expanding))
        layout.addWidget(QtGui.QLabel("Label:"))
        layout.addWidget(self.label_edit)
        layout.addWidget(self.accept_btn)
        layout.addWidget(self.reject_btn)
        widget = QtGui.QWidget()
        widget.setFixedWidth(100)
        widget.setLayout(layout)
        return widget

    def set_data(self, batch_size, data):
        self.left_mean_label.setText(str(round(np.mean(data[0]), 5)))
        self.left_std_label.setText(str(round(np.std(data[0]), 5)))
        self.right_mean_label.setText(str(round(np.mean(data[1]), 5)))
        self.right_std_label.setText(str(round(np.std(data[1]), 5)))
        self.batch_size_label.setText(str(batch_size))

        print("Plotting data...")
        plot_data(self.axes, data)
        self.canvas.draw()
        self.canvas.flush_events()

        self.batch_size = batch_size
        self.data = data

    def accept_sample(self):
        label = None
        try:
            label = float(self.label_edit.text())
        except ValueError:
            try:
                label = int(self.label_edit.text())
            except ValueError:
                print("Failed to interpret label")
                return

        if label < -90.0 or 90.0 < label:
            print("Label not in range")
            return

        print("Saving sample...")
        save_sample(FILE_PATH + '32kHz_' + str(self.batch_size) + '.csv', self.data, label)
        self.get_sample()

    def get_sample(self):
        print("Getting sample...")
        batch_size, data = sample(self.serial_con, 1000)
        self.set_data(batch_size, data)
        return


class TrainingWidget(QtGui.QWidget):

    def __init__(self):
        super(TrainingWidget, self).__init__()


class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle("2d sound location")
        # self.setWindowIcon(QtGui.QIcon())

        main_widget = QtGui.QWidget()
        self.setCentralWidget(main_widget)

        tabs = QtGui.QTabWidget()
        tabs.addTab(SamplingWidget(), "Sampling")
        tabs.addTab(TrainingWidget(), "Training")
        # extract_action = QtGui.QAction("blabal", self)
        # extract_action.setShortcut("Ctrl+Q")
        # extract_action.setStatusTip("Leave the app")
        # extract_action.triggered.connect(self.close_application)

        # self.statusBar()

        # mainMenu = self.menuBar()
        # fileMenu = mainMenu.addMenu("&File")
        # fileMenu.addAction(extract_action)

        layout = QtGui.QGridLayout()
        layout.addWidget(tabs)
        main_widget.setLayout(layout)
        self.show()


def main():
    app = QtGui.QApplication(sys.argv)
    GUI = Window()

    sys.exit(app.exec_()) # keeps app from exiting!!


if __name__ == "__main__":
    main()
