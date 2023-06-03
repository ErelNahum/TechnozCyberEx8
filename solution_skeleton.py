import socket
from struct import pack, unpack
import json
import base64
from typing import *

USER_LIST = 0
MAIL_WRITE = 1
MAIL_GET = 2

SETTINGS = "settings.dat"


def craft_user_list_packet(username: str, password: str) -> Dict[str, str]:
    """
    Crafts a user list packet (ID 0)
    Packets structure:
    {ID: USER_LIST, user: username, pass: password}
    :param username: the username of the user
    :param password: the password of the user
    :return: the crafted packet dict
    """
    return {'ID': 0, 'user': username, 'pass': password}


def craft_mail_write_packet(username: str, password: str, to: str, subject: str, message: str) -> Dict[str, str]:
    """
    Crafts a mail write packet (ID 1)
    Packets structure:
    {ID: MAIL_WRITE, user: username, pass: password, to: to, subject: subject, message: message}
    :param username: the username of the user
    :param password: the password of the user
    :param to: the destination of the mail
    :param subject: the subject of the mail
    :param message: the message of the mail
    :return: the crafted packet dict
    """
    return {'ID': 1, 'user': username, 'pass': password, 'to': to, 'subject': subject, 'message': message}


def craft_mail_get_packet(username: str, password: str) -> Dict[str, str]:
    """
    Crafts a mail get packet (ID 2)
    Packets structure:
    {ID: MAIL_GET, user: username, pass: password}
    :param username: the username of the user
    :param password: the password of the user
    :return: the crafted packet dict
    """
    return {'ID': 2, 'user': username, 'pass': password}


def get_file_content() -> bytes:
    """
    This function returns the current file contents
    :return: the string of this python file
    """
    with open(__file__, 'rb') as f:
        return f.read()


def load_settings() -> Dict[str, str]:
    """
    This function loads the settings file
    :return: the settings file for this computer
    """
    with open(SETTINGS, "r") as f:
        return json.loads(f.read().strip())


def send_payload(payload: Dict[str, str], host: str, port: 25565) -> None:
    """
    This function sends a dict payload and receives the answer from the server
    :param payload:
    :return:
    """
    payload = json.dumps(payload)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        length = len(payload)
        length = pack("<I", length)
        s.sendall(length)
        s.sendall(payload.encode())
        length = s.recv(1024)
        print(length)
        length = unpack("<I", length)[0]
        payload = s.recv(length)
        return json.loads(payload)


def main():
    settings = load_settings()
    user = settings['user']
    password = settings['password']
    host = settings['server']
    port = settings['port']

    print(send_payload(craft_user_list_packet(user, password), host, int(port)))



if __name__ == "__main__":
    main()
