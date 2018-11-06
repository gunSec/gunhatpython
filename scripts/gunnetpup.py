#!usr/bin/python2.7
import sys
import socket
import getopt
import threading
import subprocess

#global vars
listen = False
command = False
upload = False
execute = ""
target = ""
uploadDestination = ""
port = 0

#main function
def usage():
    print "GunNet Pup"
    print
    print "Usage: gunnetpup.py -t <target ip> -p <port>"
    print "-l --listen - listen on [host]:[port] for incoming connections"
    print "-e --execute=file_to_run - execute the given file upon receiving a connection"
    print "-c --command - initialize a command shell"
    print "-u --upload=destination - upon receiving connection upload a file and write to [destination]"
    print
    print
    print "Examples: "
    print "gunnetpup.py -t 192.168.0.1 -p 5555 -l -c"
    print "gunnetpup.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "gunnetpup.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./gunnetpup.py -t 192.168.11.12 -p 135"
    sys.exit(0)

def clientSender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to target host
        client.connect((target,port))
        if len(buffer):
            client.send(buffer)
        while True:
            #wait for data back
            recvLen = 1
            response = ""

            while recvLen:
                data = client.recv(4096)
                recvLen = len(data)
                response += data

                if recvLen < 4096:
                    break

            #wait for more data
            print response,
            buffer = raw_input("")
            buffer += "\n"

            #send it
            client.send(buffer)
    except:
        print "\n[*] Exception! Exiting."
        #close connection
        client.close()

def serverLoop():
    global target
    #if no target set, listen on all
    if not len(target):
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target,port))
    server.listen(5)

    while True:
        clientSocket, addr = server.accept()
        #spin thread to handle client
        clientThread = threading.Thread(target=clientHandler, args=(clientSocket,))
        clientThread.start()

def runCommand(command):
    #trim newline
    command = command.rstrip()
    #run command, try to get response
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"
    return output

def clientHandler(clientSocket):
    global upload
    global execute
    global command

    if len(uploadDestination):
        #read it all in
        fileBuffer = ""

        while True:
            data = clientSocket.recv(1024)

            if not data:
                break
        else:
            fileBuffer += data

            try:
                fileDescriptor = open(uploadDestination,"wb")
                fileDescriptor.write(fileBuffer)
                fileDescriptor.close()

                #acknowledge we wrote
                clientSocket.send("Successfully saved file to %s\r\n" % uploadDestination)
            except:
                clientSocket.send("Failed to save file to %s\r\n" % uploadDestination)

    #check for command execution
    if len(execute):
        output = runCommand(execute)
        clientSocket.send(output)

    if command:
        while True:
            clientSocket.send("<GNP:#> ")
            cmdBuffer = ""
            while "\n" not in cmdBuffer:
                cmdBuffer += clientSocket.recv(1024)
            response = runCommand(cmdBuffer)
            clientSocket.send(response)

#real main
def main():
    global listen
    global port
    global execute
    global command
    global uploadDestination
    global target

    if not len(sys.argv[1:]):
        usage()
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu", ["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l","--listen"):
            listen = True
        elif o in ("-e","--execute"):
            execute = a
        elif o in ("-c","--commandshell"):
            command = True
        elif o in ("-u","--upload"):
            uploadDestination = a
        elif o in ("-t","target"):
            target = a
        elif o in ("-p","--port"):
            port = int(a)
        else:
            assert False,"Unhandled Option"

    if not listen and len(target) and port > 0:
        # read in the buffer from the commandline
        # this will block, so send CTRL-D if not sending input
        # to stdin
        buffer = sys.stdin.read()
        # send data
        clientSender(buffer)

    if listen:
        serverLoop()

main()
