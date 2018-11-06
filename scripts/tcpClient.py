#!usr/bin/python2.7
import socket

target_host = "104.236.153.107"
target_port = 5569

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((target_host, target_port))
request = "Test2"
print "[*] Sending: %s" % request
client.send(request)

response = client.recv(4096)

print "[*] Received: %s" % response
