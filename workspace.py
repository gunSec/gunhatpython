#!usr/bin/python2.7
import sys
import socket
import threading

def serverLoop(localHost,localPort,remoteHost,remotePort,receiveFirst):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((localHost,localPort))
    except:
        print "[!] Failed to listen on %s:%d" % (localHost,localPort)
        print "[!] Check for other listening sockets or correct permissions."
        sys.exit(0)

    print "[*] Listening on %s:%d" % (localHost,localPort)

    server.listen(5)

    while True:
        clientSocket, addr = server.accept()
        print "[->] Received incoming connection from %s:%d" %(addr[0],addr[1])
        proxyThread = threading.Thread(target=proxyHandler,args=(clientSocket,remoteHost,remotePort,receiveFirst))
        proxyThread.start()

def proxyHandler():
    #connect to remote host
    remoteSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remoteSocket.connect((remoteHost,remotePort))

    if receiveFirst:
        remoteBuffer = receiveFrom(remoteSocket)
        hexdump(remoteBuffer)

        remoteBuffer = responseHandler(remoteBuffer)

        if len(remoteBuffer):
            print "[<-] Sending %d bytes to localhost" % len(remoteBuffer)
            clientSocket.send(remoteBuffer)

    while True:
        localBuffer = receiveFrom(clientSocket)
        if len(localBuffer):
            print "[->] Received %d bytes from localhost." % len(localBuffer)
            hexdump(localBuffer)

            localBuffer = requestHandler(localBuffer)
            remoteSocket.send(localBuffer)
            print "[->] Sent to remote."

        remoteBuffer = receiveFrom(remoteSocket)
        if len(remoteBuffer):
            print "[<-] Received %d bytes from remote." % len(remoteBuffer)
            hexdump(remoteBuffer)
            remoteBuffer = responseHandler(remoteBuffer)
            clientSocket.send(remoteBuffer)
            print "[<-] Sent to localhost."

        if not len(localBuffer) or not len(remoteBuffer):
            clientSocket.close()
            remoteSocket.close()
            print "[*] No more data, cleaning up."

            break

def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append( b"%04X %-*s %s" % (i, length*(digits + 1), hexa,

        text) )
    print b'\n'.join(result)

def receiveFrom(connection):
    buffer = ""
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer

def requestHandler(buffer):
    #put packet modifications here
    return buffer

def responseHandler(buffer):
    #put packet modifications here
    return buffer


def main():
    if len(sys.argv[1:]) != 5:
        print "Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [receivefirst]"
        print "Example: /proxy.py 127.0.0.1 5569 10.10.10.10 5569 True"
        sys.exit(0)

    #local listening parameters
    localHost = sys.argv[1]
    localPort = int(sys.argv[2])

    #remote target
    remoteHost = sys.argv[3]
    remotePort = sys.argv[4]

    #tells proxy to connect and receive data
    receiveFirst = sys.argv[5]
    if "True" in receiveFirst:
        receiveFirst = True
    else:
        receiveFirst = False

    #listening socket
    serverLoop(localHost,localPort,remoteHost,remotePort,receiveFirst)

main()
