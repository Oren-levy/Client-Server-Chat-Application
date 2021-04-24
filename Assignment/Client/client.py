# coding: utf-8
# Python 3.7
import os
from socket import *
from ClientHelperFunctions import *
from user import *

import json
import threading
import time
import sys
from socket import SHUT_RDWR

# get ip from user first arg
serverIP = sys.argv[1]
# get server from user second arg
serverPort = int(sys.argv[2])
# get private port from user third arg
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
udp_buffer = 4096

# Get user ip_addr and port
ip, port = clientSocket.getsockname()
# Create a user class
user = User(clientSocket, ip, port, clientUdpPort)
print(port)
print(clientUdpPort)

thread_lock = threading.Condition()


# This function is responsible for servicing a private connection with another client.
def private_recv_handler():
    print("> Private server listening ...")

    active = True
    while active:
        # Wait for peer-to-peer connection to be established
        data, addr = serverSocketUdp.recvfrom(udp_buffer)
        data = data.decode()
        data = json.loads(data)

        with thread_lock:
            # Get the name of presenter and prepend to file name being shared
            file_name = data["presenter"] + "_" + data["file_name"]

            # Inform client that a private connection has been established
            print("\n> " + data["presenter"] + " has established a private connection with you. Receiving " + file_name)

            # We dont assume the file type and so we write in bytes
            fp = open(file_name, 'wb')
            file_data, addr = serverSocketUdp.recvfrom(udp_buffer)

            try:
                # So long as there are more bytes to read, keep writing to file
                while file_data:
                    fp.write(file_data)
                    serverSocketUdp.settimeout(6)
                    file_data, addr = serverSocketUdp.recvfrom(udp_buffer)
            # File done downloading
            except timeout:
                fp.close()
                serverSocketUdp.settimeout(None)
                thread_lock.notify()

                print("> File downloaded")
                print("> Enter one of the following commands [MSG, DLT, EDT, RDM, ATU, OUT UDP]: ")


# This function is called when a user submits the UDP command, and is responsible for establishing a private connection
# with another client
def private_send_handler(response):
    sending = True
    while sending:
        with thread_lock:
            # User is offline
            if response["response"] == "offline":
                print("> " + response["audience"] + " is offline. Cant establish private connection")
            # Sending to yourself is not allowed
            elif response["response"] == "yourself":
                print("> You can't establish a private connection with yourself")
            # No file exists
            elif response["response"] == "keyError":
                print("> Invalid name given")
            # Success, establish connection. Get IP and Port from server response
            else:
                print("> Establishing private connection with " + response["audience"])
                audience_ip = response["ip"]
                audience_port = response["udp_port"]
                file = response["file_name"]

                # First instance we just send the file name so the client can can record it
                private_message = get_private_connection(user.get_username(), response["audience"], file)
                clientSocketUdp.sendto(private_message.encode(), (audience_ip, audience_port))

                try:
                    # We dont assume the file type and so we read in bytes
                    fp = open(file, "rb")
                    data = fp.read(1024)
                    print("> Sending file ...")
                    while data:
                        if clientSocketUdp.sendto(data, (audience_ip, audience_port)):
                            data = fp.read(udp_buffer)
                    print("> File sent")
                    fp.close()
                except FileNotFoundError:
                    print("> " + file + " is not a file")

            thread_lock.notify()
            sending = False


# This function is responsible for receiving and processing server responses
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
            # Empty array means no new messages after given timestamp
            if len(response) == 0:
                print("> Server Response: No new messages to read")
            # Server received a format that's not compatible with message log file
            elif response[0] == "Incorrect format":
                print("> Incorrect format given, we expect: RDM 08 Apr 2021 13:59:19. Try again")
            # Messages found in server, loop through and print to user
            else:
                print("> See new messages below: ")
                for message in response:
                    print("> Server Response: ", message.strip())

        elif command == "ATU":
            # Empty array, no other users online
            if len(response) == 0:
                print("> Server Response: No other active users")
            # Array not empty, loop through printing online users
            else:
                for active_users in response:
                    print("> Server Response: ", active_users)

        elif command == "OUT":
            print("> Server Response: ", response)
            # Do all the closing of client sockets and exit
            clientSocket.shutdown(SHUT_RDWR)
            clientSocket.close()
            os._exit(0)

        elif command == "UDP":
            # We dont communicate with the server, so go to private conn handle and establish direct conn with client
            private_send_handler(login_response)

        # All other responses are a simple single message that can be displayed here
        else:
            print("> Server Response: ", response)

# Thread responsible for taking in user input and sending to server
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
                print("> An argument must follow MSG. For example: MSG Hello World! Try again")

            else:
                # Convert to json and send msg to server
                message = post_msg(args, user.get_username())
                clientSocket.send(message.encode())

        elif command == "DLT":
            # Get args following dlt
            msg_num, timestamp = partition_two_arg(user_input)

            # Incorrect argument given
            if not msg_num or not timestamp:
                print("> Exactly two arguments must follow DLT. For example: DLT #1 08 Apr 2021 13:59:19. Try again")

            else:
                # Put request to be sent to server as JSON object
                delete = put_dlt(msg_num, timestamp, user.get_username())
                clientSocket.send(delete.encode())

        elif command == "EDT":
            # Get args following edt
            msg_num, timestamp, msg = partition_edt(user_input)

            if not msg_num or not timestamp or not msg:
                print(
                    "> Exactly three arguments must follow EDT. For example: EDT #1 08 Apr 2021 13:59:19 Hello "
                    "World. Try again")

            else:
                # Put request to be sent to server as JSON object
                edit = put_edit(msg_num, timestamp, msg, user.get_username())
                clientSocket.send(edit.encode())

        elif command == "RDM":
            # Get args following rdm
            timestamp = partition_one_arg(user_input)
            if not timestamp:
                print("> Exactly one argument must follow RDM. For example: RDM 08 Apr 2021 13:59:19. Try again")

            else:
                # Post request to be sent to server as JSON object
                read_messages = post_read_messages(timestamp, user.get_username())
                clientSocket.send(read_messages.encode())

        elif command == "ATU":
            # Get request to be sent to server as JSON object
            active_users = get_active_users(user.get_username())
            clientSocket.send(active_users.encode())

        elif command == "OUT":
            # Post request to be sent to server as JSON object
            logout = post_logout(user.get_username())
            clientSocket.send(logout.encode())
            active = False

        elif command == "UDP":
            # Get args following dlt
            audience, file_name = partition_two_arg(user_input)
            if not audience or not file_name:
                print("> Exactly two arguments must follow UDP. For example: UPD Obi-wan lecture1.mp4. Try again")

            else:
                # Bypass server, establish connection with another client but first we issue something simmilar to ATU
                # to get the clients PORT and IP address
                peer_to_peer = get_private_connection(user.get_username(), audience, file_name)
                clientSocket.send(peer_to_peer.encode())

        else:
            # No command from the expected list was found, issue user to try again
            print("> You did not enter a command from the list. Try again")

        # Wait for server response before prompting user again
        time.sleep(0.1)

# This function is responsible for creating a new thread for the client. Three threads it total:
# 1. We create one private thread for receiving files from other clients.
# 2. We create one thread for receiving info from the server.
# 3. We create one thread for sending info to the server.
def create_user_threads():
    private_recv_thread = threading.Thread(name="PrivateRecvHandler", target=private_recv_handler)
    private_recv_thread.daemon = True
    private_recv_thread.start()

    # Thread for receiving
    recv_thread = threading.Thread(name="RecvHandler", target=recv_handler)
    recv_thread.daemon = True
    recv_thread.start()

    # Thread for sending
    send_thread = threading.Thread(name="SendHandler", target=send_handler)
    send_thread.daemon = True
    send_thread.start()

    while True:
        time.sleep(0.1)

# First function that is called when client starts up. We get login details and send to server for validation
# Upon success we create threads for the client.
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

        # Too many invalid passwords sent to server
        elif response == "USER_BLOCKED":
            print("> Too many invalid password attempts, account blocked. Please try again later")
            try:
                clientSocket.shutdown(SHUT_RDWR)
                clientSocket.close()
                sys.exit()
                break
            except Exception:
                pass
        # Check server response, if invalid password prompt user
        elif response == "INVALID_PASSWORD":
            print("Invalid Password. Please try again")

        # Check server response, if invalid username prompt user
        elif response == "INVALID_USERNAME":
            print("Invalid Username. Please try again")

# Main function to try login.
if __name__ == "__main__":
    try:
        login()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
