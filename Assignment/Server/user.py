class User:

    def __init__(self, limit):
        self.username = " "
        self.password = " "
        self.blocked = False
        self.blockTime = 0
        self.passAttLimit = limit
        self.passAtt = 0
        self.status = "offline"
        self.loginTime = 0
        self.logoutTime = 0
        self.ipAddr = 0
        self.udp_port = 0
        self.inbox = 0
        self.privConns = 0

    def update_user_info_dump(self, payload):
        self.username = payload["username"]
        self.password = payload["password"]
        self.ipAddr = payload["ip_address"]
        self.udp_port = payload["udp_port"]

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_blocked(self):
        return self.blocked

    def set_blocked(self, val):
        self.blocked = val

    def get_block_time(self):
        return self.blockTime

    def start_block_timer(self, start):
        self.blockTime = start

    def get_pass_atmpt_limit(self):
        return self.passAttLimit

    def get_pass_atmpt(self):
        return self.passAtt

    def restart_pass_atmpt(self):
        self.passAtt = 0

    def incr_pass_atmpt(self):
        print(self.passAtt)
        self.passAtt += 1


#
# def authenticate_user_login(user, userData):
#     username = user.get_username()
#     password = user.get_password()
#     # Check username exists
#     if userData.get(username) is not None:
#         # User is blocked
#         if user.get_blocked() is True:
#             # Change to unblocked if enough time has past
#             if (time.time() - user.get_block_time()) > 20:
#                 user.set_blocked(False)
#             # Not enough time has past, user remains blocked.
#             else:
#                 return "USER_BLOCKED"
#
#         # Wrong password, increment failed attempts
#         if userData[username]['password'] != password:
#             user.incr_pass_atmpt()
#             # Limit reached, block user, start block-timer, and restart count for passwordAttempts
#             if user.get_pass_atmpt() == user.get_pass_atmpt_limit():
#                 user.set_blocked(True)
#                 user.start_block_timer(time.time())
#                 user.restart_pass_atmpt()
#                 return "USER_BLOCKED"
#
#             return "INVALID_PASSWORD"
#
#         # Passwords matches AND not blocked - approve login
#         return "LOGIN_SUCCESS"
#
#     # Username doesn't exist
#     else:
#         return "INVALID_USERNAME"