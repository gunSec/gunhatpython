#!usr/bin/python2.7
import socket
import threading

bindIP = "0.0.0.0"
bindPort = 5569

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bindIP,bindPort))

server.listen(5)
print "[*] Listening on %s:%d" % (bindIP,bindPort)

def handleClient(clientSocket):
    request = clientSocket.recv(1024)
    print "[*] Received: %s" % request
    clientSocket.send("Fuck you")
    clientSocket.close()

while True:
    client,addr = server.accept()
    print "[*] Accepted Connection from %s:%d" % (addr[0],addr[1])
    clientHandler = threading.Thread(target=handleClient,args=(client,))
    clientHandler.start()
