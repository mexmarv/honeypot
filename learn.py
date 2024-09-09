import sqlite3
import nmap
import socket
from scapy.all import sniff
import netifaces as ni
import pandas as pd

# SQLite setup
db_conn = sqlite3.connect('learned_services.db', check_same_thread=False)
db_cursor = db_conn.cursor()

# Create tables for storing learned systems and services
def initialize_db():
    db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS systems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            os_family TEXT,
            open_ports TEXT,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            service_name TEXT,
            learned_response TEXT,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db_conn.commit()

# Function to get the local subnet dynamically
def get_subnet():
    interfaces = ni.interfaces()
    for iface in interfaces:
        if iface != 'lo':  # Ignore loopback
            iface_details = ni.ifaddresses(iface)
            if ni.AF_INET in iface_details:
                ip_info = iface_details[ni.AF_INET][0]
                ip_address = ip_info['addr']
                netmask = ip_info['netmask']

                # Calculate subnet
                ip_parts = ip_address.split('.')
                mask_parts = netmask.split('.')
                subnet = '.'.join([str(int(ip_parts[i]) & int(mask_parts[i])) for i in range(4)])
                cidr = sum([bin(int(x)).count('1') for x in mask_parts])  # Count the number of '1's in the netmask
                return f"{subnet}/{cidr}"
    return None

# Function to insert/update system data
def store_system(ip, os_family, open_ports):
    db_cursor.execute('''
        INSERT INTO systems (ip, os_family, open_ports)
        VALUES (?, ?, ?)
    ''', (ip, os_family, ','.join(map(str, open_ports))))
    db_conn.commit()

# Store service data
def store_service(ip, service_name, learned_response):
    db_cursor.execute('''
        INSERT INTO services (ip, service_name, learned_response)
        VALUES (?, ?, ?)
    ''', (ip, service_name, learned_response))
    db_conn.commit()

# Network scanning with nmap
def scan_network(subnet):
    nm = nmap.PortScanner()
    nm.scan(hosts=subnet, arguments='-O')  # Scans the dynamically detected subnet
    for host in nm.all_hosts():
        if 'osclass' in nm[host]:
            os_family = nm[host]['osclass'][0]['osfamily']
        else:
            os_family = 'Unknown'
        open_ports = scan_ports(host)
        store_system(host, os_family, open_ports)

# Port scanning
def scan_ports(ip, start_port=1, end_port=1024):
    open_ports = []
    for port in range(start_port, end_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1)
        result = sock.connect_ex((ip, port))
        if result == 0:
            open_ports.append(port)
            # Simulate learned service response
            service_response = f"Fake response for {ip} on port {port}"
            store_service(ip, f"Port {port}", service_response)
        sock.close()
    return open_ports

# Packet capture using scapy
def capture_packets(interface='eth0', timeout=30):
    packets = sniff(iface=interface, timeout=timeout)
    # Store packet data or process as needed
    packets.summary()
    return packets

# Print a summary of found servers
def print_found_servers():
    db_cursor.execute('SELECT ip, service_name FROM services')
    services = db_cursor.fetchall()

    if services:
        df = pd.DataFrame(services, columns=["IP Address", "Service"])
        print("\nFound Servers:")
        print(df.to_string(index=False))
    else:
        print("No servers found.")

# Main execution
if __name__ == "__main__":
    initialize_db()

    # Dynamically get the subnet
    subnet = get_subnet()
    if subnet:
        print(f"Detected subnet: {subnet}")
        print("Scanning network and learning services...")
        scan_network(subnet)

        print("Capturing packets...")
        capture_packets()

        # Print the found servers in a table
        print_found_servers()
    else:
        print("Could not detect a valid subnet.")
