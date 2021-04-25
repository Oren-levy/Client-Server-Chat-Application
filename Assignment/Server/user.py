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