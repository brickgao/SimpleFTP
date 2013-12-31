# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
from ftp import FTP

class QMainArea(QtGui.QWidget):

    def __init__(self):

        super(QMainArea, self).__init__()
        self.initLayout()

    def initLayout(self):
        
        self.addressLable = QtGui.QLabel(u'连接地址')
        self.addressText = QtGui.QLineEdit(self)

        self.accountLable = QtGui.QLabel(u'用户名')
        self.accountText = QtGui.QLineEdit(self)

        self.passwdLable = QtGui.QLabel(u'密码')
        self.passwdText = QtGui.QLineEdit(self)
        self.passwdText.setEchoMode(QtGui.QLineEdit.Password)

        self.loginBtn = QtGui.QPushButton(u'登录')

        self.logoutBtn = QtGui.QPushButton(u'断开')

        self.uploadBtn = QtGui.QPushButton(u'上传')

        self.downloadBtn = QtGui.QPushButton(u'下载')

        self.fileListLable = QtGui.QLabel(u'服务器文件列表')
        self.fileList = QtGui.QTreeWidget()
        self.fileList.setHeaderLabels([u'文件名',
                                       u'文件大小', 
                                       u'文件类型',
                                       u'最近修改', 
                                       u'权限', 
                                       u'所有者/组'])

        self.logLable = QtGui.QLabel(u'日志')
        self.logView = QtGui.QPlainTextEdit()
        self.logView.setReadOnly(True)

        grid = QtGui.QGridLayout()
        grid.setSpacing(5)
        
        grid.addWidget(self.addressLable, 0, 1, 1, 1)
        grid.addWidget(self.addressText, 0, 2, 1, 3)
        grid.addWidget(self.accountLable, 1, 1, 1, 1)
        grid.addWidget(self.accountText, 1, 2, 1, 3)
        grid.addWidget(self.passwdLable, 2, 1, 1, 1)
        grid.addWidget(self.passwdText, 2, 2, 1, 3)
        grid.addWidget(self.loginBtn, 3, 1, 1, 2)
        grid.addWidget(self.logoutBtn, 3, 3, 1, 2)
        grid.addWidget(self.logLable, 4, 1, 1, 1)
        grid.addWidget(self.logView, 5, 1, 1, 4)
        grid.addWidget(self.fileListLable, 6, 1, 1, 1)
        grid.addWidget(self.fileList, 7, 1, 1, 4)
        grid.addWidget(self.uploadBtn, 8, 1, 1, 2)
        grid.addWidget(self.downloadBtn, 8, 3, 1, 2)
                
        self.setLayout(grid)

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

        self.mainArea = QMainArea()

        self.setCentralWidget(self.mainArea)

        self.setGeometry(100, 100, 400, 600)
        self.setMinimumSize(400, 600)
        self.setMaximumSize(400, 600)
        self.setWindowTitle(u'SimpleFTP')
        self.show()
        
        
def main():

    app = QtGui.QApplication(sys.argv)
    ex = mainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

