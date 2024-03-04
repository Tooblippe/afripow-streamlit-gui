import sys
from pathlib import Path

from PySide6.QtUiTools import QUiLoader

from PySide6 import QtGui
from PySide6.QtCore import QFile, QTextStream
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMainWindow

Loader = QUiLoader()

__version__ = "0.0.1"
APP_NAME = "PyPSA Navigator"
APP_ICON_PATH = "ui//icons//app_icon.png"
UI_PATH = "ui/afripow.ui"
STYLESHEET_PATH = "ui/styles/stylesheet.qss"
SCREEN_RATIO = 0.9


class AfripowGui(QMainWindow):
    def __init__(self):
        super(AfripowGui, self).__init__()
        self.home = None
        self.init_ui()
        self.load_menus()
        self.assign_buttons()

    def load_menus(self):
        _menubar = self.menuBar()
        fileMenu = _menubar.addMenu("File")
        menu_item = QAction("Open", self)
        menu_item.triggered.connect(self.test_fn)
        fileMenu.addAction(menu_item)

    def assign_buttons(self):
        home = self.home
        home.testButton.clicked.connect(self.test_fn)

    def test_fn(self):
        print("test")

    def init_ui(self):
        self.apply_stylesheet()
        self.center()
        self.home = Loader.load(Path(UI_PATH))
        self.setCentralWidget(self.home)
        self.setWindowTitle(f"{APP_NAME} - {__version__}")
        self.show()

    def apply_stylesheet(self):
        file = QFile(STYLESHEET_PATH)
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        self.setStyleSheet(stream.readAll())

    def center(self):
        primary_screen = QtGui.QGuiApplication.primaryScreen()
        screen_size = QtGui.QScreen.availableSize(primary_screen)
        self.resize(
            screen_size.width() * SCREEN_RATIO,
            screen_size.height() * SCREEN_RATIO,
        )
        qr = self.frameGeometry()
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(APP_ICON_PATH))
    main_window = AfripowGui()
    sys.exit(app.exec())


if __name__ == "__main__":
    print("Application is starting ... ")
    main()
