import sys

from PySide6 import QtCore, QtWidgets

from deemian_viewer.main_window import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)
    window.setWindowTitle("Deemian Viewer")

    window.showMaximized()

    app.exec()

if __name__ == "__main__":
    main()
