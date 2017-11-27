from PyQt5.QtCore import QDateTime, Qt, QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QPen,  QColor, QFont, QIntValidator
from PyQt5.QtWidgets import (QApplication, QDialog, QDial, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QSizePolicy,
    QInputDialog,  QLineEdit, QDesktopWidget)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

zigzag = False

class WidgetGallery(QDialog):
    valueSignal = pyqtSignal()

    # Parametros da linha
    qtd_iteracoes = 10
    R0 = 5
    Rl = 15
    Rg = 0
    E = 100

    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)
        img = QLabel(self)
        pixmap = QPixmap('static/linha500.png')
        img.setPixmap(pixmap)
        img.setAlignment(Qt.AlignCenter)
        self.getE()
        self.getRg()
        self.getR0()
        self.getRl()
        self.getQtdIteracoes()

        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(img, 1, 0)
        self.mainLayout.addWidget(self.entradas(), 2, 0)
        self.mainLayout.addWidget(
            PlotZigZag(self,
            width=5, height=4, qtd_iteracoes=self.qtd_iteracoes, R0=self.R0,
            Rl=self.Rl, Rg=self.Rg, E=self.E
            ),
            1, 1)
        self.mainLayout.addWidget(
            PlotVl(self,
            width=5, height=4, qtd_iteracoes=self.qtd_iteracoes, R0=self.R0,
            Rl=self.Rl, Rg=self.Rg, E=self.E
            ),
            2, 1)



        self.setLayout(self.mainLayout)
        self.setWindowTitle("Diagrama de Zig-Zag - Linha de trasmissão")


    def entradas(self):
        groupBox = QGroupBox("Parâmetros da linha")
        groupBox.setCheckable(True)
        groupBox.setChecked(True)

        pushButton = QPushButton("&Gerar diagramas")
        self.R0Label = QLabel("Impedancia de Caracteristica (Z):")
        self.R0Input = QLineEdit(self)
        self.R0Input.setText(str(self.R0))
        self.RlLabel = QLabel("Impedancia da Carga (Z):")
        self.RlInput = QLineEdit(self)
        self.RlInput.setText(str(self.Rl))
        self.RgLabel = QLabel("Impedancia do Gerador (Z):")
        self.RgInput = QLineEdit(self)
        self.RgInput.setText(str(self.Rg))
        self.ELabel = QLabel("Valor da Fonte de tensão (V):")
        self.EInput = QLineEdit(self)
        self.EInput.setText(str(self.E))
        # self.PLabel = QLabel("Quantidade de períodos analisados: ")
        # self.PInput = QLineEdit(self)
        # self.PInput.setText(str(self.qtd_iteracoes))


        vbox = QVBoxLayout()
        groupBox.setLayout(vbox)
        vbox.addWidget(self.R0Label)
        vbox.addWidget(self.R0Input)
        vbox.addWidget(self.RlLabel)
        vbox.addWidget(self.RlInput)
        vbox.addWidget(self.RgLabel)
        vbox.addWidget(self.RgInput)
        vbox.addWidget(self.ELabel)
        vbox.addWidget(self.EInput)
        # vbox.addWidget(self.PLabel)
        # vbox.addWidget(self.PInput)
        vbox.addWidget(pushButton)
        pushButton.clicked.connect(self.plot_chart)

        return groupBox

    def plot_chart(self):

        if self.R0Input.text() != ""  and self.RlInput.text() != "" and self.RgInput.text() != "" \
            and self.EInput.text() != "":
            self.R0 = float(self.R0Input.text())
            self.Rl = float(self.RlInput.text())
            self.Rg = float(self.RgInput.text())
            self.E = float(self.EInput.text())

            self.mainLayout.addWidget(self.entradas(), 2, 0)

            self.mainLayout.addWidget(
                PlotZigZag(self,
                width=5, height=4, qtd_iteracoes=self.qtd_iteracoes, R0=self.R0,
                Rl=self.Rl, Rg=self.Rg, E=self.E
                ),
                1, 1)
            self.mainLayout.addWidget(
                PlotVl(self,
                width=5, height=4, qtd_iteracoes=self.qtd_iteracoes, R0=self.R0,
                Rl=self.Rl, Rg=self.Rg, E=self.E
                ),
                2, 1)
            self.setLayout(self.mainLayout)


    def getQtdIteracoes(self):
        i, okPressed = QInputDialog.getInt(self, "Quantidade períodos",
            "Quantidade períodos: ", 8, 0, 14, 1)
        if okPressed:
            self.qtd_iteracoes = i + 1

    def getR0(self):
        R0, okPressed = QInputDialog.getDouble(self, "Impedancia Caracteristica",
            "Impedancia Caracteristica:", 50, 0, 10000, 2)

        if okPressed:
            self.R0 = R0

    def getRl(self):
        Rl, okPressed = QInputDialog.getDouble(self, "Impedancia da Carga",
        "Impedancia da Carga:", 150, 0, 10000, 2)

        if okPressed:
            self.Rl = Rl

    def getRg(self):
        Rg, okPressed = QInputDialog.getDouble(self, "Impedancia do Gerador",
            "Impedancia do Gerador:", 0, 0, 10000, 2)

        if okPressed:
            self.Rg = Rg

    def getE(self):
        E, okPressed = QInputDialog.getDouble(self, "Voltagem da Fonte",
            "Voltagem da fonte:", 100, 0, 10000, 2)

        if okPressed:
            self.E = E
            print(self.E)


class PlotZigZag(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, E=100, Rg=0,
    Rl=150, R0=150, qtd_iteracoes=9):
        self.Tg = (Rg - R0)/(Rg + R0)
        self.Tl = (Rl - R0)/(Rl + R0)
        self.Vl = R0 * E / (R0 + Rg)
        self.qtd_iteracoes = qtd_iteracoes

        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


        self.plot()


    def plot(self):
        coeficientes = [0] * self. qtd_iteracoes
        coeficientes[0] = 1
        for i in range(1, self.qtd_iteracoes):
            if i % 2 == 1:
                coeficientes[i] = coeficientes[i-1] * self.Tl
            else:
                coeficientes[i] = coeficientes[i-1] * self.Tg

        x_escala = 1
        y_escala = 2

        x = np.zeros(self.qtd_iteracoes)
        y = np.arange(0, self.qtd_iteracoes*2, y_escala)

        for i in range(self.qtd_iteracoes):
            if i % 2 == 1:
                x[i] = x_escala

        ax = self.figure.add_subplot(111)
        ax.axis('off')
        ax.quiver(x[:-1], y[:-1], x[1:]-x[:-1], y[1:]-y[:-1], scale_units='xy', angles='xy', scale=3)
        ax.plot(x, y, 'black', linewidth=2.5)

        ax.text(0, -2, 0)
        ax.text(x_escala, -2, "L")
        ax.set_title("Diagrama de reflexões")
        for i, coeficiente in enumerate(coeficientes):
            ax.text(-0.2, y_escala*i - 0.1*y_escala, str(i) + "T")
            ax.text((x_escala * i%2), (y_escala * i) + y_escala/2,
                "{0:.1f}".format(coeficiente * self.Vl) + " V")
        self.draw()


class PlotVl(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, E=100, Rg=0,
    Rl=150, R0=150, qtd_iteracoes=9):
        self.Tg = (Rg - R0)/(Rg + R0)
        self.Tl = (Rl - R0)/(Rl + R0)
        self.Vl = R0 * E / (R0 + Rg)
        self.E, self.Rg, self.Rl = E, Rg, Rl
        self.qtd_iteracoes = qtd_iteracoes

        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


        self.plot()


    def plot(self):
        coeficientes = [0] * self.qtd_iteracoes
        coeficientes[0] = 1
        for i in range(1, self.qtd_iteracoes):
            if i % 2 == 1:
                coeficientes[i] = coeficientes[i-1] * self.Tl
            else:
                coeficientes[i] = coeficientes[i-1] * self.Tg

        x_escala = 1
        y_escala = 2

        x = np.arange(0, self.qtd_iteracoes)
        y = np.zeros(self.qtd_iteracoes)

        for i in range(1, self.qtd_iteracoes, 2):
            c_atual = 0
            for j in range(i+1):
                c_atual += coeficientes[j]

            y[i] = self.Vl * c_atual
            if (i+1) < self.qtd_iteracoes:
                y[i + 1] = self.Vl * c_atual

        x_, y_ = [x[0]], [y[0]]
        for i, v in enumerate(y[:-1]):
            if y[i] != y[i+1]:
                y_ += [y[i], y[i+1]]
                x_ += [x[i+1], x[i+1]]
            else:
                y_ += [y[i]]
                x_ += [x[i]]

        ax = self.figure.add_subplot(111)
        ax.axis('off')
        ax.plot(x_, y_, 'black', linewidth=2.5)
        for i in x:
            ax.text(i, -5*y_escala, str(i) + "T")

        y_max = np.amax(y)
        y_ = [y[0], y[-1], y_max]
        for j in np.sort(np.unique(y_)):
            ax.text(-1.5*x_escala, j, str(j) + " V")

        ax.text(np.amax(x)/2, np.amax(y)/4,
         "V na carga converge para: " + str(self.E * self.Rl / (self.Rl + self.Rg)) +"V")

        ax.set_title("Vl (tensão na carga) x T (período)")
        self.draw()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    gallery = WidgetGallery()
    sizeObject = QDesktopWidget().screenGeometry(-1)
    gallery.setFixedSize(sizeObject.width()*0.94,sizeObject.height()*0.9)
    gallery.showMaximized()

    sys.exit(app.exec_())
