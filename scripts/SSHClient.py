import threading
import paramiko
import subprocess

def sshCommand(ip, user, passwd, command):
    print "[*] SSH to %s" % ip
    print "[*] User: %s:%s" %(user,passwd)
    print "[*] Running: %s" % command
    print "[*] Received:"
    print "---------------------------------"
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        print ssh_session.recv(1024)
    return

sshCommand('104.236.153.107', 'root', 'guNst@r55r00tchingchong', 'cat /etc/passwd')
