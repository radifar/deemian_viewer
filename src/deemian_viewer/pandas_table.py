from PySide6 import QtCore


class PandasTableModel(QtCore.QAbstractTableModel):

    def __init__(self, data, conf=1):
        super(PandasTableModel, self).__init__()
        self._data_all = data
        self._data = self._data_all[self._data_all["conformation"] == conf]
    
    def set_frame(self, conf):
        self.beginResetModel()
        self._data = self._data_all[self._data_all["conformation"] == conf]
        self.endResetModel()

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            column = index.column()
            value = self._data.iloc[row, column]
            if column == 4:
                return f'{value:.3f}'
            return str(value)
        elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
            return QtCore.Qt.AlignmentFlag.AlignCenter

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == QtCore.Qt.Vertical:
                return str(self._data.index[section])