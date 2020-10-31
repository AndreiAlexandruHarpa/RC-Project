import socket


class Client(object):

    def __init__(self, mac_addr):
        self.mac_addr = mac_addr
        self.ip = '0.0.0.0'
        self.mask = None
        self.timestamp = 0
        self.gateway_addr = None
        self.time_servers = []
        self.client_name = None
        self.dns_servers = []
        self.requested_lease_time = None
        self.start_lease_time = None
        self.end_lease_time = None
        self.smtp_server = None
        self.pop3_server = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    def discover(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.settimeout(0.2)
        self.sock.bind(("", 44444))
        message = b"broadcast message"
        self.sock.sendto(message, ('<broadcast>', 37020))

    def listen_broadcast(self):
        data, addr = self.sock.recvfrom(1024)
        self.ip = data.decode();
        print("received: " + str(data.decode()))

    def request(self):
        print('request: ' + self.ip)
