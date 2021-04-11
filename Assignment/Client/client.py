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

# Create a client TCP socket and initiate the TCP connection between the client and server.
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverIP, serverPort))

# Create a client UDP socket for peer-to-peer
# Use two sockets, one for sending and one for receiving
clientSocketUdp = socket(AF_INET, SOCK_DGRAM)
serverSocketUdp = socket(AF_INET, SOCK_DGRAM)
serverSocketUdp.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocketUdp.bind(('localhost', clientUdpPort))

# Get user ip_addr and port
ip, port = clientSocket.getsockname()
# Create a user class
user = User(clientSocket, ip, port, clientUdpPort)
print(port)
print(clientUdpPort)

thread_lock = threading.Condition()


def private_recv_handler():
    print("> Private server listening ...")
    active = True
    while active:
        # Wait for response from server
        peer_to_peer_file, client_address = serverSocketUdp.recvfrom(2048)
        peer_to_peer_file = peer_to_peer_file.decode()
        peer_to_peer_file = json.loads(peer_to_peer_file)
        print("\n> " + peer_to_peer_file["presenter"] + " has established a private connection with you. Receiving "
                                                        "file...")

        with thread_lock:
            file_name = peer_to_peer_file["presenter"] + "_" + peer_to_peer_file["file_name"]
            print("Presenter: ", peer_to_peer_file["presenter"])
            print("Audience: ", peer_to_peer_file["audience"])
            print(peer_to_peer_file["file_name"])
            print(file_name)
            thread_lock.notify()


def private_send_handler(response):
    sending = True
    while sending:
        with thread_lock:
            if response["response"] == "offline":
                print("> " + response["audience"] + " is offline. Cant establish private connection")

            elif response["response"] == "yourself":
                print("> You can't establish a private connection with yourself")

            else:
                print("> Establishing private connection with " + response["audience"])
                audience_ip = response["ip"]
                audience_port = response["udp_port"]
                file = response["file_name"]
                print(audience_ip)
                print(audience_port)
                print(file)
                private_message = get_private_connection(user.get_username(), response["audience"], file)
                clientSocketUdp.sendto(private_message.encode(), (audience_ip, audience_port))

            thread_lock.notify()
            sending = False


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
            if len(response) == 0:
                print("> Server Response: No new messages to read")
            else:
                print("> See new messages below")
                for message in response:
                    print("> Server Response: ", message.strip())

        elif command == "ATU":
            if len(response) == 0:
                print("> Server Response: No other active users")
            else:
                for active_users in response:
                    print("> Server Response: ", active_users)

        elif command == "OUT":
            print("> Server Response: ", response)
            clientSocket.close()

        elif command == "UDP":
            private_send_handler(login_response)


        else:
            print("> Server Response: ", response)


def send_handler():
    active = True
    while active:
        user_input = input("> Enter one of the following commands [MSG, DLT, EDT, RDM, ATU, OUT UDP]: ")
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
                print(
                    "> Exactly three arguments must follow EDT in the form: messagenumber timestamp message. For example: EDT #1 08 Apr 2021 13:59:19 Hellow World. Try again")

            else:
                edit = put_edit(msg_num, timestamp, msg, user.get_username())
                clientSocket.send(edit.encode())

        elif command == "RDM":
            # Get args following rdm
            timestamp = partition_one_arg(user_input)
            if not timestamp:
                print("> Exactly one argument must follow RDM. For example: RDM 08 Apr 2021 13:59:19. Try again")

            else:
                read_messages = post_read_messages(timestamp, user.get_username())
                clientSocket.send(read_messages.encode())

        elif command == "ATU":
            active_users = get_active_users(user.get_username())
            clientSocket.send(active_users.encode())

        elif command == "OUT":
            logout = post_logout(user.get_username())
            clientSocket.send(logout.encode())

        elif command == "UDP":
            # Get args following dlt
            audience, file_name = partition_two_arg(user_input)
            if not audience or not file_name:
                print("> Exactly two arguments must follow UDP. For example: UPD Obi-wan lecture1.mp4. Try again")

            else:
                peer_to_peer = get_private_connection(user.get_username(), audience, file_name)
                clientSocket.send(peer_to_peer.encode())

        else:
            print("> You did not enter a command from the list. Try again")

        # Wait for server response before prompting user again
        time.sleep(0.1)


def create_user_threads():
    private_recv_thread = threading.Thread(name="PrivateRecvHandler", target=private_recv_handler)
    private_recv_thread.daemon = True
    private_recv_thread.start()

    recv_thread = threading.Thread(name="RecvHandler", target=recv_handler)
    recv_thread.daemon = True
    recv_thread.start()

    send_thread = threading.Thread(name="SendHandler", target=send_handler)
    send_thread.daemon = True
    send_thread.start()

    while True:
        time.sleep(0.1)


#
# def create_private_user_threads():
#     print('Private client server is now listening...')
#     while True:
#         print("ACCEPTED PRIV CONN")
#         # With each new private connection we create a new socket dedicated to that client
#         connection_socket, client_address = serverSocketUdp.accept()
#
#         # create a new thread for the client socket
#         recv_thread_udp = threading.Thread(name=str(client_address),
#                                            target=private_recv_handler(connection_socket, client_address))
#         recv_thread_udp.daemon = False
#         recv_thread_udp.start()


def login():
    while True:

        # Get user login details
        login_details = post_login(user.get_ip_addr(), user.get_port(), user.get_prv_port())
        # Send user login details to server
        clientSocket.send(login_details.encode())

        # Wait for response from server
        login_response = clientSocket.recv(1024).decode()
        login_response = json.loads(login_response)
        response = login_response["response"]

        if response == "LOGIN_SUCCESS":
            print("> Login success. Hi", login_response["username"])

            # Now that we know the user is legit, update their info
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
