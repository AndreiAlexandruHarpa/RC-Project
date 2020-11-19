import socket
import struct
import Packet as pk
import threading
import ipaddress

from random import randint


def get_host_name():
    name = socket.gethostname()
    host_name = bytes(name, 'utf-8')
    return host_name


class Client(threading.Thread):

    def __init__(self, mac_address, port, gui):
        super().__init__()
        self.gui = gui
        self.mac_address = mac_address
        self.port = port
        self.ip = None
        self.requested_ip = b'\xc0\xa8\x00\x01'
        self.server_ip = ipaddress.ip_address('0.0.0.0')
        self.mask = None
        self.timestamp = 0
        self.gateway_address = None
        self.time_servers = []
        self.client_name = None
        self.dns_servers = []
        self.requested_lease_time = None
        self.lease_time = None
        self.start_lease_time = None
        self.end_lease_time = None
        self.smtp_server = None
        self.pop3_server = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.settimeout(5)
        self.sock.bind(('', self.port))
        self.transactionID = randint(0, 2**32 - 1)
        self.MAGIC_COOKIE = '0x63825363'

    def getMacAddressInBytes(self):
        mac = b''
        for i in range(2, 14, 2):
            m = int(self.mac_address[i:i + 2], 16)
            mac += struct.pack('!B', m)
        return mac

    def discover(self):
        pack = pk.Packet(self.gui)
        pack.OP = 1
        pack.XID = self.transactionID
        pack.CHADDR = self.getMacAddressInBytes()
        pack.MSG_TYPE = 1
        packet = pack.pack()

        print(packet)
        print(len(packet))
        self.sock.sendto(packet, ('<broadcast>', 34344))
        data, address = self.sock.recvfrom(1024)
        packet = pk.Packet(self.gui)
        packet.unpack(data)
        print(len(packet.options))

    def offer(self, data):
        for option in data.options:
            if option[0] == 50:
                if data.YIADDR == self.requested_ip:
                    return True
                else:
                    return False
        return True

    def request(self):
        pack = pk.Packet(self.gui)
        pack.OP = 1
        pack.XID = self.transactionID
        pack.CHADDR = self.getMacAddressInBytes()
        pack.MSG_TYPE = 3
        packet = pack.pack()  # Option 53, Message type  238

        self.sock.sendto(packet, ('<broadcast>', 67))

    def acknowledge(self, data):
        self.ip = data[12:16]
        byte = 239
        while byte < len(data):
            if data[byte] == 54:
                self.server_ip = data[byte + 2: byte + 6]
                continue
            elif data[byte] == 51:
                self.lease_time = data[byte + 2] << 24 | data[byte + 3] << 16 | data[byte + 4] << 8 | data[byte + 5]
                continue
            elif data[byte] == 1:
                self.mask = data[byte + 2: byte + 6]

    def listen_broadcast(self):
        packet = pk.Packet(self.gui)
        data_received = []
        temp = False
        while True:
            if not temp:
                self.discover()
            for i in range(10):
                data_received.append(self.sock.recvfrom(1024))
            for data in data_received:
                packet.unpack(data[0])
                if self.transactionID == packet.XID and packet.MAGIC_COOKIE == self.MAGIC_COOKIE:
                    if packet.MSG_TYPE == 2:
                        if self.offer(packet):
                            temp = True
                            break
            if not temp:
                continue

    def request(self):
        print('request: ' + self.ip)

    def get_ip(self):
        return self.ip
