import socket
import struct
import Packet as pk
import threading
import ipaddress
import tkinter as tk

from random import randint


def get_host_name():
    name = socket.gethostname()
    host_name = bytes(name, 'utf-8')
    return host_name


class Client:

    def __init__(self, mac_address, port, gui):
        self.gui = gui
        self.mac_address = mac_address
        self.port = port
        self.ip = ipaddress.ip_address('0.0.0.0')
        self.requested_ip = ipaddress.ip_address('0.0.0.0')
        self.received_ip = ipaddress.ip_address('0.0.0.0')
        self.server_ip = ipaddress.ip_address('0.0.0.0')
        self.mask = ipaddress.ip_address('0.0.0.0')
        self.gateway_address = ipaddress.ip_address('0.0.0.0')
        self.timestamp = 0
        self.time_servers = []
        self.client_name = None
        self.dns_servers = []
        self.lease_time = None
        self.renewal_value = None
        self.rebinding_value = None
        self.start_lease_time = None
        self.end_lease_time = None
        self.lease_time_thread = None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('192.168.1.87', self.port))
        self.transactionID = randint(0, 2**32 - 1)
        self.MAGIC_COOKIE = '0x63825363'
        self.fip = True
        self.renew_timer = None
        self.rebind_timer = None

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
        from os import stat
        if stat("ip_history.txt").st_size != 0:
            f = open("ip_history.txt", "r")
            ip_list = f.read().split('\n')
            self.requested_ip = ip_list[-1].split('-')[0]
            pack.ip = ipaddress.ip_address(self.requested_ip)
            f.close()

        packet = pack.pack()
        self.gui.setText(packet)
        self.sock.sendto(packet, ('255.255.255.255', 67))
        self.listen_broadcast()
        print(self.received_ip)

    def offer(self, data):
        self.gui.decline['state'] = tk.NORMAL
        self.gui.request['state'] = tk.NORMAL
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
        pack.ip = self.received_ip
        packet = pack.pack()
        self.sock.sendto(packet, ('<broadcast>', 67))
        self.listen_broadcast()

    def acknowledge(self, packet):
        self.ip = packet.YIADDR
        self.server_ip = packet.SIADDR

        for option in packet.options:
            if option[0] == 51:
                self.lease_time = struct.unpack_from('!I', option[2])[0]
            if option[0] == 1:
                self.mask = option[2]
            if option[0] == 3:
                self.gateway_address = option[2]
            if option[0] == 58:
                self.renewal_value = struct.unpack_from('!I', option[2])[0]
            if option[0] == 59:
                self.renewal_value = struct.unpack_from('!I', option[2])[0]
            # 2, 4 si 15 de intrebat
        f = open("ip_history.txt", "a")
        f.write('\n' + str(self.ip) + '-' + str(self.server_ip))
        f.close()
        self.gui.release['state'] = tk.NORMAL
        self.gui.inform['state'] = tk.NORMAL
        self.gui.discover['state'] = tk.DISABLED
        self.gui.request['state'] = tk.DISABLED

    def release(self):
        pack = pk.Packet(self.gui)
        pack.OP = 1
        pack.XID = self.transactionID
        pack.CHADDR = self.getMacAddressInBytes()
        pack.MSG_TYPE = 7
        pack.CIADDR = self.ip
        packet = pack.pack()
        self.sock.sendto(packet, (str(self.server_ip), 67))
        self.ip = ipaddress.ip_address('0.0.0.0')
        self.server_ip = ipaddress.ip_address('0.0.0.0')
        self.gateway_address = ipaddress.ip_address('0.0.0.0')
        self.requested_ip = ipaddress.ip_address('0.0.0.0')
        self.received_ip = ipaddress.ip_address('0.0.0.0')
        self.mask = ipaddress.ip_address('0.0.0.0')
        self.lease_time = 0
        self.renewal_value = 0
        self.rebinding_value = 0
        self.start_lease_time = 0
        self.end_lease_time = 0
        if self.rebind_timer:
            self.rebind_timer.cancel()
        if self.renew_timer:
            self.renew_timer.cancel()
        self.gui.release['state'] = tk.DISABLED
        self.gui.inform['state'] = tk.DISABLED
        self.gui.decline['state'] = tk.DISABLED
        self.gui.discover['state'] = tk.NORMAL

    def inform(self):
        pack = pk.Packet(self.gui)
        pack.OP = 1
        pack.XID = self.transactionID
        pack.CHADDR = self.getMacAddressInBytes()
        pack.CIADDR = self.ip
        pack.MSG_TYPE = 8
        packet = pack.pack()
        self.sock.sendto(packet, (str(self.server_ip), 67))

    def listen_broadcast(self):
        packet = pk.Packet(self.gui)
        data_received = []

        while True:
            try:
                self.sock.settimeout(2)
                data_received.append(self.sock.recvfrom(1024))
                self.sock.settimeout(None)
            except socket.timeout:
                break
        for data in data_received:
            packet.unpack(data[0])
            if self.transactionID == packet.XID and packet.MAGIC_COOKIE == self.MAGIC_COOKIE:
                if packet.MSG_TYPE == 2:
                    if self.offer(packet):
                        self.received_ip = packet.YIADDR
                        break
                    else:
                        self.received_ip = packet.YIADDR
        if self.transactionID == packet.XID and packet.MAGIC_COOKIE == self.MAGIC_COOKIE:
            if packet.MSG_TYPE == 5:
                self.acknowledge(packet)
                self.renew_timer = threading.Timer(0.5 * 10, self.request)
                self.renew_timer.start()
            if packet.MSG_TYPE == 6:
                self.gui.setText('\n<< NAK')
                if self.lease_time:
                    self.rebind_timer = threading.Timer(0.375 * 10, self.discover)
                    self.rebind_timer.start()

    def get_ip(self):
        return self.ip


