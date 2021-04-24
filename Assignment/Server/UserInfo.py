# When the server starts up we load all the information pertaining to users
# in a list of dictionaries. This information is originally going to be unknown, though will be updated
# once the user is logged in.
def init_user_data(userData, passAttLimit):
    credFp = open("Credentials.txt", "r")
    credentials = credFp.readlines()
    addingData = True

    while addingData:
        for loginDetails in credentials:
            details = loginDetails.split(' ')
            username = details[0]
            password = details[1].strip()

            userData[username] = ({
                'username': username,
                'password': password,
                'blocked': False,
                'passAttLimit': passAttLimit,
                'passwordAttempts': 0,
                'blockTime': 0,
                'status': 'offline',
                'loginTime': 0,
                'logoutTime': 0,
                'ipAddr': 0,
                'port': 0,
                'udpPort': 0,
                'inbox': [],
                'privConns': []

            })

        addingData = False


# Big update once user logs in
def update_user_data_dump(payload, user_data):
    username = payload["username"]
    password = payload["password"]
    ip_addr = payload["ip_address"]
    port = payload["port"]
    udp_port = payload["udp_port"]

    user_data[username]['username'] = username
    user_data[username]['password'] = password
    user_data[username]['ipAddr'] = ip_addr
    user_data[username]['port'] = port
    user_data[username]['udpPort'] = udp_port
    user_data[username]['status'] = "online"


# For updating specific user information
def update_user_data_specific(user_data, user, key, val):
    user_data[user][key] = val
