# -*- coding: utf-8 -*-

import sys, threading, time, os
from PyQt4 import QtGui, QtCore
from ftp import FTP
from logging import Logger, Handler, getLogger, Formatter

mutex = threading.Lock()

def append_to_widget(widget, s):
    widget.append(s)

    
class loggerHandler(Handler):

    def __init__(self, loggerWidget):
        
        self.loggerWidget = loggerWidget
        super(loggerHandler, self).__init__()

    def emit(self, record):

        self.loggerWidget.emit(QtCore.SIGNAL('newLog(QString)'), 
                                             QtCore.QString(self.format(record).decode('gbk')))

        

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
        self.loginBtn.clicked.connect(self.login)

        self.logoutBtn = QtGui.QPushButton(u'断开')
        self.logoutBtn.clicked.connect(self.logout)

        self.uploadBtn = QtGui.QPushButton(u'上传')
        self.uploadBtn.clicked.connect(self.upload)

        self.downloadBtn = QtGui.QPushButton(u'下载')
        self.downloadBtn.clicked.connect(self.download)

        self.fileListLable = QtGui.QLabel(u'服务器文件列表')
        self.fileList = QtGui.QTreeWidget()
        self.fileList.setHeaderLabels([u'文件名',
                                       u'文件大小', 
                                       u'文件类型',
                                       u'最近修改', 
                                       u'权限', 
                                       u'所有者/组'])
        self.fileList.itemDoubleClicked.connect(self.changeDirectory)
        self.connect(self,
                     QtCore.SIGNAL('needRefresh'),
                     self.refreshFileList)

        self.logLable = QtGui.QLabel(u'日志')
        self.logView = QtGui.QTextBrowser()

        self.ftp = FTP('')
        self.logger = self.ftp.logger
        self.handler = loggerHandler(self.logView)
        self.handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s'))

        self.logger.addHandler(self.handler)
        
        self.logView.connect(self.logView,
                             QtCore.SIGNAL('newLog(QString)'), 
                             lambda log: append_to_widget(self.logView, log))

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

    def login(self):
        
        if self.addressText.text() == '':
            return self.errorAlert(u'请输入服务器的地址')
        if self.accountText.text() == '' and self.passwdText.text() != '':
            return self.errorAlert(u'您已经输入密码，请输入用户名')

        t = threading.Thread(target=self.loginRun)
        t.start()

    def loginRun(self):

        global mutex

        mutex.acquire()
        
        self.ftp.url = str(self.addressText.text())
        if self.accountText.text() == '' and self.passwdText.text() == '':
            self.ftp.login()
        else:
            self.ftp.login(self.accountText.text(), 
                           self.passwdText.text())

        self.ftp.retrlines('LIST')

        self.emit(QtCore.SIGNAL('needRefresh'))
        
        mutex.release()


    def refreshFileList(self):
        
        self.fileList.clear()
        root = QtGui.QTreeWidgetItem()
        root.setText(0, u'..')
        self.fileList.addTopLevelItem(root)
        for _ in self.ftp.currentList:
            fileInfo = QtGui.QTreeWidgetItem()
            fileInfo.setText(0, _['name'])
            fileInfo.setText(1, _['size'])
            if _['permissions'][0] == 'd':
                fileInfo.setText(2, u'文件夹')
            elif _['isLn']:
                fileInfo.setText(2, u'链接')
            else:
                fileInfo.setText(2, u'非文件夹/链接')
            fileInfo.setText(3, _['date'])
            fileInfo.setText(4, _['permissions'])
            fileInfo.setText(5, _['owner'] + ' ' +  _['ownerGroup'])
            self.fileList.addTopLevelItem(fileInfo)
        

    def logout(self):
        
        t = threading.Thread(target=self.logoutRun)
        t.start()

    
    def logoutRun(self):
        
        global mutex

        mutex.acquire()

        self.ftp.quit()
        self.fileList.clear()

        mutex.release()

    
    def download(self):

        _ = self.fileList.currentItem()
        if not _:
            return self.errorAlert(u'请选择文件')
        if _.text(2) != u'非文件夹/链接':
            return self.errorAlert(u'请选择非文件夹/连接')
        fname = QtGui.QFileDialog.getSaveFileName(self,
                                                  u'下载文件', 
                                                  _.text(0), 
                                                  u'*.*')
        fname = (unicode(fname))
        if fname == '':
            return
        __ = str(_.text(0))
        fname = str(os.path.abspath(fname))

        t = threading.Thread(target=self.downloadRun, args=(__,
                                                            fname, ))
        t.start()

            
    def downloadRun(self, filenameIn, filenameOut):

        global mutex

        mutex.acquire()
        
        self.ftp.getDownload(filenameIn, filenameOut)

        self.ftp.retrlines('LIST')

        self.emit(QtCore.SIGNAL('needRefresh'))
        
        mutex.release()

        
    def upload(self):

        fname = QtGui.QFileDialog.getOpenFileName(self,
                                                  u'上传文件', 
                                                  '', 
                                                  u'*.*')
        fname = unicode(fname)
        if fname == '':
            return
        _fname = str(os.path.abspath(fname))
        fname = fname.split('/')[-1]

        t = threading.Thread(target=self.uploadRun, 
                             args=(fname, _fname, ))
        t.start()
        

    def uploadRun(self, filename, _filename):

        global mutex

        mutex.acquire()
        
        self.ftp.getUpload(filename, _filename)

        self.ftp.retrlines('LIST')
    
        self.emit(QtCore.SIGNAL('needRefresh'))

        mutex.release()

    
    def changeDirectory(self):

        _ = self.fileList.currentItem()

        t = threading.Thread(target=self.changeDirectoryRun, 
                             args=(str(_.text(0)), ))
        t.start()


    def changeDirectoryRun(self, directory):

        global mutex

        mutex.acquire()

        self.ftp.cwd(directory)

        self.ftp.retrlines('LIST')

        self.emit(QtCore.SIGNAL('needRefresh'))

        mutex.release()
        
        
    def errorAlert(self, s):

        QtGui.QMessageBox.critical(self, u'错误', s)


        
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
