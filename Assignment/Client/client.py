# coding: utf-8
# Python 3.7
import os
from socket import *
from ClientHelperFunctions import *
from user import *

import json
import atexit
import threading
import time
import sys
import signal
from typing import Dict
from socket import SHUT_RDWR

# serverName = 'localhost'
serverIP = sys.argv[1]
serverPort = int(sys.argv[2])
clientUdpPort = int(sys.argv[3])

# Create a clients TCP socket
clientSocket = socket(AF_INET, SOCK_STREAM)
# Initiate the TCP connection between the client and server.
clientSocket.connect((serverIP, serverPort))
# Get user ip_addr and port
ip, port = clientSocket.getsockname()
# Create a user class
user = User(clientSocket, ip, port, clientUdpPort)


def recv_handler():
    active = True
    while active:
        # Wait for response from server
        login_response = clientSocket.recv(1024).decode()
        # loads takes in a string and returns a json object
        login_response = json.loads(login_response)

        response = login_response["response"]
        command = login_response["command"]

        if command == "RDM":
            for message in response:
                print(message)

        else:
            print("Server Response: ", response)


def send_handler():
    active = True
    while active:
        user_input = input("> Enter one of the following commands [MSG, DLT, EDT, RDM, ATU, OUT UPD]: ")
        # Get command
        command = partition_command(user_input)

        if command == "MSG":
            # Get args following msg
            args = partition_one_arg(user_input)

            if not args.strip():
                print("An argument must follow MSG. For example: MSG Hello World! Try again")

            else:
                # Convert to json and send msg to server
                message = post_msg(args, user.get_username())
                clientSocket.send(message.encode())

        elif command == "DLT":
            # Get args following dlt
            msg_num, timestamp = partition_two_arg(user_input)

            if not msg_num or not timestamp:
                print("> Exactly two arguments must follow DLT. For example: DLT #1 08 Apr 2021 13:59:19. Try again")

            else:
                print("TRYING TO DELETE: ", msg_num, timestamp)
                delete = put_dlt(msg_num, timestamp, user.get_username())
                clientSocket.send(delete.encode())

        elif command == "EDT":
            # Get args following edt
            msg_num, timestamp, msg = partition_edt(user_input)

            if not msg_num or not timestamp or not msg:
                print("> Exactly three arguments must follow EDT in the form: messagenumber timestamp message. For example: EDT #1 08 Apr 2021 13:59:19 Hellow World. Try again")

            else:
                print("TRYING TO EDT: ", msg_num, timestamp, msg)
                edit = put_edit(msg_num, timestamp, msg, user.get_username())
                clientSocket.send(edit.encode())

        elif command == "RDM":
            # Get args following rdm
            timestamp = partition_one_arg(user_input)
            print(timestamp)
            if not timestamp:
                print("> Exactly one argument must follow RDM. For example: RDM 08 Apr 2021 13:59:19. Try again")

            else:
                read_messages = post_read_messages(timestamp, user.get_username())
                clientSocket.send(read_messages.encode())

        elif command == "OUT":
            print("OUT")

        elif command == "UPD":
            print("UPD")

        else:
            print("> You did not enter a command from the list. Try again")


        time.sleep(0.1)

def create_user_threads():
    recv_thread = threading.Thread(name="RecvHandler", target=recv_handler)
    recv_thread.daemon = True
    recv_thread.start()

    send_thread = threading.Thread(name="SendHandler", target=send_handler)
    send_thread.daemon = True
    send_thread.start()

    while True:
        time.sleep(0.1)


def login():
    while True:

        # Get user login details
        login_details = post_login(ip, user.port, clientUdpPort)
        # Send user login details to server
        clientSocket.send(login_details.encode())

        # Wait for response from server
        login_response = clientSocket.recv(1024).decode()
        login_response = json.loads(login_response)
        response = login_response["response"]

        if response == "LOGIN_SUCCESS":
            print("> Login success. Hi", login_response["username"])

            # Now that we know the user is legit, update their info
            # user.update_user_dump(login_response["username"], clientSocket, ip, port, clientUdpPort)
            user.set_username(login_response["username"])
            create_user_threads()
            break

        elif response == "USER_BLOCKED":
            print("> Too many invalid password attempts, account blocked. Please try again later")
            try:
                clientSocket.shutdown(SHUT_RDWR)
                clientSocket.close()
                sys.exit()
                break
            except Exception:
                pass

        elif response == "INVALID_PASSWORD":
            print("Invalid Password. Please try again")

        elif response == "INVALID_USERNAME":
            print("Invalid Username. Please try again")


if __name__ == "__main__":
    try:
        login()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
