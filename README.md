SimpleFTP
=========

SimpleFTP 是一个由 Python 编写的简易 GUI 客户端。

**Tips**: SimpleFTP 是从 socket 层面完成的 FTP 协议，目的在于学习 FTP 协议，如果你需要用于生产环境，建议使用`ftplib`或者其他模块。

依赖
----

你可以在 [Python.org](python.org) 上获取 Python

在 [Riverbank](http://www.riverbankcomputing.co.uk/software/pyqt/intro) 上获取 PyQt

结构
----

`ftp.py`是 ftp 模块部分，函数基本与`ftplib`保持一致，使用`logging`模块输出调试/通知信息。 

`ui.py`是 gui 模块部分，将`logging`中的`logger`定向输出至`QTextBrowser`，为了保证线程安全，更新由信号触发。

使用
----

通过`python main.py`启动，适用的 ftp 服务器有 vsftpd 还有一些 win 环境下的小型 ftp 服务器。

日志
----

2014/1/1 修复线程安全问题

2014/1/2 修复大文件传输的问题

协议
----

[GPL](http://www.gnu.org/licenses/gpl.html)

