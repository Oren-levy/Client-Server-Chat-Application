import json
import sys
import re


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


def post_msg(message, username):
    payload = json.dumps({
        "command": "MSG",
        "message": message,
        "username": username
    })

    return payload


def put_dlt(msg_num, timestamp, username):
    payload = json.dumps({
        "command": "DLT",
        "msg_num": msg_num,
        "timestamp": timestamp,
        "message_to_dlt": msg_num + " " + timestamp + " " + username,
        "username": username
    })

    return payload


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


def post_read_messages(timestamp, username):
    payload = json.dumps({
        "command": "RDM",
        "timestamp": timestamp,
        "username": username
    })

    return payload


def get_active_users(username):
    payload = json.dumps({
        "command": "ATU",
        "username": username
    })

    return payload


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


def partition_command(user_input):
    command = user_input.partition(" ")
    return command[0]


def partition_one_arg(user_input):
    msg = user_input.partition(" ")
    return msg[2]


def partition_two_arg(user_input):
    dlt = user_input.partition(" ")
    component = dlt[2].partition(" ")
    msg_num = component[0]
    timestamp = component[2]

    return msg_num, timestamp


def partition_edt(user_input):
    msg_num, ts = partition_two_arg(user_input)
    timestamp = ts[:20]
    message = ts[20:]
    return msg_num, timestamp, message


def partition_rdm(user_input):
    ts = partition_one_arg(user_input)
    timestamp = ts[:20]
    return timestamp
