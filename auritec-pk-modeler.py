from model import one_compartment_model, two_compartment_model
from scipy.optimize import curve_fit
import pandas as pd
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import sys
import numpy as np
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

        self.vbox2 = QVBoxLayout()
        self.combo2 = QComboBox()
        self.combo2.addItems(["2-compartment", "1-compartment"])
        self.vbox2.addWidget(self.combo2)

        self.hboxka = QHBoxLayout()
        kA = QLabel("kA (absorption rate):")
        self.kA_input = QLineEdit()
        self.hboxka.addWidget(kA)
        self.hboxka.addWidget(self.kA_input)

        self.hboxkel = QHBoxLayout()
        kel = QLabel("kEl (elimination rate):")
        self.kel_input = QLineEdit()
        self.hboxkel.addWidget(kel)
        self.hboxkel.addWidget(self.kel_input)

        self.hboxd = QHBoxLayout()
        dose = QLabel("Dose (mg/kg):")
        self.d_input = QLineEdit()
        self.hboxd.addWidget(dose)
        self.hboxd.addWidget(self.d_input)

        self.hboxvd = QHBoxLayout()
        vd = QLabel("Vol of dist Vd (L/kg):")
        self.vd_input = QLineEdit()
        self.hboxvd.addWidget(vd)
        self.hboxvd.addWidget(self.vd_input)

        self.hboxInt = QHBoxLayout()
        interval = QLabel("Interval (days):")
        self.int_input = QLineEdit()
        self.hboxInt.addWidget(interval)
        self.hboxInt.addWidget(self.int_input)

        self.hboxnumd = QHBoxLayout()
        num_d = QLabel("Num doses:")
        self.numd_input = QLineEdit()
        self.hboxnumd.addWidget(num_d)
        self.hboxnumd.addWidget(self.numd_input)

        self.combo3 = QComboBox()
        self.combo3.addItems(["Linear Scale", "Log Scale"])
        self.vbox2.addWidget(self.combo3)

        # Set the central widget of the Window.
        self.vbox2.addLayout(self.hboxka)
        self.vbox2.addLayout(self.hboxkel)
        self.vbox2.addLayout(self.hboxd)
        self.vbox2.addLayout(self.hboxvd)
        self.vbox2.addLayout(self.hboxInt)
        self.vbox2.addLayout(self.hboxnumd)

        calc_button2 = QPushButton("Calculate")
        calc_button2.clicked.connect(self.calc_2)
        self.vbox2.addWidget(calc_button2)

        export_button2 = QPushButton("Export to CSV")
        export_button.clicked.connect(self.exportcsv2)
        self.vbox2.addWidget(export_button2)

        widget2 = QWidget()
        widget2.setLayout(self.vbox2)

        tabwidget = QTabWidget()
        tabwidget.addTab(widget, "Param Calculator")
        tabwidget.addTab(widget2, "Multiple Dose Calculator")

        self.setCentralWidget(tabwidget)
        self.setWindowTitle("Auritec PK Modeler")

    def calc_2(self):
        ka = float(self.kA_input.text())
        kel = float(self.kel_input.text())
        dose = float(self.d_input.text())
        vd = float(self.vd_input.text())
        interval = int(self.int_input.text())
        num_doses = int(self.numd_input.text())

        css = (ka * dose) / (kel * (ka - kel) * vd)
        model_type = self.combo2.currentText()

        # Define the function to calculate plasma levels
        def plasma_levels(t):
            plasma = np.zeros_like(t)
            for i in range(num_doses):
                if i == 0:
                    ct = (dose / vd) * (ka / (ka + kel)) * (1 -
                                                            np.exp(-(ka + kel) * t[i])) + css * np.exp(-kel * t[i])
                else:
                    previous_dose_time = interval * i
                    time_since_last_dose = t - previous_dose_time
                    if model_type == "1-compartment":
                        ct = (dose / vd) * (ka / (ka + kel)) * ((1 - np.exp(-kel * time_since_last_dose)) / (
                            1 - np.exp(-(ka + kel) * time_since_last_dose)))
                        ct += css * (np.exp(-kel * time_since_last_dose) - np.exp(-(
                            ka + kel) * time_since_last_dose) * np.exp(-kel * interval))
                        ct += plasma * np.exp(-kel * interval)
                    elif model_type == "2-compartment":
                        ct = (dose / vd) * (ka / (ka + kel)) * \
                            (1 - np.exp(-ka * time_since_last_dose))
                        ct += css * (np.exp(-kel * time_since_last_dose) - np.exp(-(
                            ka + kel) * time_since_last_dose) * np.exp(-kel * interval))
                        ct += plasma * np.exp(-kel * interval)
                plasma = np.where(t >= interval * i, ct, plasma)
            return plasma

        # Define the time range
        self.time2 = np.linspace(0, 365, 1000)

        # Calculate the plasma levels for the time ranges
        self.plasma = plasma_levels(self.time2)

    def exportcsv2(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        d = {'Time': self.time2,
             'Plasma Level': self.plasma}
        df = pd.DataFrame(d)
        if dlg.exec():
            directory, _filter = dlg.getSaveFileName()
            df.to_csv(str(directory) + '.csv' if len(str(directory)) > 4 and str(directory)
                      [:-4] != '.csv' else '')

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
