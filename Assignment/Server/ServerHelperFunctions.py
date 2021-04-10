import json
import sys
from socket import *
import time
import datetime
import re
import os.path


def authenticate_user_login(userDetails, userData):
    username = userDetails["username"]
    password = userDetails["password"]

    # Check username exists
    if userData.get(username) is not None:
        # User is blocked
        if userData[username]['blocked'] is True:
            # Change to unblocked if enough time has past
            if (time.time() - userData[username]['blockTime']) > 10:
                userData[username]['blocked'] = False
            # Not enough time has past, user remains blocked.
            else:
                return "USER_BLOCKED"

        # Wrong password, increment failed attempts
        if userData[username]['password'] != password:
            userData[username]['passwordAttempts'] += 1
            # Limit reached, block user, start block-timer, and restart count for passwordAttempts
            if userData[username]['passwordAttempts'] == userData[username]['passAttLimit']:
                userData[username]['blocked'] = True
                userData[username]['blockTime'] = time.time()
                userData[username]['passwordAttempts'] = 0
                return "USER_BLOCKED"

            return "INVALID_PASSWORD"

        # Passwords matches AND not blocked - approve login
        return "LOGIN_SUCCESS"

    # Username doesn't exist
    else:
        return "INVALID_USERNAME"


def create_user_log(payload, user_data):
    file_to_open = "userlog.txt"

    username = payload["username"]
    ext_one_ip = str(user_data[username]["ipAddr"])
    ext_two_port = str(user_data[username]['udp_port'])

    format_log_file(username, file_to_open, ext_one_ip, ext_two_port)


def create_message_log(payload):
    file_to_open = "messagelog.txt"

    username = payload["username"]
    ext_one_msg = payload["message"]
    ext_two_edited = "<unedited>"

    format_log_file(username, file_to_open, ext_one_msg, ext_two_edited)


def get_num_lines(file_to_open):
    num_lines = sum(1 for line in open(file_to_open))
    num_lines += 1

    return num_lines


def get_time_stamp():
    timestamp = datetime.date.today()
    cur_time = datetime.datetime.now().time().replace(microsecond=0)
    date = datetime.datetime(timestamp.year, timestamp.month, timestamp.day)
    cur_time = str(cur_time)
    timestamp = date.strftime("%d %b %Y ")

    timestamp += cur_time

    return timestamp


def format_log_file(username, file_to_open, ext_one, ext_two):
    fp = open(file_to_open, "a+")

    num_lines = get_num_lines(file_to_open)
    timestamp = get_time_stamp()

    format_log = (str(num_lines) +
                  "; " +
                  timestamp +
                  "; " +
                  username +
                  "; " +
                  ext_one +
                  "; " +
                  ext_two +
                  " " +
                  "\n")
    print(format_log)
    fp.write(format_log)
    fp.close()


# Return confirmation message to client
def user_confirm_message():
    num_lines = get_num_lines("messagelog.txt")
    num_lines = num_lines - 1
    timestamp = get_time_stamp()

    format_log = ("> Message #" +
                  str(num_lines) +
                  " posted at " +
                  timestamp)
    return format_log


def delete_message(payload):
    dlt = payload["message_to_dlt"]
    response = "No message for you to delete"
    message_list = []
    match = False

    with open("messagelog.txt", "r+") as fp:
        for line in fp:
            if check_for_match(line, dlt):
                # Response to the client
                response = ("Message " + payload["msg_num"] + " at " + payload["timestamp"] + " has been deleted")
                match = True
                continue

            # Shift the index down only after we find a match
            if match:
                # Get the msg number and subtract one to reflect the new msg order
                index = int(line[0]) - 1
                mod_line = line
                # [1:] gets all content from index one onward
                mod_line = str(index) + mod_line[1:]
                message_list.append(mod_line)

            # Otherwise add existing line
            else:
                message_list.append(line)

    fp.close()
    write_to_file(message_list)

    return response


def edit_message(payload):
    edt = payload["message_to_edt"]
    message_list = []
    response = "No message for you to edit"
    match = False
    with open("messagelog.txt", "r+") as fp:
        for line in fp:
            # Check if message#, timestamp, username match
            if check_for_match(line, edt):
                # Preserve message number despite editing the message
                index = int(line[0])
                # Get new timestamp
                timestamp = get_time_stamp()
                # Replace line in fp with edited line
                edited_line = (str(index) + "; " + timestamp + "; " + payload["username"] + ";" + payload[
                    "message"] + "; " + "<edited>" + '\n')
                response = ("Message " + payload["msg_num"] + " at " + payload["timestamp"] + " has been edited")
                match = True

            # If match, add edited line to the message_list
            if match:
                message_list.append(edited_line)
                match = False

            # Otherwise add the existing line
            else:
                message_list.append(line)

    fp.close()
    write_to_file(message_list)
    return response


def read_messages(payload):
    new_messages = []
    print(payload["timestamp"])
    print(payload["username"])
    message_time = payload["timestamp"]
    print("timestamp_to_check BEFORE: ", message_time)
    message_time = time.strptime(message_time, "%d %b %Y %H:%M:%S")
    print("timestamp_to_check AFTER: ", message_time[0:6])
    fp = open("messagelog.txt", "r")
    for line in fp:
        print("-------------------------------------------------------------------------------------------------")
        timestamp = line[3:23]
        print("timestamp BEFORE: ", timestamp)
        message = time.strptime(timestamp, "%d %b %Y %H:%M:%S")
        print("timestamp AFTER: ", message[0:6])
        print("-------------------------------------------------------------------------------------------------")

        if str(message) > str(message_time):
            new_messages.append(line)
            print("TRUE")
    fp.close()
    return new_messages


# See if a message exists in a file
def check_for_match(line, dlt):
    # Remove colons
    no_colon = re.sub(';', '', line)
    # Search for exact match within each line
    if dlt[1:] in no_colon:
        return True


# Takes in a list and writes the contents to messagelog.txt
def write_to_file(message_list):
    fp = open("messagelog.txt", "w")
    for new_line in message_list:
        fp.write(new_line)
    fp.close()
