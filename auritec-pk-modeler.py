from model import three_compartment_model
from scipy.optimize import curve_fit
import pandas as pd
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import sys
import matplotlib
matplotlib.use('QtAgg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # NOQA
from matplotlib.figure import Figure  # NOQA


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vbox = QVBoxLayout()
        upload_btn = QPushButton("Upload data file")
        upload_btn.clicked.connect(self.getfiles)
        self.input = None

        hbox1 = QHBoxLayout()
        A = QLabel("A:")
        self.A_input = QLineEdit()
        hbox1.addWidget(A)
        hbox1.addWidget(self.A_input)

        hbox2 = QHBoxLayout()
        alpha = QLabel("alpha:")
        self.alpha_input = QLineEdit()
        hbox2.addWidget(alpha)
        hbox2.addWidget(self.alpha_input)

        hbox3 = QHBoxLayout()
        B = QLabel("B:")
        self.B_input = QLineEdit()
        hbox3.addWidget(B)
        hbox3.addWidget(self.B_input)

        hbox4 = QHBoxLayout()
        beta = QLabel("beta:")
        self.beta_input = QLineEdit()
        hbox4.addWidget(beta)
        hbox4.addWidget(self.beta_input)

        # Set the central widget of the Window.
        self.vbox.addWidget(upload_btn)
        self.vbox.addLayout(hbox1)
        self.vbox.addLayout(hbox2)
        self.vbox.addLayout(hbox3)
        self.vbox.addLayout(hbox4)

        calc_button = QPushButton("Calculate")
        calc_button.clicked.connect(self.calc)
        self.vbox.addWidget(calc_button)

        self.results = QLabel()
        self.vbox.addWidget(self.results)

        widget = QWidget()
        widget.setLayout(self.vbox)
        self.setCentralWidget(widget)
        self.setWindowTitle("Auritec PK Modeler")

    def getfiles(self):
        filenames = QFileDialog.getOpenFileName(self, 'Open CSV input file')

        if filenames[0]:
            self.input = pd.read_csv(filenames[0])

    def calc(self):
        # TODO: validate inputs
        params, _ = curve_fit(three_compartment_model, self.input["time"], self.input["plasma_level"], p0=[float(
            self.A_input.text()), float(self.alpha_input.text()), float(self.B_input.text()), float(self.beta_input.text())])
        A, alpha, B, beta = params
        label_text = f"A: {A}, alpha: {alpha}, B: {B}, beta: {beta}"
        print(label_text)
        self.results.setText(label_text)

        fitted_plasma_level = three_compartment_model(
            self.input["time"], A, alpha, B, beta)
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.vbox.addWidget(self.canvas)
        self.canvas.axes.cla()
        self.canvas.axes.plot(
            self.input["time"], self.input["plasma_level"], marker="o", linestyle="--", label="Data")
        self.canvas.axes.plot(
            self.input["time"], fitted_plasma_level, marker=".", linestyle="-", label="Fitted Curve")

        self.canvas.axes.set_xlabel("Time")
        self.canvas.axes.set_ylabel("Plasma Level")
        self.canvas.axes.set_title("Two-Compartment Pharmacokinetics")
        self.canvas.axes.legend()
        self.canvas.axes.grid(True)
        self.show()

        self.resize(300, 700)


app = QApplication(sys.argv)

window = MainWindow()
window.resize(300, 200)
window.show()

app.exec()
