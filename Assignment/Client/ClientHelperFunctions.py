import json


# This file has two main responsibilities:
# 1. Functions for each client command to be made into a JSON objects to send the server.
# 2. Basic helper function to partition user commands/input.

# Login JSON Object
def post_login(ip_addr, port, udp_port):
    payload = json.dumps({
        "command": "login",
        "ip_address": ip_addr,
        "port": port,
        "udp_port": udp_port,
        "username": input("> Enter username: "),
        "password": input("> Enter password: ")
    })

    return payload


# MSG JSON Object
def post_msg(message, username):
    payload = json.dumps({
        "command": "MSG",
        "message": message,
        "username": username
    })

    return payload


# DLT JSON Object
def put_dlt(msg_num, timestamp, username):
    payload = json.dumps({
        "command": "DLT",
        "msg_num": msg_num,
        "timestamp": timestamp,
        "message_to_dlt": msg_num + " " + timestamp + " " + username,
        "username": username
    })

    return payload


# EDT JSON Object
def put_edit(msg_num, timestamp, message, username):
    payload = json.dumps({
        "command": "EDT",
        "msg_num": msg_num,
        "timestamp": timestamp,
        "message": message,
        "message_to_edt": msg_num + " " + timestamp + " " + username,
        "username": username
    })

    return payload


# RDM JSON Object
def post_read_messages(timestamp, username):
    payload = json.dumps({
        "command": "RDM",
        "timestamp": timestamp,
        "username": username
    })

    return payload


# ATU JSON Object
def get_active_users(username):
    payload = json.dumps({
        "command": "ATU",
        "username": username
    })

    return payload


# OUT JSON Object
def post_logout(username):
    payload = json.dumps({
        "command": "OUT",
        "username": username
    })

    return payload


# Query the server to see if the user we want to establish a private connection with is online
def get_private_connection(presenter, audience, file):
    payload = json.dumps({
        "command": "UDP",
        "presenter": presenter,
        "audience": audience,
        "file_name": file
    })

    return payload


# Get the first argument of user input
def partition_command(user_input):
    command = user_input.partition(" ")
    return command[0]


# Get the second argument of user input
def partition_one_arg(user_input):
    msg = user_input.partition(" ")
    return msg[2]


# Get the third argument of user input
def partition_two_arg(user_input):
    dlt = user_input.partition(" ")
    component = dlt[2].partition(" ")
    msg_num = component[0]
    timestamp = component[2]

    return msg_num, timestamp


# Get the first two arguments after EDT
def partition_edt(user_input):
    msg_num, ts = partition_two_arg(user_input)
    # Everything from 0 - 20 store in timestamp
    timestamp = ts[:20]
    # Everything from 20 onward store in message
    message = ts[20:]
    return msg_num, timestamp, message


# Get first argument
def partition_rdm(user_input):
    ts = partition_one_arg(user_input)
    # Store everything from 0 to 20 in timestamp. Ignore everything else
    timestamp = ts[:20]
    return timestamp
