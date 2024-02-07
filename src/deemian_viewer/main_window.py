import json
import os, sys
from pathlib import Path
import tarfile

import pandas as pd
from PySide6 import QtCore, QtNetwork, QtWidgets, QtWebChannel, QtWebSockets

from deemian_viewer.data_processing import setup_dataframe
from deemian_viewer.molecule_view import MoleculeView
from deemian_viewer.pandas_table import PandasReactTableModel


class WebSocketTransport(QtWebChannel.QWebChannelAbstractTransport):
    """QWebChannelAbstractSocket implementation using a QWebSocket internally
        The transport delegates all messages received over the QWebSocket over
        its textMessageReceived signal. Analogously, all calls to
        sendTextMessage will be sent over the QWebSocket to the remote client.
    """

    def __init__(self, socket):
        """Construct the transport object and wrap the given socket.
           The socket is also set as the parent of the transport object."""
        super().__init__(socket)
        self._socket = socket
        self._socket.textMessageReceived.connect(self.text_message_received)
        self._socket.disconnected.connect(self._disconnected)

    def __del__(self):
        """Destroys the WebSocketTransport."""
        self._socket.deleteLater()

    def _disconnected(self):
        self.deleteLater()

    def sendMessage(self, message):
        """Serialize the JSON message and send it as a text message via the
           WebSocket to the client."""
        doc = QtCore.QJsonDocument(message)
        json_message = str(doc.toJson(QtCore.QJsonDocument.Compact), "utf-8")
        # Remove RuntimeError below when exiting caused by race condition when collecting garbage
        # RuntimeError: Internal C++ object (PySide6.QtWebSockets.QWebSocket) already deleted.
        try:
            self._socket.sendTextMessage(json_message)
        except RuntimeError:
            pass

    @QtCore.Slot(str)
    def text_message_received(self, message_data_in):
        """Deserialize the stringified JSON messageData and emit
           messageReceived."""
        message_data = QtCore.QByteArray(bytes(message_data_in, encoding='utf8'))
        message = QtCore.QJsonDocument.fromJson(message_data)
        if message.isNull():
            print("Failed to parse text message as JSON object:", message_data)
            return
        if not message.isObject():
            print("Received JSON message that is not an object: ", message_data)
            return
        self.messageReceived.emit(message.object(), self)


class WebSocketClientWrapper(QtCore.QObject):
    """Wraps connected QWebSockets clients in WebSocketTransport objects.
       This code is all that is required to connect incoming WebSockets to
       the WebChannel. Any kind of remote JavaScript client that supports
       WebSockets can thus receive messages and access the published objects.
    """
    client_connected = QtCore.Signal(WebSocketTransport)

    def __init__(self, server, parent=None):
        """Construct the client wrapper with the given parent. All clients
           connecting to the QWebSocketServer will be automatically wrapped
           in WebSocketTransport objects."""
        super().__init__(parent)
        self._server = server
        self._server.newConnection.connect(self.handle_new_connection)
        self._transports = []

    @QtCore.Slot()
    def handle_new_connection(self):
        """Wrap an incoming WebSocket connection in a WebSocketTransport
           object."""
        socket = self._server.nextPendingConnection()
        transport = WebSocketTransport(socket)
        self._transports.append(transport)
        self.client_connected.emit(transport)


class Backend(QtCore.QObject):
    """An instance of this class gets published over the WebChannel."""

    def __init__(self, backend_dictionary, viewer):
        """Initialize the QObject."""
        super().__init__()
        self.open_deemian = backend_dictionary["openfile"]
        self.set_conformation = backend_dictionary["set_conformation"]
        self.handle_tree_pair = viewer.handle_tree_pair
        self.handle_selection_popper = viewer.handle_selection_popper
    
    @QtCore.Slot()
    def openFile(self):
        self.open_deemian()
    
    @QtCore.Slot(str)
    def setConformation(self, o):
        conformation = json.loads(o)
        self.set_conformation(conformation["position"])
    
    @QtCore.Slot(str)
    def handleTreePair(self, o):
        checked = json.loads(o)
        self.handle_tree_pair(checked)
    
    @QtCore.Slot(str)
    def handleSelection(self, o):
        checked = json.loads(o)
        self.handle_selection_popper(checked)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.deemian_data = {}
        self.deemian_loaded = False
        self.reactmodels = {}
        self.isPlaying = False
        self.dirname = os.path.dirname(os.path.realpath(__file__))

        self.widget = QtWidgets.QWidget()
        self.viewer = MoleculeView()

        # https://gist.github.com/vidjuheffex/a9f352334b80c4a1a2f0e14da23fce04
        # https://www.call-with.cc/post/remote-frontends-for-pyside2-based-vfx-tooling-over

        self.server = QtWebSockets.QWebSocketServer("QWebChannel PySide Example",
                              QtWebSockets.QWebSocketServer.NonSecureMode, )

        if not self.server.listen(QtNetwork.QHostAddress.LocalHost, 12345):
            print("Failed to open web socket server at port 12345.")
            sys.exit(-1)

        # wrap WebSocket clients in QWebChannelAbstractTransport objects
        self.client_wrapper = WebSocketClientWrapper(self.server)

        # setup the channel
        self.channel = QtWebChannel.QWebChannel()
        self.client_wrapper.client_connected.connect(self.channel.connectTo)

        self.backend_dictionary = dict(
            openfile=self.open_file,
            set_conformation=self.move_slider
        )

        self.backend = Backend(self.backend_dictionary, self.viewer)
        self.channel.registerObject("backend", self.backend)

        main_layout = QtWidgets.QGridLayout(self.widget)
        main_layout.addWidget(self.viewer, 0, 0)
        self.setLayout(main_layout)
        self.setCentralWidget(self.widget)
    
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
            self.viewer.load_deemian(self.deemian_data, dirname)
            self.deemian_loaded = True
            
    def setup_table(self, metadata):
        self.viewer.runJS(f"window.tableData.length = 0")
        self.reactmodels = PandasReactTableModel()
        for interacting_subject in metadata["measurement"]["interacting_subjects"]:
            name = interacting_subject["name"]
            data_name = interacting_subject["results"]
            data = setup_dataframe(self.deemian_data[data_name])

            self.reactmodels.register_table(name, data)

        for i in range(len(self.reactmodels)):
            self.viewer.runJS(f"window.tableData.push({self.reactmodels.get_data(i)})")
        
        self.viewer.runJS("if (document.getElementById('tabforceUpdate')) {document.getElementById('tabforceUpdate').click()}")

    def setup_frameSelect(self, metadata):
        min_value, max_value = metadata["measurement"]["conformation_range"]

        if (max_value - min_value) > 0:
            self.viewer.runJS("window.playerMinMax.length = 0")
            self.viewer.runJS(f"window.playerMinMax.push({min_value});window.playerMinMax.push({max_value})")
            self.viewer.runJS("document.getElementById('enablePlayer').click()")
        else:
            self.viewer.runJS("document.getElementById('disablePlayer').click()")

    
    @QtCore.Slot(int)
    def move_slider(self, num):
        self.viewer.runJS(f"window.tableData.length = 0")
        self.reactmodels.set_frame(num)

        for i in range(len(self.reactmodels)):
            self.viewer.runJS(f"window.tableData.push({self.reactmodels.get_data(i)})")

        self.viewer.runJS("if (document.getElementById('tabforceUpdate')) {document.getElementById('tabforceUpdate').click()}")

        if self.deemian_loaded:
            self.viewer.set_frame(num)

    @QtCore.Slot()
    def quit_app(self):
        self.app.quit()
