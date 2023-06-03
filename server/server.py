import enum
import socket
from logging import Logger
from threading import Lock, Thread
from struct import pack, unpack
import json
from bcrypt import checkpw

# Consts
USERS_FILE = "users.txt"
# User file structure: 
# USERNAME:HASH:CONTACTS

SELF_IP = "0.0.0.0"
PORT = 25565

# Packet Types
USER_LIST = 0
MAIL_WRITE = 1
MAIL_GET = 2
# Globals
mailLock = Lock()
mails = {}
hashes = {}
contacts = {}
server = None
logger = Logger("hero")

class Connection (Thread):
    def __init__(self, client_socket):
        Thread.__init__(self)
        self.socket = client_socket

    def run(self):
        try:
            length = self.socket.recv(4)
            length = unpack("<I", length)[0]
            data = b""  
            while length > 0:
                new_data = self.socket.recv(length)
                length -= len(new_data)
                data += new_data
            data = json.loads(data)
            if "user" not in data or "pass" not in data or "ID" not in data or data['user'] not in mails:
                data = "{ID:-1}"
            elif not checkpw(data['pass'].encode(), hashes[data['user']]): # This is the shitteist verification code I have written
                data = "{\"ID\" : -1}"
            elif data["ID"] == USER_LIST:
                # Handle User List packet
                data = self.user_list(data)
            elif data["ID"] == MAIL_WRITE:
                data = self.mail_write(data)
            elif data["ID"] == MAIL_GET:
                data = self.mail_get(data)
            if type(data) != str:
                raise Exception("Unhandled packet: " + str(data))
            length = len(data)
            length = pack("<I", length)
            self.socket.sendall(length)
            self.socket.sendall(data.encode())
        except Exception as e:
            logger.warning("Invalid connection !")
            logger.warning(str(e))
            raise e
    
    def user_list(self, data):
        new_data = {'ID': USER_LIST, 'users': contacts[data['user']]}
        return json.dumps(new_data)
    
    def mail_write(self, data):
        success = False
        if "user" in data and "to" in data and "subject" in data and "message" in data:
            pyld = data['message']
            sub = data['subject']
            frm = data['user']
            to = data['to']
            if to in contacts[data['user']]:
                message = {"from": frm, "subject": sub, "data": pyld}
                mailLock.acquire()
                global mails
                if to in mails:
                    mails[to].append(message)
                    success = True
                mailLock.release()
        new_data = {'ID': MAIL_WRITE, 'status': success}
        return json.dumps(new_data)
    
    def mail_get(self, data):
        new_data = {'ID': MAIL_GET, 'mail_count': 0, 'mails': []}
        if "user" in data:
            user = data["user"]
            mailLock.acquire()
            global mails
            if user in mails:
                new_data['mails'] = mails[user]
                mails[user] = []
            mailLock.release()
            new_data['mail_count'] = len(new_data['mails'])
        return json.dumps(new_data)


def setup():
    with open(USERS_FILE, "r") as f:
        myline = f.readline()
        while myline:
            myline = myline.strip()
            username, hawsh, contact = myline.split(':')
            if myline != "":
                mails[username] = []
                hashes[username] = hawsh.encode()
                contacts[username] = contact.split(',')
            myline = f.readline()
    global server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SELF_IP, PORT))

def listen():
    global server
    server.listen()
    print("Server Online ;)")
    while True:
        (client_socket, addr) = server.accept()
        print("Hello Client", addr)
        logger.info("Client connected:", addr)
        client = Connection(client_socket)
        client.run()

def main():
    setup()
    logger.info(mails)
    listen()

if __name__ == "__main__":
    main()