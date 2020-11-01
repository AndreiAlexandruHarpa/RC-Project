import socket
import struct

from random import randint


class Client(object):

    def __init__(self, mac_addr, port):
        self.mac_addr = mac_addr
        self.port = port
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
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.settimeout(0.5)
        self.sock.bind(('', self.port))
        self.transactionID = b''
        for i in range(4):
            n = randint(0, 255)
            self.transactionID += struct.pack('!B', n)

    def getMacAddressInBytes(self):
        mac = b''
        for i in range(2, 14, 2):
            m = int(self.mac_addr[i:i + 2], 16)
            mac += struct.pack('!B', m)
        return mac

    def discover(self):
        packet = b''
        packet += b'\x01'  # Message type: Boot Request
        packet += b'\x01'  # Hardware type: Ethernet
        packet += b'\x06'  # Hardware address length: 6
        packet += b'\x00'  # Hops: 0
        packet += self.transactionID  # Transaction ID (random)
        packet += b'\x00\x00'  # Seconds elapsed: 0
        packet += b'\x00\x00'  # Flags: 0
        packet += b'\x00\x00\x00\x00'  # Client IP address: 0.0.0.0
        packet += b'\x00\x00\x00\x00'  # Your (client) IP address: 0.0.0.0
        packet += b'\x00\x00\x00\x00'  # Next Server IP address: 0.0.0.0
        packet += b'\x00\x00\x00\x00'  # Gateway IP address: 0.0.0.0
        packet += self.getMacAddressInBytes()  # Client hardware address(16 bytes)
        packet += b'\x00' * 10
        packet += b'\x00' * 64  # Server name not given
        packet += b'\x00' * 124  # Boot file name not given
        packet += b'\x63\x82\x53\x63'  # Magic Cookie: DHCP
        packet += b'\xff'  # Options endmark

        self.sock.sendto(packet, ('<broadcast>', 67))

    def listen_broadcast(self):
        data, addr = self.sock.recvfrom(1024)
        self.ip = data.decode()
        print("received: " + str(data.decode()))

    def request(self):
        print('request: ' + self.ip)
