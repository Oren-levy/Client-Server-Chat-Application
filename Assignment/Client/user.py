class User:

    def __init__(self, socket, ip, port, udp_port):
        self.username = ""
        self.password = ""
        self.socket = socket
        self.ipAddr = ip
        self.port = port
        self.udpPort = udp_port

    def update_user_dump(self, username, socket, ip, port, udp_port):
        self.username = username
        self.password = password
        self.socket = socket
        self.ipAddr = ip
        self.port = port
        self.udpPort = udp_port

    def get_username(self):
        return self.username

    def set_username(self, name):
        self.username = name

    def get_password(self):
        return self.password

    def set_password(self, password):
        self.password = password

    def get_socket(self):
        return self.socket

    def set_socket(self, socket):
        self.socket = socket

    def get_ip_addr(self):
        return self.ipAddr

    def set_ip_addr(self, ip_addr):
        self.ipAddr = ip_addr

    def get_port(self):
        return self.port

    def set_port(self, port):
        self.port = port

    def get_prv_port(self):
        return self.udpPort

    def set_prv_port(self, udp_port):
        self.udpPort = udp_port
