from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction, QMenu
from PyQt5.QtCore import pyqtSignal

from .tools import changeDiameterTool, initialKNTool, maxKNTool

class toolManager(QObject):

    changeApplied = pyqtSignal()

    def __init__(self, fileManager, simulationManager):
        super().__init__()

        self.fileManager = fileManager
        self.simulationManager = simulationManager

        self.tools = {'Set': [changeDiameterTool(self), initialKNTool(self), maxKNTool(self)],
                      'Optimize': [],
                      'Design': []}

        for toolCategory in self.tools.keys():
            for tool in self.tools[toolCategory]:
                self.simulationManager.simulationDone.connect(tool.simDone)
                self.simulationManager.simCanceled.connect(tool.simCanceled)

    def setPreferences(self, pref):
        for toolCategory in self.tools.keys():
            for tool in self.tools[toolCategory]:
                tool.setPreferences(pref)

    def setupMenu(self, menu):
        for toolCategory in self.tools.keys():
            category = menu.addMenu(toolCategory)
            for tool in self.tools[toolCategory]:
                toolAction = QAction(tool.name, category)
                toolAction.setStatusTip(tool.description)
                toolAction.triggered.connect(tool.show)
                category.addAction(toolAction)

    def getMotor(self):
        return self.fileManager.getCurrentMotor()

    def updateMotor(self, motor):
        self.fileManager.addNewMotorHistory(motor)
        self.changeApplied.emit()

    def requestSimulation(self):
        motor = self.fileManager.getCurrentMotor()
        self.simulationManager.runSimulation(motor, False)