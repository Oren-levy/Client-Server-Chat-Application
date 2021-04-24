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
if numPassFailAtt <= 1 or numPassFailAtt >= 5:
    print("> Server: The consecutive unsuccessful authentication attempts before a user should be blocked must be an "
          "integer between 1 and 5")
    os._exit(0)

# When the server starts up create a new and empty message.log and user.log file
# as we want a new session with each new start up of the server
fp = open("messagelog.txt", "w")
fp.close()
fp = open("userlog.txt", "w")
fp.close()

thread_lock = threading.Condition()

# Create and initialise a list of dictionaries data structure to store user info
userData = {}
userData[0] = {}
init_user_data(userData, numPassFailAtt)


# JSON object response from server to be sent to client
def send_response(client, payload, response):
    payload = json.dumps({
        "command": payload["command"],
        "response": response,
        "username": payload["username"]
    })

    client.send(payload.encode())


# The name is somewhat misleading. The server doesnt actually know that a client is going to establish a
# private connection with another user, it just sends all the info for a client to do so. Similar to issuing
# an ATU command and partitioning the response on client end, except this design is more robust.
# The naming is so the reader of the application understands whats happening.
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


# For each new client that connects to the server, we use this main function
# to send responses back to the client. The client argument in the function is a thread
# that services each respective client without interuption (multi-threading)
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

                # NOTE: BELOW EACH COMMAND WE HAVE RESPONSE = FUNCTION. EACH FUNCTION SERVICES A PARTICULAR COMMAND
                # ISSUED BY A CLIENT, AND THEN GENERATES A RESPONSE WHICH WE PASS INTO THE send_response FUNCTION
                # THAT CREATE A JSON OBJECT TO SEND BACK TO CLIENT.

                # MSG request issued from client
                elif command == "MSG":
                    create_message_log(payload)
                    response = user_confirm_message()

                # DLT request issued from client
                elif command == "DLT":
                    response = delete_message(payload)

                # EDT request issued from client
                elif command == "EDT":
                    response = edit_message(payload)

                # RDM request issued from client
                elif command == "RDM":
                    response = read_messages(payload)

                # ATU request issued from client
                elif command == "ATU":
                    response = active_users(userData, payload)

                # OUT request issued from client
                elif command == "OUT":
                    response = logout(userData, payload)

                # UDP request issued from client
                elif command == "UDP":
                    ip, port, response = get_private_connection_info(userData, payload)
                    send_response_private_conn(client, ip, port, response, payload)
                    thread_lock.notify()
                    print(response)
                    continue

                # Messages that inform the owner of the server the commands issued by clients
                print(response)
                send_response(client, payload, response)
                thread_lock.notify()

                if command == "OUT":
                    # Destroy threads pertaining to this particular client
                    client.shutdown(SHUT_RDWR)
                    client.close()
                    return

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
