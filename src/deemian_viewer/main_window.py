import json
import os
from pathlib import Path
import tarfile

import pandas as pd
from PySide6 import QtCore, QtGui, QtWidgets

from deemian_viewer.data_processing import setup_dataframe
from deemian_viewer.dialog import RunCommandDialog
from deemian_viewer.molecule_view import MoleculeView
from deemian_viewer.pandas_table import PandasTableModel

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.deemian_data = {}
        self.deemian_loaded = False
        self.models = {}
        self.tables = {}
        self.isPlaying = False
        self.dirname = os.path.dirname(os.path.realpath(__file__))

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        view_menu = menu_bar.addMenu("View")
        tool_menu = menu_bar.addMenu("Tool")
        open_action = file_menu.addAction("Open Deemian file")
        quit_action = file_menu.addAction("Quit")
        max_mol_action = view_menu.addAction("Maximize Molecule View")
        command_action = tool_menu.addAction("Run JS Command")
        open_action.triggered.connect(self.open_file)
        quit_action.triggered.connect(self.quit_app)
        max_mol_action.triggered.connect(self.max_mol_view)
        command_action.triggered.connect(self.run_command)

        self.widget = QtWidgets.QWidget()

        self.viewer = MoleculeView()
        self.page = self.viewer.page()

        self.tree_pair = QtWidgets.QTreeWidget(self.widget)
        self.tree_pair.setHeaderLabel("Interacting Subjects")

        self.tree_selection = QtWidgets.QTreeWidget(self.widget)
        self.tree_selection.setHeaderLabel("Visualize Selections")

        self.tabTable = QtWidgets.QTabWidget()
        self.tabTable.setMinimumHeight(400)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMaximum(1)
        self.slider.valueChanged.connect(self.move_slider)

        self.playButton = QtWidgets.QPushButton()
        self.playButton.setIcon(QtGui.QIcon(self.dirname + '/icons/play.png'))
        self.playButton.clicked.connect(self.play_trajectory)
        self.pauseButton = QtWidgets.QPushButton()
        self.pauseButton.setIcon(QtGui.QIcon(self.dirname + '/icons/pause.png'))
        self.pauseButton.hide()
        self.pauseButton.clicked.connect(self.pause_trajectory)
        self.prevButton = QtWidgets.QPushButton()
        self.prevButton.setIcon(QtGui.QIcon(self.dirname + '/icons/back.png'))
        self.prevButton.clicked.connect(self.decrement_frame)
        self.nextButton = QtWidgets.QPushButton()
        self.nextButton.setIcon(QtGui.QIcon(self.dirname + '/icons/next.png'))
        self.nextButton.clicked.connect(self.increment_frame)

        self.frameSelect = QtWidgets.QLineEdit()
        self.frameSelect.setFixedSize(QtCore.QSize(60, 25))
        self.frameSelect.setAlignment(QtCore.Qt.AlignCenter)
        self.frameSelect.setText('1')
        self.frameSelect.returnPressed.connect(self.select_frame)
        
        player_layout = QtWidgets.QHBoxLayout()
        player_layout.addWidget(self.playButton)
        player_layout.addWidget(self.pauseButton)
        player_layout.addWidget(self.slider)
        player_layout.addWidget(self.prevButton)
        player_layout.addWidget(self.frameSelect)
        player_layout.addWidget(self.nextButton)

        main_layout = QtWidgets.QGridLayout(self.widget)

        main_layout.addWidget(self.viewer, 0, 0, 2, 1)
        main_layout.addWidget(self.tree_pair, 0, 1)
        main_layout.addWidget(self.tree_selection, 0, 2)
        main_layout.addWidget(self.tabTable, 1, 1, 1, 2)
        main_layout.addLayout(player_layout, 2, 0)

        self.setLayout(main_layout)
        self.setCentralWidget(self.widget)
    
    @QtCore.Slot()
    def run_command(self):
        dialog = RunCommandDialog(self.viewer, self.widget)
        dialog.setWindowTitle("Run JavaScript Command")
        dialog.exec()
    
    @QtCore.Slot()
    def open_file(self):
        self.deemian_loaded = False
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption='Open file', dir='.', filter="Deemian Data files (*.dd)")
        if filename:
            with tarfile.open(filename) as tf:
                for entry in tf:
                    if entry.name == "deemian.json":
                        binary_json = tf.extractfile(entry).read()
                        self.deemian_data["deemian.json"] = json.loads(binary_json)
                    elif entry.name.split(".")[-1] == "parquet":
                        self.deemian_data[entry.name]  = pd.read_parquet(tf.extractfile(entry), engine="fastparquet")
                    else:
                        self.deemian_data[entry.name] = tf.extractfile(entry).read().decode("utf-8")
            
            metadata = self.deemian_data["deemian.json"]

            self.setup_table(metadata)
            self.setup_frameSelect(metadata)
            dirname = Path(os.path.dirname(filename))
            self.viewer.load_deemian(self.deemian_data, dirname, self.tree_pair, self.tree_selection)
            self.deemian_loaded = True
            
    def setup_table(self, metadata):
        self.tabTable.clear()
        for interacting_subject in metadata["measurement"]["interacting_subjects"]:
            name = interacting_subject["name"]
            data_name = interacting_subject["results"]
            data = setup_dataframe(self.deemian_data[data_name])

            self.models[name] = PandasTableModel(data)
            self.tables[name] = QtWidgets.QTableView()

            self.tables[name].setModel(self.models[name])
            self.tables[name].setAlternatingRowColors(True)
            self.tables[name].hideColumn(6)
            self.tables[name].setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.tables[name].setStyleSheet(
                            "QTableView {"
                            "font-size: 14px;"
                            "}"
                            "QHeaderView::section{background-color: #ffffff; "
                            "font-weight: bold; "
                            "padding-top: 1px;"
                            "padding-bottom: 1px;"
                            "color: #3467ba; "
                            "border:0px; "
                            "border-left: 1px solid #ababab; "
                            "border-right: 1px solid #ababab;"
                            "border-bottom: 1px solid gray;}"
                        )
            header = self.tables[name].horizontalHeader()
            header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
            header.setMinimumSectionSize(45)
            header.setStretchLastSection(True)

            self.tabTable.addTab(self.tables[name], name)

    def setup_frameSelect(self, metadata):
        min_value, max_value = metadata["measurement"]["conformation_range"]

        onlyInt = QtGui.QIntValidator()
        onlyInt.setRange(min_value, max_value)
        self.frameSelect.setValidator(onlyInt)
        self.frameSelect.setText(str(min_value))

        self.slider.setRange(min_value, max_value)
    
    @QtCore.Slot(int)
    def select_frame(self):
        frame = int(self.frameSelect.text())
        self.slider.setValue(frame)
    
    @QtCore.Slot(int)
    def move_slider(self, num):
        self.frameSelect.setText(str(num))
        if self.deemian_loaded:
            self.viewer.set_frame(num)
            for model in self.models.values():
                model.set_frame(num)

    @QtCore.Slot()
    def increment_frame(self):
        self.slider.setValue(self.slider.value() + 1)
    
    @QtCore.Slot()
    def decrement_frame(self):
        self.slider.setValue(self.slider.value() - 1)
    
    def playing_trajectory(self):
        if self.isPlaying:
            value = self.slider.value()
            if value == self.slider.maximum():
                value = self.slider.minimum() - 1
            self.slider.setValue(value + 1)
            QtCore.QTimer.singleShot(900, self.playing_trajectory)

    @QtCore.Slot()
    def play_trajectory(self):
        self.playButton.hide()
        self.pauseButton.show()

        self.isPlaying = True
        self.playing_trajectory()
            
    @QtCore.Slot()
    def pause_trajectory(self):
        self.isPlaying = False

        self.playButton.show()
        self.pauseButton.hide()

    @QtCore.Slot()
    def max_mol_view(self):
        if self.tree_pair.isHidden():
            self.tree_pair.show()
            self.tree_selection.show()
            self.tabTable.show()
        else:
            self.tree_pair.hide()
            self.tree_selection.hide()
            self.tabTable.hide()

    @QtCore.Slot()
    def quit_app(self):
        self.app.quit()
