# -*- coding:utf8 -*-

import socket, re

class FTP():

    def __init__(self, url):
        
        self.url = url
        self.loginSucc = False
        self.pasvSucc = False
        self.currentList = []

    # If you want to login anonymous, just left account empty
    def login(self, account = 'anonymous', passwd = ''):

        self.account = account
        self.passwd = passwd
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Port 21 is used to trans command
        self.sock.connect((self.url, 21))
        _ = self.sock.recv(1024)
        # Return False when connect error
        if not '220' in _:   return False, _
        self.sock.sendall('USER ' + self.account + '\r\n')
        _ = self.sock.recv(1024)
        # Return False when send account error
        if not '331' in _:   return False, _
        self.sock.sendall('PASS ' + self.passwd + '\r\n')
        _ = self.sock.recv(1024)
        # Return False when passwd error
        if not '230' in _:   return False, _
        else:
            # Init passive mode. If error, return False
            self.loginSucc = True
            return True, _

    def changeIntoPasv(self):
        
        if not self.loginSucc:  return False, 'You should login first'

        self.sock.sendall('PASV\r\n')
        _ = self.sock.recv(1024)
        if not '227' in _:     return False, _
        # Use another sock
        __ = _[27:-4].split(',')
        self.h = __[0] + '.' + __[1] + '.' + __[2] + '.' + __[3]
        self.p = int(__[4]) * 256 + int(__[5])
        self.sockPasv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockPasv.connect((self.h, self.p))
        self.pasvSucc = True
        return True, _

    def retrlines(self, command):

        if not self.loginSucc:  return False, 'You should login first'
        if not self.pasvSucc: return False, 'You should change into PASV mode'

        # List Command: List the file in current directory
        if command == 'LIST':
            self.sock.sendall('LIST\r\n')
            _ = self.sock.recv(1024)
            if not '150' in _:   return False, _
            _ = self.sockPasv.recv(8152)
            self.pasvSucc = False
            self.sockPasv.close()
            _ = _.split('\r\n')[:-1]
            self.currentList = []
            for __ in _:
                # Format List
                ___ = re.findall(r'[\w|\-|>|/|\.]+', __)
                ____ = {}
                ____['permissions'] = ___[0]
                ____['linkNum']     = ___[1] 
                ____['owner']       = ___[2]
                ____['ownerGroup']  = ___[3]
                ____['date']        = ___[7] + ' ' + \
                                      ___[6] + ' ' + \
                                      ___[5]
                ____['name']        = ___[6]
                if ___[7] == '->':  ____['isLn'] = True
                else:               ____['isLn'] = False
                if ____['isLn']:    ____['Ln'] = ___[8]
                self.currentList.append(____)
            _ = self.sock.recv(1024)
            if '226' in _:       return True, _
            

    def cwd(self, directory):

        if not self.loginSucc:  return False, 'You should login first.'

        self.sock.sendall('CWD ' + directory + '\r\n')
        _ = self.sock.recv(1024)
        # If change directory error
        if not '250' in _:       return False, _
        return True, _
        
    def getSize(self, filename):
        
        if not self.loginSucc:   return False, 'You should login first.'

        self.sock.sendall('SIZE ' + filename + '\r\n')
        _ = self.sock.recv(1024)
        # If SIZE Command error
        if _[:3] != '213':       return False, _
        return True, _[4:-2]

    def getDownload(self, filenameIn, filenameOut):

        if not self.loginSucc:  return False, 'You should login first'
        if not self.pasvSucc: return False, 'You should change into PASV mode'
        
        self.sock.sendall('RETR ' + filenameIn + '\r\n')
        _ = self.sock.recv(1024)
        # If RETR Command error
        if not '150' in _:       return False, _
        _ = self.sockPasv.recv(8152)
        _file = open(unicode(filenameOut), 'wb')
        _file.write(_)
        _file.close()
        self.pasvSucc = False
        self.sockPasv.close()
        _ = self.sock.recv(1024)
        # If not complete
        if not '226' in _:       return False, _
        return True, _
    
if __name__ == '__main__':
    ftp = FTP('ftp.sjtu.edu.cn')
    print ftp.login()
    print ftp.changeIntoPasv()
    print ftp.retrlines('LIST')
    print ftp.cwd('html')
    print ftp.changeIntoPasv()
    print ftp.retrlines('LIST')
    print ftp.getSize('index.html')
    print ftp.changeIntoPasv()
    print ftp.getDownload('index.html', '123.html')

