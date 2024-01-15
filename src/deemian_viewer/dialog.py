from PySide6 import QtCore, QtWidgets

class RunCommandDialog(QtWidgets.QDialog):
    def __init__(self, viewer, parent=None):
        super().__init__(parent)
        
        self.page = viewer.page()
        self.resize(600, 300)

        self.textedit = QtWidgets.QPlainTextEdit(self)
        self.button_command = QtWidgets.QPushButton('run')
        self.button_command.clicked.connect(self.run_javascript)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.textedit)
        self.layout.addWidget(self.button_command)
        self.setLayout(self.layout)
        print(self.textedit.toPlainText())
    
    @QtCore.Slot()
    def run_javascript(self):
        command = self.textedit.toPlainText()
        self.page.runJavaScript(command)
