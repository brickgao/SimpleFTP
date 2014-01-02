from PyQt4 import QtGui
import ui, sys

def main():

    app = QtGui.QApplication(sys.argv)
    ex = ui.mainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
