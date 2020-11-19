import socket
import struct
import numpy as np

from random import randint


class Client(object):

    def __init__(self, mac_addr, port):
        self.mac_addr = mac_addr
        self.port = port
        self.ip = None
        self.requested_ip = b'\xc0\xa8\x00\x01' #  test
        self.server_ip = None
        self.options = np.zeros(12)
        self.mask = None
        self.timestamp = 0
        self.gateway_addr = None
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

    def get_host_name(self):
        name = socket.gethostname()
        host_name = bytes(name, 'utf-8')
        return host_name

    def discover(self):
        packet = b''
        packet += b'\x01'  # Message type: Boot Request
        packet += b'\x01'  # Hardware type: Ethernet
        packet += b'\x06'  # Hardware address length: 6
        packet += b'\x00'  # Hops: 0      3
        packet += self.transactionID  # Transaction ID (random)   7
        packet += b'\x00\x00'  # Seconds elapsed: 0
        packet += b'\x00\x00'  # Flags: 0    11
        packet += b'\x00\x00\x00\x00'  # Client IP address: 0.0.0.0   15
        packet += b'\x00\x00\x00\x00'  # Your (client) IP address: 0.0.0.0
        packet += b'\x00\x00\x00\x00'  # Next Server IP address: 0.0.0.0
        packet += b'\x00\x00\x00\x00'  # Gateway IP address: 0.0.0.0  27
        packet += self.getMacAddressInBytes()  # Client hardware address(16 bytes)  33
        packet += b'\x00' * 10   # 43
        packet += b'\x00' * 64  # Server name not given   107
        packet += b'\x00' * 124  # Boot file name not given   231
        packet += b'\x63\x82\x53\x63'  # Magic Cookie: DHCP   235
        packet += b'\x35\x01\x01'  # Option 53, Message type  238
        packet += b'\x32\x04\xc0\xa8\x00\x01'  # Option 50, Request IP address
        packet += b'\x0c\x0f'
        packet += self.get_host_name()
        packet += b'\xff'  # Option 255 Endmark

        self.sock.sendto(packet, ('<broadcast>', 67))

    def offer(self, data):
        given_ip = data[16:20]
        # trebuie sa mai verificam daca este activa optiune de requested ip din gui
        """
                   byte = 239
                   while byte < len(data):
                       if data[byte] == 51:
                           self.lease_time = data[byte + 2] << 24 | data[byte + 3] << 16 | data[byte + 4] << 8 | data[byte + 5]
                           break
                       else:
                           offset = data[byte + 1]
                           byte = byte + offset + 2
                   return 0
               else:
                   return 1
        """
        if given_ip == self.requested_ip:
            return 0
        else:
            return 1

    def server_bin_to_int(self):
        ip = ''
        for i in range(len(self.server_ip) - 1):
            ip += str(self.server_ip[i]) + '.'
        ip += str(self.server_ip[len(self.server_ip) - 1])
        return ip

    def request(self):
        packet = b''
        packet += b'\x01'  # Message type: Boot Request
        packet += b'\x01'  # Hardware type: Ethernet
        packet += b'\x06'  # Hardware address length: 6
        packet += b'\x00'  # Hops: 0      3
        packet += self.transactionID  # Transaction ID (random)   7
        packet += b'\x00\x00'  # Seconds elapsed: 0
        packet += b'\x00\x00'  # Flags: 0    11
        packet += b'\x00\x00\x00\x00'  # Client IP address: 0.0.0.0   15
        packet += b'\x00\x00\x00\x00'  # Your (client) IP address: 0.0.0.0
        packet += b'\x00\x00\x00\x00'  # Next Server IP address: 0.0.0.0   de verificat daca trimitem pe broadcast
        packet += b'\x00\x00\x00\x00'  # Gateway IP address: 0.0.0.0  27
        packet += self.getMacAddressInBytes()  # Client hardware address(16 bytes)  33
        packet += b'\x00' * 10  # 43
        packet += b'\x00' * 64  # Server name not given   107
        packet += b'\x00' * 124  # Boot file name not given   231
        packet += b'\x63\x82\x53\x63'  # Magic Cookie: DHCP   235
        packet += b'\x35\x01\x03'  # Option 53, Message type  238
        packet += b'\x32\x04\xc0\xa8\x00\x01'  # Option 50, Request IP address
        packet += b'\x36\x04'  # Option 54 DHCP Server
        packet += self.server_ip
        packet += b'\xff'  # Option 255 Endmark

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
        data, addr = self.sock.recvfrom(1024)
        if data[4:8] == self.transactionID:
            if data[0] == 2 and data[238] == 2:
                if self.offer(data) == 1:
                    self.discover()
            elif data[0] == 2 and data[238] == 5:
                self.acknowledge(data)

    def request(self):
        print('request: ' + self.ip)

    def get_ip(self):
        return self.ip
