# coding: utf-8
# Python 3.7
# Sourced and edited from uni assignment sample code on UDP multi-threading
import os

from ServerHelperFunctions import *
from UserInfo import *
from user import *

from socket import *
import sys
import threading
import time
import json

# Get command line arguments for server
serverPort = int(sys.argv[1])
numPassFailAtt = int(sys.argv[2])

if 1 <= numPassFailAtt <= 6:
    try:
        print("Success")
    except ValueError:
        print("“Invalid number of allowed failed consecutive attempt: number. The valid value of argument number is "
              "an integer between 1 and 5")

fp = open("messagelog.txt", "w")
fp.close()
fp = open("userlog.txt", "w")
fp.close()

thread_lock = threading.Condition()

# Create and initialise a list of dictionaries data structure to store user info
userData = {}
userData[0] = {}
init_user_data(userData, numPassFailAtt)


def send_response(client, payload, response):
    payload = json.dumps({
        "command": payload["command"],
        "response": response,
        "username": payload["username"]
    })

    client.send(payload.encode())


def send_response_private_conn(client, ip, port, response, payload):
    payload = json.dumps({
        "command": payload["command"],
        "response": response,
        "presenter": payload["presenter"],
        "audience": payload["audience"],
        "ip": ip,
        "udp_port": port,
        "file_name": payload["file_name"]
    })

    client.send(payload.encode())


def service_client_main(client, client_address, user):
    def service_client():
        active = True
        while active:
            payload = client.recv(1024).decode()

            # This will function as the client response status, similar to an API's 400/403 etc
            response = "error no such command in server."

            if not payload:
                exit(0)

            with thread_lock:
                # Json.loads takes in a string and returns a json obj
                payload = json.loads(payload)
                # user.update_user_info_dump(payload)

                command = payload["command"]
                if command == "login":
                    response = authenticate_user_login(payload, userData)
                    # response = authenticate_user_login(user, userData)

                    if response == "LOGIN_SUCCESS":
                        print("USER AUTHENTICATED")
                        update_user_data_dump(payload, userData)
                        create_user_log(payload, userData)
                        update_user_data_specific(userData, payload["username"], 'loginTime', get_time_stamp())

                elif command == "MSG":
                    create_message_log(payload)
                    response = user_confirm_message()

                elif command == "DLT":
                    response = delete_message(payload)

                elif command == "EDT":
                    response = edit_message(payload)

                elif command == "RDM":
                    response = read_messages(payload)

                elif command == "ATU":
                    response = active_users(userData, payload)

                elif command == "OUT":
                    response = logout(userData, payload)

                elif command == "UDP":
                    ip, port, response = get_private_connection_info(userData, payload)
                    send_response_private_conn(client, ip, port, response, payload)
                    thread_lock.notify()
                    print(response)
                    continue

                print(response)
                send_response(client, payload, response)
                thread_lock.notify()

    return service_client


def recv_tcp_conn_handler():
    global thread_lock
    global clients
    global clientSocket
    global serverSocket
    print('Server is now listening...')
    while True:
        # With each new client connection we create a new socket dedicated to that client
        conn_socket, client_address = serverSocket.accept()

        user = User(numPassFailAtt)

        # Create a service_client_main object for each new client
        service_client_socket = service_client_main(conn_socket, client_address, user)

        # Create a new thread for each new client
        new_client_thread = threading.Thread(name=str(client_address), target=service_client_socket)
        new_client_thread.daemon = False
        new_client_thread.start()
        print(new_client_thread)

        # threadList.append(new_client_thread)
        # print(len(threadList))


# Create a TCP client/server socket, one for receiving and one for sending data.
# Bind serverSocket to localhost with a user inputted port, and wait for connections
# clientSocket = socket(AF_INET, SOCK_STREAM)
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(5)

# We create only one recv thread - happens when we start up the server
recv_thread = threading.Thread(name="recvTcpConnHandler", target=recv_tcp_conn_handler)
recv_thread.daemon = True
recv_thread.start()

# send_thread = threading.Thread(name="SendHandler", target=send_tcp_conn_handler)
# send_thread.daemon = True
# send_thread.start()

# this is the main thread
while True:
    try:
        time.sleep(0.1)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            os.remove("userlog.txt")
            os.remove("messagelog.txt")
            serverSocket.close()
            sys.exit(0)
        except SystemExit:
            os._exit(0)
