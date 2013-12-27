# -*- coding:utf8 -*-

import socket

class FTP():

    def __init__(self, url):
        
        self.url = url
        self.loginSucc = False

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
            self.loginSucc = True        
            self.sock.sendall('PASV\r\n')
            __ = self.sock.recv(1024)
            #Init passive mode. If error, return False
            if not '227' in __:     return False, __
            __ = __[27:-4].split(',')
            self.h = __[:4]
            self.p = __[4:]
            return True, _

    def cwd(self, floder):

        pass

    
if __name__ == '__main__':
    ftp = FTP('ftp.sjtu.edu.cn')
    _, recv = ftp.login()
    print _, recv
