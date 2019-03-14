from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal

from threading import Thread

class simulationProgressDialog(QDialog):

    simulationCanceled = pyqtSignal()

    def __init__(self):
        QDialog.__init__(self)
        loadUi("resources/SimulatingDialog.ui", self)

        self.buttonBox.rejected.connect(self.closeEvent)

    def show(self):
        self.progressBar.setValue(0)
        super().show()

    def close(self):
        super().close()

    def closeEvent(self, event = None):
        self.close()
        self.simulationCanceled.emit()

    def progressUpdate(self, progress):
        self.progressBar.setValue(int(progress * 100))

class simulationManager(QObject):

    newSimulationResult = pyqtSignal(object)
    simProgress = pyqtSignal(float)

    def __init__(self):
        super().__init__()

        self.progDialog = simulationProgressDialog()
        self.simProgress.connect(self.progDialog.progressUpdate)
        self.newSimulationResult.connect(self.progDialog.close)
        self.progDialog.simulationCanceled.connect(self.cancelSim)

        self.motor = None
        self.preferences = None

        self.currentSimThread = None
        self.threadStopped = False # Set to true to stop simulation thread after it finishes the iteration it is on

    def setPreferences(self, preferences):
        self.preferences = preferences

    def runSimulation(self, motor):
        self.motor = motor
        self.threadStopped = False
        self.progDialog.show()
        self.currentSimThread = Thread(target = self._simThread)
        self.currentSimThread.start()

    def _simThread(self):
        simRes = self.motor.runSimulation(self.preferences, self.updateProgressBar)
        if simRes is not None:
            self.newSimulationResult.emit(simRes)

    def updateProgressBar(self, prog):
        self.simProgress.emit(prog)
        return self.threadStopped

    def cancelSim(self):
        self.threadStopped = True