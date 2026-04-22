from controllers.mainwindow_ctrl import Cocomo2Mainwindow
from function_point import FunctionPointMethod

from PyQt5.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)
    window = Cocomo2Mainwindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
