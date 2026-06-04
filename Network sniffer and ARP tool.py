#!/usr/bin/env python3
"""
Demonstrates MITM attacks, packet capture, and network reconnaissance
FOR AUTHORIZED TESTING ONLY
"""

import socket
import struct
import threading
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class Packet:
    """Represents a captured network packet"""
    timestamp: float
    src_ip: str
    dst_ip: str
    protocol: str
    src_port: int
    dst_port: int
    payload: bytes
    raw_data: bytes

class PacketAnalyzer:
    """
    Educational packet sniffer demonstrating network protocol analysis
    """
    
    def __init__(self, interface="eth0"):
        self.interface = interface
        self.packets_captured = []
        self.running = False
        self.filters = {
            'tcp': True,
            'udp': True,
            'icmp': True,
            'arp': True
        }
        
    def parse_ethernet_header(self, data: bytes) -> dict:
        """Parse Ethernet frame header"""
        dest_mac = data[0:6]
        src_mac = data[6:12]
        eth_type = struct.unpack('!H', data[12:14])[0]
        
        return {
            'dest_mac': self.mac_to_str(dest_mac),
            'src_mac': self.mac_to_str(src_mac),
            'type': eth_type,
            'payload': data[14:]
        }
    
    def mac_to_str(self, mac: bytes) -> str:
        """Convert MAC bytes to string"""
        return ':'.join(f'{b:02x}' for b in mac)
    
    def parse_ip_header(self, data: bytes) -> dict:
        """Parse IP packet header"""
        version_ihl = data[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0xF
        header_length = ihl * 4
        
        total_length = struct.unpack('!H', data[2:4])[0]
        protocol = data[9]
        src_ip = socket.inet_ntoa(data[12:16])
        dst_ip = socket.inet_ntoa(data[16:20])
        
        return {
            'version': version,
            'header_length': header_length,
            'total_length': total_length,
            'protocol': protocol,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'payload': data[header_length:]
        }
    
    def parse_tcp_header(self, data: bytes) -> dict:
        """Parse TCP segment header"""
        src_port = struct.unpack('!H', data[0:2])[0]
        dst_port = struct.unpack('!H', data[2:4])[0]
        seq_num = struct.unpack('!I', data[4:8])[0]
        ack_num = struct.unpack('!I', data[8:12])[0]
        data_offset = (data[12] >> 4) * 4
        flags = data[13]
        
        flag_names = []
        if flags & 0x02: flag_names.append('SYN')
        if flags & 0x10: flag_names.append('ACK')
        if flags & 0x01: flag_names.append('FIN')
        if flags & 0x04: flag_names.append('RST')
        if flags & 0x08: flag_names.append('PSH')
        if flags & 0x20: flag_names.append('URG')
        
        return {
            'src_port': src_port,
            'dst_port': dst_port,
            'seq_num': seq_num,
            'ack_num': ack_num,
            'flags': flag_names,
            'payload': data[data_offset:]
        }
    
    def parse_udp_header(self, data: bytes) -> dict:
        """Parse UDP datagram header"""
        src_port = struct.unpack('!H', data[0:2])[0]
        dst_port = struct.unpack('!H', data[2:4])[0]
        length = struct.unpack('!H', data[4:6])[0]
        
        return {
            'src_port': src_port,
            'dst_port': dst_port,
            'length': length,
            'payload': data[8:]
        }
    
    def process_packet(self, raw_data: bytes):
        """Process captured packet through protocol stack"""
        # Ethernet
        eth = self.parse_ethernet_header(raw_data)
        
        if eth['type'] == 0x0800:  # IPv4
            ip = self.parse_ip_header(eth['payload'])
            
            packet_info = {
                'timestamp': time.time(),
                'src_ip': ip['src_ip'],
                'dst_ip': ip['dst_ip'],
                'protocol': ip['protocol'],
                'raw_data': raw_data
            }
            
            # Transport layer
            if ip['protocol'] == 6 and self.filters['tcp']:  # TCP
                tcp = self.parse_tcp_header(ip['payload'])
                packet_info.update({
                    'protocol': 'TCP',
                    'src_port': tcp['src_port'],
                    'dst_port': tcp['dst_port'],
                    'flags': tcp['flags'],
                    'payload': tcp['payload']
                })
                self.analyze_tcp_packet(packet_info)
                
            elif ip['protocol'] == 17 and self.filters['udp']:  # UDP
                udp = self.parse_udp_header(ip['payload'])
                packet_info.update({
                    'protocol': 'UDP',
                    'src_port': udp['src_port'],
                    'dst_port': udp['dst_port'],
                    'payload': udp['payload']
                })
                self.analyze_udp_packet(packet_info)
                
            elif ip['protocol'] == 1 and self.filters['icmp']:  # ICMP
                packet_info['protocol'] = 'ICMP'
                self.analyze_icmp_packet(packet_info)
                
        elif eth['type'] == 0x0806 and self.filters['arp']:  # ARP
            self.analyze_arp_packet(eth['payload'])
    
    def analyze_tcp_packet(self, packet: dict):
        """Analyze TCP packet for interesting data"""
        interesting_ports = [21, 22, 23, 25, 80, 443, 3306, 3389, 5432, 8080]
        
        if packet['src_port'] in interesting_ports or packet['dst_port'] in interesting_ports:
            print(f"\n[+] TCP {packet['src_ip']}:{packet['src_port']} -> "
                  f"{packet['dst_ip']}:{packet['dst_port']}")
            print(f"    Flags: {packet['flags']}")
            
            # HTTP analysis
            if packet['dst_port'] == 80 or packet['src_port'] == 80:
                try:
                    payload = packet['payload'].decode('utf-8', errors='ignore')
                    if 'HTTP' in payload:
                        lines = payload.split('\r\n')
                        for line in lines[:5]:
                            if line.strip():
                                print(f"    HTTP: {line[:80]}")
                        
                        # Extract credentials
                        if 'Authorization: Basic' in payload:
                            print("    [!] BASIC AUTH DETECTED")
                        if 'password=' in payload.lower():
                            print("    [!] PASSWORD IN URL")
                except:
                    pass
            
            # FTP analysis
            if packet['dst_port'] == 21 or packet['src_port'] == 21:
                try:
                    payload = packet['payload'].decode('utf-8', errors='ignore')
                    if 'USER ' in payload or 'PASS ' in payload:
                        print(f"    [!] FTP CREDENTIAL: {payload.strip()}")
                except:
                    pass
    
    def analyze_udp_packet(self, packet: dict):
        """Analyze UDP packet"""
        if packet['src_port'] == 53 or packet['dst_port'] == 53:
            print(f"\n[+] DNS Query: {packet['src_ip']} -> {packet['dst_ip']}")
            # Parse DNS query
            try:
                dns_data = packet['payload'][12:]  # Skip header
                query_len = dns_data[0]
                query = dns_data[1:1+query_len].decode()
                print(f"    Query: {query}")
            except:
                pass
    
    def analyze_icmp_packet(self, packet: dict):
        """Analyze ICMP packet"""
        print(f"\n[+] ICMP: {packet['src_ip']} -> {packet['dst_ip']}")
    
    def analyze_arp_packet(self, data: bytes):
        """Analyze ARP packet"""
        hw_type = struct.unpack('!H', data[0:2])[0]
        proto_type = struct.unpack('!H', data[2:4])[0]
        opcode = struct.unpack('!H', data[6:8])[0]
        
        sender_mac = self.mac_to_str(data[8:14])
        sender_ip = socket.inet_ntoa(data[14:18])
        target_mac = self.mac
