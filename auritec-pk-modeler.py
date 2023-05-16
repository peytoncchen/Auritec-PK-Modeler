from model import one_compartment_model, two_compartment_model
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

        self.combo = QComboBox()
        self.combo.addItems(["2-compartment", "1-compartment"])
        self.combo.currentTextChanged.connect(self.on_change_comp)
        self.vbox.addWidget(self.combo)

        self.hbox1 = QHBoxLayout()
        A = QLabel("A:")
        self.A_input = QLineEdit()
        self.hbox1.addWidget(A)
        self.hbox1.addWidget(self.A_input)

        self.hbox2 = QHBoxLayout()
        alpha = QLabel("alpha:")
        self.alpha_input = QLineEdit()
        self.hbox2.addWidget(alpha)
        self.hbox2.addWidget(self.alpha_input)

        self.hbox3 = QHBoxLayout()
        B = QLabel("B:")
        self.B_input = QLineEdit()
        self.hbox3.addWidget(B)
        self.hbox3.addWidget(self.B_input)

        self.hbox4 = QHBoxLayout()
        beta = QLabel("beta:")
        self.beta_input = QLineEdit()
        self.hbox4.addWidget(beta)
        self.hbox4.addWidget(self.beta_input)

        # Set the central widget of the Window.
        self.vbox.addWidget(upload_btn)
        self.vbox.addLayout(self.hbox1)
        self.vbox.addLayout(self.hbox2)
        self.vbox.addLayout(self.hbox3)
        self.vbox.addLayout(self.hbox4)

        calc_button = QPushButton("Calculate")
        calc_button.clicked.connect(self.calc)
        self.vbox.addWidget(calc_button)

        export_button = QPushButton("Export to CSV")
        export_button.clicked.connect(self.exportcsv)
        self.vbox.addWidget(export_button)

        self.results = QLabel()
        self.vbox.addWidget(self.results)

        self.change_beta_button = QPushButton("Change Beta")
        self.change_beta_button.clicked.connect(self.change_calc_beta)
        hbox5 = QHBoxLayout()
        self.c_beta = QLabel("Change beta:")
        self.changed_beta = QLineEdit()
        hbox5.addWidget(self.c_beta)
        hbox5.addWidget(self.changed_beta)
        self.vbox.addLayout(hbox5)
        self.vbox.addWidget(self.change_beta_button)

        widget = QWidget()
        widget.setLayout(self.vbox)
        self.setCentralWidget(widget)
        self.setWindowTitle("Auritec PK Modeler")

    def on_change_comp(self):
        if self.combo.currentText() == "1-compartment":
            self.B_input.setEnabled(False)
            self.beta_input.setEnabled(False)
            self.c_beta.setText("Change Alpha")
            self.change_beta_button.setText("Change Alpha")
        else:
            self.B_input.setEnabled(True)
            self.beta_input.setEnabled(True)
            self.c_beta.setText("Change Beta")
            self.change_beta_button.setText("Change Beta")

    def change_calc_beta(self):
        if self.combo.currentText() == "2-compartment":
            params, _ = curve_fit(two_compartment_model, self.input["time"], self.input["plasma_level"], p0=[float(
                self.A_input.text()), float(self.alpha_input.text()), float(self.B_input.text()), float(self.beta_input.text())])
            A, alpha, B, _ = params
            label_text = f"A: {'%.3f'%A}, alpha: {'%.3f'%alpha}, B: {'%.3f'%B}, beta: {'%.3f'%float(self.changed_beta.text())}"
            print(label_text)
            self.results.setText(label_text)

            self.fitted_plasma_level = two_compartment_model(
                self.input["time"], A, alpha, B, float(self.changed_beta.text()))
            if hasattr(self, 'canvas'):
                self.vbox.removeWidget(self.canvas)
                self.canvas = None
            self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
            self.vbox.addWidget(self.canvas)
            self.canvas.axes.cla()
            self.canvas.axes.plot(
                self.input["time"], self.input["plasma_level"], marker="o", linestyle="--", label="Data")
            self.canvas.axes.plot(
                self.input["time"], self.fitted_plasma_level, marker=".", linestyle="-", label="Fitted Curve")

            self.canvas.axes.set_xlabel("Time")
            self.canvas.axes.set_ylabel("Plasma Level")
            self.canvas.axes.set_title("Two-Compartment Pharmacokinetics")
            self.canvas.axes.legend()
            self.canvas.axes.grid(True)
            self.show()

            self.resize(500, 700)
        else:
            params, _ = curve_fit(one_compartment_model, self.input["time"], self.input["plasma_level"], p0=[float(
                self.A_input.text()), float(self.alpha_input.text())])
            A, _ = params
            label_text = f"A: {'%.3f'%A}, alpha: {'%.3f'%float(self.changed_beta.text())}"
            print(label_text)
            self.results.setText(label_text)

            self.fitted_plasma_level = one_compartment_model(
                self.input["time"], A, float(self.changed_beta.text()))
            if hasattr(self, 'canvas'):
                self.vbox.removeWidget(self.canvas)
                self.canvas = None
            self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
            self.vbox.addWidget(self.canvas)
            self.canvas.axes.cla()
            self.canvas.axes.plot(
                self.input["time"], self.input["plasma_level"], marker="o", linestyle="--", label="Data")
            self.canvas.axes.plot(
                self.input["time"], self.fitted_plasma_level, marker=".", linestyle="-", label="Fitted Curve")

            self.canvas.axes.set_xlabel("Time")
            self.canvas.axes.set_ylabel("Plasma Level")
            self.canvas.axes.set_title("One-Compartment Pharmacokinetics")
            self.canvas.axes.legend()
            self.canvas.axes.grid(True)
            self.show()

            self.resize(500, 700)

    def exportcsv(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        d = {'Time': self.input["time"],
             'Plasma Level': self.fitted_plasma_level}
        df = pd.DataFrame(d)
        if dlg.exec():
            directory, _filter = dlg.getSaveFileName()
            df.to_csv(str(directory) + '.csv' if len(str(directory)) > 4 and str(directory)
                      [:-4] != '.csv' else '')

    def getfiles(self):
        filenames = QFileDialog.getOpenFileName(self, 'Open CSV input file')

        if filenames[0]:
            self.input = pd.read_csv(filenames[0])

    def calc(self):
        # TODO: validate inputs
        if self.combo.currentText() == "2-compartment":
            params, _ = curve_fit(two_compartment_model, self.input["time"], self.input["plasma_level"], p0=[float(
                self.A_input.text()), float(self.alpha_input.text()), float(self.B_input.text()), float(self.beta_input.text())])
            A, alpha, B, beta = params
            label_text = f"A: {'%.3f'%A}, alpha: {'%.3f'%alpha}, B: {'%.3f'%B}, beta: {'%.3f'%beta}"
            print(label_text)
            self.results.setText(label_text)

            self.fitted_plasma_level = two_compartment_model(
                self.input["time"], A, alpha, B, beta)
            if hasattr(self, 'canvas'):
                self.vbox.removeWidget(self.canvas)
                self.canvas = None
            self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
            self.vbox.addWidget(self.canvas)
            self.canvas.axes.cla()
            self.canvas.axes.plot(
                self.input["time"], self.input["plasma_level"], marker="o", linestyle="--", label="Data")
            self.canvas.axes.plot(
                self.input["time"], self.fitted_plasma_level, marker=".", linestyle="-", label="Fitted Curve")

            self.canvas.axes.set_xlabel("Time")
            self.canvas.axes.set_ylabel("Plasma Level")
            self.canvas.axes.set_title("Two-Compartment Pharmacokinetics")
            self.canvas.axes.legend()
            self.canvas.axes.grid(True)
            self.show()

            self.resize(500, 700)
        else:
            params, _ = curve_fit(one_compartment_model, self.input["time"], self.input["plasma_level"], p0=[float(
                self.A_input.text()), float(self.alpha_input.text())])
            A, alpha = params
            label_text = f"A: {'%.3f'%A}, alpha: {'%.3f'%alpha}"
            print(label_text)
            self.results.setText(label_text)

            self.fitted_plasma_level = one_compartment_model(
                self.input["time"], A, alpha)
            if hasattr(self, 'canvas'):
                self.vbox.removeWidget(self.canvas)
                self.canvas = None
            self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
            self.vbox.addWidget(self.canvas)
            self.canvas.axes.cla()
            self.canvas.axes.plot(
                self.input["time"], self.input["plasma_level"], marker="o", linestyle="--", label="Data")
            self.canvas.axes.plot(
                self.input["time"], self.fitted_plasma_level, marker=".", linestyle="-", label="Fitted Curve")

            self.canvas.axes.set_xlabel("Time")
            self.canvas.axes.set_ylabel("Plasma Level")
            self.canvas.axes.set_title("One-Compartment Pharmacokinetics")
            self.canvas.axes.legend()
            self.canvas.axes.grid(True)
            self.show()

            self.resize(500, 700)


app = QApplication(sys.argv)

window = MainWindow()
window.resize(300, 200)
window.show()

app.exec()
