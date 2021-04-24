import time
import datetime
import re

# Check all edge cases for a user when they try login:
# 1. Wrong username
# 2. Wrong password
# 3. Blocked
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


# Open the log file and update it with a new user when they connect to the server
def create_user_log(payload, user_data):
    file_to_open = "userlog.txt"

    username = payload["username"]
    ext_one_ip = str(user_data[username]["ipAddr"])
    ext_two_port = str(user_data[username]['udpPort'])

    format_log_file(username, file_to_open, ext_one_ip, ext_two_port)


# This should really be called update_message_log as we update the message log whenever a user issues a new message
def create_message_log(payload):
    file_to_open = "messagelog.txt"

    username = payload["username"]
    ext_one_msg = payload["message"]
    ext_two_edited = "<unedited>"

    format_log_file(username, file_to_open, ext_one_msg, ext_two_edited)


# Count the number of lines in a file to that we can
# prefix both message log and user log with correct user/message order
def get_num_lines(file_to_open):
    num_lines = sum(1 for line in open(file_to_open))
    num_lines += 1

    return num_lines


# Get the current date and remove microseconds, then convert to a named month format with day first
def get_time_stamp():
    # Get todays date
    timestamp = datetime.date.today()
    # Remove microseconds
    cur_time = datetime.datetime.now().time().replace(microsecond=0)
    # Convert to day month year format
    date = datetime.datetime(timestamp.year, timestamp.month, timestamp.day)
    cur_time = str(cur_time)
    timestamp = date.strftime("%d %b %Y ")

    timestamp += cur_time

    return timestamp


# Add user message to the log file in a consistent format
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


# Delete a message from the message.log file
def delete_message(payload):
    dlt = payload["message_to_dlt"]
    file_to_open = "messagelog.txt"
    error_response = "No message for you to delete"
    success_response = ("Message " + payload["msg_num"] + " at " + payload["timestamp"] + " has been deleted")

    return update_file(file_to_open, dlt, error_response, success_response)


# Edit a message from the message.log file
def edit_message(payload):
    edt = payload["message_to_edt"]
    message_list = []
    response = "No message for you to edit"
    match = False
    file_to_open = "messagelog.txt"
    with open(file_to_open, "r+") as fp:
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
    write_to_file(message_list, file_to_open)
    return response


# Read all new messages after the given timestamp
def read_messages(payload):
    new_messages = []
    message_time = payload["timestamp"]
    # Validate the timestamp given by the user matches the timestamp structure of the server
    try:
        message_time = time.strptime(message_time, "%d %b %Y %H:%M:%S")
    # Wrong format received
    except ValueError:
        incorrect_format = "Incorrect format"
        new_messages.append(incorrect_format)
        return new_messages
    fp = open("messagelog.txt", "r")
    for line in fp:
        timestamp = line[3:23]
        message = time.strptime(timestamp, "%d %b %Y %H:%M:%S")

        # Check for messages AFTER the timestamp given
        if str(message) > str(message_time):
            new_messages.append(line)
    fp.close()
    return new_messages

# Check the users that are online and store in an array
def active_users(user_data, payload):
    active_user_list = []
    curr_user = payload["username"]
    for user in user_data:
        if user != 0 and curr_user != user and user_data[user]["status"] == 'online':
            active_user = (str(user) +
                           ", " +
                           str(user_data[user]['ipAddr']) +
                           ", " +
                           str(user_data[user]['udpPort']) +
                           ", active since " +
                           str(user_data[user]['loginTime']))

            active_user_list.append(active_user)

    return active_user_list

# Log a user out and update the user.log file
def logout(user_data, payload):
    dlt_user = payload["username"]
    user_data[dlt_user]['status'] = "offline"
    error_response = "Couldn't log you out"
    success_response = ("> Goodbye " + dlt_user + ". You are now logged out")
    file_to_open = "userlog.txt"

    return update_file(file_to_open, dlt_user, error_response, success_response)


# Return the users IP and Port number so that a private connection may be established
# between two clients.
def get_private_connection_info(user_data, payload):
    audience = payload["audience"]
    ip = 0
    port = 0
    response = "Unexpected"
    try:
        # Trying to get information about an offline user
        if user_data[audience]['status'] == "offline":
            response = "offline"

        # Trying to get information about oneself
        elif user_data[audience]['username'] == payload["presenter"]:
            response = "yourself"

        # User online, get information
        else:
            ip = user_data[audience]['ipAddr']
            port = user_data[audience]['udpPort']
            response = "online"

        return ip, port, response

    except KeyError:
        return ip, port, "keyError"


# Opens a specified file (either userlog or messagelog), deletes the appropriate line,
# and adjusts the user positions accordingly
def update_file(file_to_open, dlt, error_response, success_response):
    response = error_response
    message_list = []
    match = False

    with open(file_to_open, "r+") as fp:
        for line in fp:
            if check_for_match(line, dlt):
                # Response to the client
                response = success_response
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
    write_to_file(message_list, file_to_open)

    return response


# See if a message exists in a file
def check_for_match(line, dlt):
    # Remove colons
    no_colon = re.sub(';', '', line)
    # Search for exact match within each line
    if dlt[1:] in no_colon:
        return True


# Takes in a list and writes the contents to messagelog.txt
def write_to_file(message_list, file):
    fp = open(file, "w")
    for new_line in message_list:
        fp.write(new_line)
    fp.close()
