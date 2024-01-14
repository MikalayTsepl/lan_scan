from socket import *
from lxml import etree
import subprocess
import ipaddress
from getmac import get_mac_address as fetchmac
from scapy.all import *
from scapy.layers.l2 import Ether, ARP
import re
from datetime import datetime


class Scanner:
    ipadr = ""
    gateway_ip = ""
    gateway_mac = ""
    alive_hosts = []

    def __init__(self):
        sockt = socket.socket(AF_INET, SOCK_DGRAM)
        try:
            addr = ('8.8.8.8', 123)
            sockt.connect(addr)
            self.ipadr = sockt.getsockname()[0]
        except Exception:
            print("A connection error occured.")
        finally:
            sockt.close()

    def get_my_ip(self):
        return self.ipadr

    def get_gateway_info(self):
        com = f'route PRINT 0* | findstr {self.ipadr}'
        ip_gate = subprocess.check_output(com, shell=True).decode('cp866').split()[2]
        mac = fetchmac(ip=ip_gate)
        self.gateway_ip = ip_gate
        self.gateway_mac = mac
        gateway_inf = f'ip:{ip_gate} and mac:{mac}'
        return gateway_inf

    def is_alive(self, ip):
        disctime = datetime.now()
        current = disctime.strftime('%D %H:%M:%S')
        req = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
        result = srp(req, timeout=0.1, verbose=0)[0]
        for sent, received in result:
            self.alive_hosts.append(
                (received.psrc, received.hwsrc, self.get_prod_by_mac(received.hwsrc), str(current)))

    def get_prod_by_mac(self, mac):
        mac = mac.upper()
        count = 0
        octets = "".join(i for i in mac if (count := count + 1) <= 8)
        try:
            tree = etree.parse('vendorMacs.xml')
            prod_branch = tree.xpath(f'//*[@mac_prefix="{octets}"]')
            parsed = ""
            for i in prod_branch:
                parsed += str(etree.tostring(i))
            only_vendor = re.findall(r'vendor_name=\".*\"', parsed)[0]
            res = re.findall(r'\"(.*)\"', only_vendor)[0]
            return res
        except (IOError, IndexError):
            return "unknown"

    def scan_net(self):
        self.get_gateway_info()
        for ip in ipaddress.ip_network(f'{self.gateway_ip}/255.255.255.0', strict=False).hosts():
            self.is_alive(str(ip))

    def get_hosts(self):
        return self.alive_hosts

    def clear_hosts(self):
        self.alive_hosts.clear()

