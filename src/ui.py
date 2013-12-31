# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
from ftp import FTP

class mainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        
        super(mainWindow, self).__init__()
        self.initLayout()

    def initLayout(self):
        
        self.statusBar()
        menuBar = self.menuBar()

        exitAction = QtGui.QAction(u'退出', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip(u'退出 SimpleFTP')
        exitAction.triggered.connect(QtGui.qApp.quit)

        self.fileMenu = menuBar.addMenu(u'菜单')
        self.fileMenu.addAction(exitAction)

        self.setWindowTitle(u'SimpleFTP')
        self.show()
        
        
def main():

    app = QtGui.QApplication(sys.argv)
    ex = mainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

