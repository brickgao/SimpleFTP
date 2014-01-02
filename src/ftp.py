# -*- coding:utf8 -*-

import socket, re, time, logging

class FTP:
    
    def __init__(self, url):
        
        self.url = url
        self.loginSucc = False
        self.currentList = []
        self.logger = logging.Logger(__name__)


    # If you want to login anonymous, just left account empty
    def login(self, account = 'anonymous', passwd = ''):

        self.account = str(account)
        self.passwd = str(passwd)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Port 21 is used to trans command
        self.sock.connect((self.url, 21))
        _ = self.sock.recv(1024)
        # Return False when connect error
        if not '220' in _:
            self.logger.error(_[:-2])
            return False
        else:   self.logger.info(_[:-2])
        self.serverWelcome = _[:-2]
        self.sock.sendall('USER ' + self.account + '\r\n')
        self.logger.info('USER ' + self.account)
        _ = self.sock.recv(1024)
        # Return False when send account error
        if not '331' in _:
            self.logger.error(_[:-2])
            return False
        else:   self.logger.info( _[:-2])
        self.sock.sendall('PASS ' + self.passwd + '\r\n')
        _ = self.sock.recv(1024)
        self.logger.info('PASS ***')
        # Return False when passwd error
        if not '230' in _:
            self.logger.error(_[:-2])
            return False
        else:
            # Init passive mode. If error, return False
            self.loginSucc = True
            self.logger.info(_[:-2])
            return True


    def changeIntoPasv(self):
        
        if not self.loginSucc:  return False, 'You should login first'

        self.sock.sendall('PASV\r\n')
        _ = self.sock.recv(1024)
        self.logger.info('PASV')
        if not '227' in _:
            self.logger.error(_[:-2])
            return False
        else:   self.logger.info(_[:-2])
        # Use another sock
        __ = _[27:-4].split(',')
        self.h = __[0] + '.' + __[1] + '.' + __[2] + '.' + __[3]
        self.p = int(__[4]) * 256 + int(__[5])
        self.sockPasv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockPasv.connect((self.h, self.p))
        return True


    def retrlines(self, command):

        if not self.loginSucc:
            self.logger.error('You should login first.')
            return False

        self.changeIntoPasv()

        # List Command: List the file in current directory
        if command == 'LIST':
            self.sock.sendall('LIST\r\n')
            _ = self.sock.recv(1024)
            self.logger.info('LIST')
            if not '150' in _:
                self.logger.error(_[:-2])
                return False
            else:   self.logger.info(_[:-2])
            _ = self.sockPasv.recv(8152)
            self.sockPasv.close()
            _ = _.split('\r\n')[:-1]
            self.currentList = []
            if 'vsFTPd' in self.serverWelcome:
                for __ in _:
                    # Format List
                    ___ = re.findall(r'[\w|\-|>|/|\.|\:]+', __)
                    ____ = {}
                    ____['permissions'] = ___[0]
                    ____['linkNum']     = ___[1] 
                    ____['owner']       = ___[2]
                    ____['ownerGroup']  = ___[3]
                    ____['size']        = ___[4]
                    if ':' in ___[7]:
                        ____['date']        = ___[5] + ' ' + \
                                              ___[6] + ' ' + \
                                              ___[7]
                    else:
                        ____['date']        = ___[7] + ' ' + \
                                              ___[5] + ' ' + \
                                              ___[6]
                    ____['name']        = ___[8]
                    if '->' in __:      ____['isLn'] = True
                    else:               ____['isLn'] = False
                    if ____['isLn']:    ____['Ln'] = ___[10]
                    self.currentList.append(____)
            else:
                for __ in _:
                    # Format List
                    ___ = re.findall(r'[\w|\-|>|/|\.|\:]+', __)
                    ____ = {}
                    ____['permissions'] = ___[0]
                    ____['linkNum']     = ___[1]
                    ____['owner']       = ___[2]
                    ____['ownerGroup']  = ___[3]
                    ____['size']        = ___[4]
                    ____['date']        = ___[5] + ' ' + \
                                          ___[6] + ' ' + \
                                          ___[7]                        
                    ____['name']        = ___[8]
                    ____['isLn']        = False
                    self.currentList.append(____)
            _ = self.sock.recv(1024)
            if not '226' in _:
                self.logger.error(_[:-2])
                return False
            else:
                self.logger.info(_[:-2])
                return True
            

    def cwd(self, directory):

        if not self.loginSucc:
            self.logger.error('You should login first.')
            return False

        self.sock.sendall('CWD ' + directory + '\r\n')
        self.logger.info('CWD ' + directory)
        _ = self.sock.recv(1024)
        # If change directory error
        if not '250' in _:       
            self.logger.error(_[:-2])
            return False
        self.logger.info(_[:-2])
        return True

        
    def getSize(self, filename):
        
        if not self.loginSucc:
            self.logger.error('You should login first.')
            return False

        self.sock.sendall('SIZE ' + filename + '\r\n')
        _ = self.sock.recv(1024)
        self.logger.info('SIZE ' + filename)
        # If SIZE Command error
        if _[:3] != '213':
            self.logger.error(_[:-2])
            return False, _
        else:
            self.logger.info(_[:-2])
            return True, int(_[4:-2])

            
    def getDownload(self, filenameIn, filenameOut):

        if not self.loginSucc:
            self.logger.info('You should login first.')
            return False

        _, fsize = self.getSize(filenameIn)

        if not _:   return False

        self.changeIntoPasv()

        self.sock.sendall('RETR ' + filenameIn + '\r\n')
        self.logger.info('RETR ' + filenameIn)
        _ = self.sock.recv(1024)
        # If RETR Command error
        if not '150' in _:
            self.logger.error(_[:-2])
            return False
        self.logger.info(_[:-2])
        _file = open(unicode(filenameOut), 'wb')
        while fsize > 0:
            _ = self.sockPasv.recv(1024)
            fsize -= len(_)
            _file.write(_)
        _file.close()
        self.sockPasv.close()
        _ = self.sock.recv(1024)
        # If not complete
        if not '226' in _:
            self.logger.error(_[:-2])
            return False
        else:
            self.logger.info(_[:-2])
            return True


    def getUpload(self, filename, filenameAbsPath):

        if not self.loginSucc:
            self.logger.error('You should login first.')
            return False

        self.changeIntoPasv()
        
        self.sock.sendall('STOR ' + filename + '\r\n')
        _ = self.sock.recv(1024)
        self.logger.info('STOR ' + filename)
        # If STOR command error
        if not '150' in _:
            self.logger.error(_[:-2])
            return False
        else:
            self.logger.info(_[:-2])
        _file = open(unicode(filenameAbsPath), 'rb')
        self.sockPasv.sendall(_file.read())
        _file.close()
        self.sockPasv.close()
        _ = self.sock.recv(1024)
        # If transfer error
        if not '226' in _:
            self.logger.error(_[:-2])
            return False
        else:
            self.logger.info(_[:-2])
            return True


    def quit(self):
        
        if not self.loginSucc:
            self.logger.error('You should login first.')
            return False

        self.sock.sendall('QUIT\r\n')
        self.logger.info('QUIT')
        _ = self.sock.recv(1024)
        # If QUIT command error
        if not '221' in _:
            self.logger.error(_[:-2])
            return False
        else:
            self.logger.info(_[:-2])
        self.loginSucc = False
        return True
