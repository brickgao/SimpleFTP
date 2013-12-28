# -*- coding:utf8 -*-

import socket, re

class FTP():

    def __init__(self, url):
        
        self.url = url
        self.loginSucc = False
        self.currentList = []

    #If you want to login anonymous, just left account empty
    def login(self, account = 'anonymous', passwd = ''):

        self.account = account
        self.passwd = passwd
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Port 21 is used to trans command
        self.sock.connect((self.url, 21))
        _ = self.sock.recv(1024)
        #Return False when connect error
        if not '220' in _:   return False, _
        self.sock.sendall('USER ' + self.account + '\r\n')
        _ = self.sock.recv(1024)
        #Return False when send account error
        if not '331' in _:   return False, _
        self.sock.sendall('PASS ' + self.passwd + '\r\n')
        _ = self.sock.recv(1024)
        #Return False when passwd error
        if not '230' in _:   return False, _
        else:
            #Init passive mode. If error, return False
            self.sock.sendall('PASV\r\n')
            __ = self.sock.recv(1024)
            if not '227' in __:     return False, __
            __ = __[27:-4].split(',')
            self.h = __[0] + '.' + __[1] + '.' + __[2] + '.' + __[3]
            self.p = int(__[4]) * 256 + int(__[5])
            self.sockPasv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sockPasv.connect((self.h, self.p))
            self.loginSucc = True
            return True, _

    def retrlines(self, command):

        #List Command: List the file in current directory
        if command == 'LIST':
            self.sock.sendall('LIST\r\n')
            _ = self.sock.recv(1024)
            if not '150' in _:   return False, _
            _ = self.sockPasv.recv(8152)
            _ = _.split('\r\n')[:-1]
            self.currentList = []
            for __ in _:
                #Format List
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
            if '226' in _:       return True, _
            

    def cwd(self, floder):

        pass

    
if __name__ == '__main__':
    ftp = FTP('ftp.sjtu.edu.cn')
    _, recv = ftp.login()
    ftp.retrlines('LIST')
