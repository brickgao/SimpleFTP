# -*- coding:utf8 -*-

import socket, re, time

class FTP:
    
    def __init__(self, url):
        
        self.url = url
        self.loginSucc = False
        self.currentList = []

    def outputLog(self, method, msg):
        
        s = ''
        if method == 'INFO':
            s = time.strftime('%Y/%m/%d %H:%M:%S ') + \
                '<font color=green>INFO: ' + msg + '</font>'
        elif method == 'ERROR':
            s = time.strftime('%Y/%m/%d %H:%M:%S') + \
                '<font color=red>ERROR: ' + msg + '</font>'
        print s
            

    # If you want to login anonymous, just left account empty
    def login(self, account = 'anonymous', passwd = ''):

        self.account = account
        self.passwd = passwd
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Port 21 is used to trans command
        self.sock.connect((self.url, 21))
        _ = self.sock.recv(1024)
        # Return False when connect error
        if not '220' in _:
            self.outputLog('ERROR', _)
            return False
        else:   self.outputLog('INFO', _)
        self.sock.sendall('USER ' + self.account + '\r\n')
        _ = self.sock.recv(1024)
        self.outputLog('INFO', 'USER ***\r\n')
        # Return False when send account error
        if not '331' in _:
            self.outputLog('ERROR', _)
            return False
        else:   self.outputLog('INFO', _)
        self.sock.sendall('PASS ' + self.passwd + '\r\n')
        _ = self.sock.recv(1024)
        self.outputLog('INFO', 'PASS ***\r\n')
        # Return False when passwd error
        if not '230' in _:
            self.outputLog('ERROR', _)
            return False
        else:
            # Init passive mode. If error, return False
            self.loginSucc = True
            self.outputLog('INFO', _)
            return True

    def changeIntoPasv(self):
        
        if not self.loginSucc:  return False, 'You should login first'

        self.sock.sendall('PASV\r\n')
        _ = self.sock.recv(1024)
        self.outputLog('INFO', 'PASV\r\n')
        if not '227' in _:
            self.outputLog('ERROR', _)
            return False
        else:   self.outputLog('INFO', _)
        # Use another sock
        __ = _[27:-4].split(',')
        self.h = __[0] + '.' + __[1] + '.' + __[2] + '.' + __[3]
        self.p = int(__[4]) * 256 + int(__[5])
        self.sockPasv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockPasv.connect((self.h, self.p))
        return True

    def retrlines(self, command):

        if not self.loginSucc:  return False, 'You should login first'

        self.changeIntoPasv()

        # List Command: List the file in current directory
        if command == 'LIST':
            self.sock.sendall('LIST\r\n')
            _ = self.sock.recv(1024)
            self.outputLog('INFO', 'LIST\r\n')
            if not '150' in _:
                self.outputLog('ERROR', _)
                return False
            else:   self.outputLog('INFO', _)
            _ = self.sockPasv.recv(8152)
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
            if not '226' in _:
                self.outputLog('ERROR', _)
                return False
            else:
                self.outputLog('INFO', _)
                return True
            

    def cwd(self, directory):

        if not self.loginSucc:  return False, 'You should login first.'

        self.sock.sendall('CWD ' + directory + '\r\n')
        self.outputLog('INFO', 'CWD ' + directory + '\r\n')
        _ = self.sock.recv(1024)
        # If change directory error
        if not '250' in _:       
            self.outputLog('ERROR', _)
            return False
        self.outputLog('INFO', _)
        return True
        
    def getSize(self, filename):
        
        if not self.loginSucc:
            self.outputLog('ERROR', 'You should login first.')
            return False

        self.sock.sendall('SIZE ' + filename + '\r\n')
        _ = self.sock.recv(1024)
        self.outputLog('INFO', 'SIZE ' + filename + '\r\n')
        # If SIZE Command error
        if _[:3] != '213':
            self.outputLog('ERROR', _)
            return False
        else:
            self.outputLog('INFO', _)
            return True

    def getDownload(self, filenameIn, filenameOut):

        if not self.loginSucc:
            self.outputLog('ERROR', 'You should login first.')
            return False

        self.changeIntoPasv()

        self.sock.sendall('RETR ' + filenameIn + '\r\n')
        _ = self.sock.recv(1024)
        self.outputLog('INFO', 'RETR ' + filenameIn + '\r\n')
        # If RETR Command error
        if not '150' in _:
            self.outputLog('ERROR', _)
            return False
        self.outputLog('INFO', _)
        _ = self.sockPasv.recv(8152)
        _file = open(unicode(filenameOut), 'wb')
        _file.write(_)
        _file.close()
        self.sockPasv.close()
        _ = self.sock.recv(1024)
        # If not complete
        if not '226' in _:
            self.outputLog('ERROR', _)
            return False
        else:
            self.outputLog('INFO', _)
            return True

    def getUpload(self, filename):

        if not self.loginSucc:
            self.outputLog('ERROR', 'You should login first.')
            return False

        self.changeIntoPasv()
        
        self.sock.sendall('STOR ' + filename + '\r\n')
        _ = self.sock.recv(1024)
        self.outputLog('INFO', 'STOR ' + filename + '\r\n')
        # If STOR command error
        if not '150' in _:
            self.outputLog('ERROR', _)
            return False
        else:
            self.outputLog('INFO', _)
        _file = open(unicode(filename), 'rb')
        self.sockPasv.sendall(_file.read())
        _file.close()
        self.sockPasv.close()
        _ = self.sock.recv(1024)
        # If transfer error
        if not '226' in _:
            self.outputLog('ERROR', _)
            return False
        else:
            self.outputLog('INFO', _)
            return True


    def quit(self):
        
        if not self.loginSucc:
            self.outputLog('ERROR', 'You should login first.')
            return False

        self.sock.sendall('QUIT\r\n')
        self.outputLog('INFO', 'QUIT\r\n')
        _ = self.sock.recv(1024)
        # If QUIT command error
        if not '221' in _:
            self.outputLog('ERROR', _)
            return False
        else:
            self.outputLog('INFO', _)
        self.loginSucc = False
        return True
    

if __name__ == '__main__':
    ftp = FTP('192.168.182.132')
    print ftp.login()
    print ftp.retrlines('LIST')
    print ftp.cwd('123')
    print ftp.retrlines('LIST')
    print ftp.getSize('123.txt')
    print ftp.getDownload('123.txt', '123.txt')
    print ftp.getUpload('456.txt')
    print ftp.quit()

