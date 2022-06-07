from socket import *
from threading import Thread, Lock

class Server:
    def __init__(self, callback, port=3333):
        self.host, self.port = "192.168.200.179", port
        self.thread_stop_sign = False
        self.callback = callback
        self.client_address = None
        self.lock = Lock()

    def server_handle(self, callback):
        """
        UDP处理函数，收到UDP报文时会调callback函数
        :param callback:回调函数
        :return:
        """
        serv = socket(AF_INET, SOCK_DGRAM)
        serv.bind((self.host, self.port))
        while True:
            message, self.client_address = serv.recvfrom(10000)
            self.lock.acquire()
            callback(message)
            self.lock.release()

    def start(self):
        """
        守护线程启动
        :return:线程成功启动，返回True，反之返回false
        """
        self.thread = Thread(target=self.server_handle, args=(self.callback,))
        self.thread.setDaemon(True)
        self.thread.start()

    def stop(self):
        """
        守护线程启动
        :return:线程关闭
        """
        self.thread_stop_sign = True
        serv = socket(AF_INET, SOCK_DGRAM)
        serv.sendto(b"stop", (self.host, self.port))
