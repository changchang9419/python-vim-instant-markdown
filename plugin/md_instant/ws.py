# -*- coding: utf-8 -*-

import socket
import base64
import hashlib
import struct
from select import select

class WebSocket():

    @staticmethod
    def handshake(conn):
        key = None 
        data = conn.recv(8192)
        if not len(data):
            return False
        for line in data.split(b'\r\n\r\n')[0].split(b'\r\n')[1:]:
            k, v = line.split(b': ')
            if k == b'Sec-WebSocket-Key':
                v += b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
                key = base64.b64encode(hashlib.sha1(v).digest())
        if not key:
            conn.close()
            return False
        response = b'HTTP/1.1 101 Switching Protocols\r\n'\
                   b'Upgrade: websocket\r\n'\
                   b'Connection: Upgrade\r\n'\
                   b'Sec-WebSocket-Accept:' + key + b'\r\n\r\n'
        conn.send(response)
        return True

    @staticmethod
    def recv(conn, size=8192):
        data = conn.recv(size)
        if not len(data):
            return False
        length = data[1] & 127
        if length == 126:
            mask = data[4:8]
            raw = data[8:]
        elif length == 127:
            mask = data[10:14]
            raw = data[14:]
        else:
            mask = data[2:6]
            raw = data[6:]
        ret = b''
        for cnt, d in enumerate(raw):
            ret += bytes(chr(d ^ mask[cnt%4]), 'utf-8')
        return ret
                      
    @staticmethod
    def send(conn, data):
        head = b'\x81'
        if len(data) < 126:
            head += struct.pack('B', len(data))
        elif len(data) <= 0xFFFF:
            head += struct.pack('!BH', 126, len(data))
        else:
            head += struct.pack('!BQ', 127, len(data))
        conn.send(head+data)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_list = set()

def sendall(data):
    data = bytes(data, 'utf-8')
    for sock in socket_list:
        if sock != server:
            WebSocket.send(sock, data)

def process(conn, data): #you should change this method
    WebSocket.send(conn, data)

def main(handle=process):
    port = 7001
    try:
        server.bind(('', port))
        server.listen(100)
    except Exception as e:
        print(e)
        exit()
    socket_list.add(server)
    print('server start on port %d' % port)
    while True:
        r, w, e = select(socket_list, [], [])
        for sock in r:
            if sock == server:
                conn, addr = sock.accept()
                if WebSocket.handshake(conn):
                    socket_list.add(conn)
            else:
                data = WebSocket.recv(sock)
                if not data:
                    socket_list.remove(sock)
                else:
                    handle(sock, data)

if __name__ == '__main__':
    main()
