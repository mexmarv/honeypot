import sqlite3
import threading
from flask import Flask, request
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import smtplib
import socket

# SQLite setup
db_conn = sqlite3.connect('learned_services.db', check_same_thread=False)
db_cursor = db_conn.cursor()

# Function to simulate HTTP service for a specific IP
def run_http_service(ip):
    app = Flask(__name__)

    @app.route('/')
    def fake_http_service():
        db_cursor.execute("SELECT learned_response FROM services WHERE ip=? AND service_name LIKE 'Port 80%'", (ip,))
        http_response = db_cursor.fetchone()
        if http_response:
            return f"<html><body>{http_response[0]}</body></html>"
        else:
            return "<html><body>Default HTTP response</body></html>"

    print(f"Starting HTTP service for {ip} on port 80...")
    app.run(host=ip, port=80, debug=False, use_reloader=False)

# Function to simulate SSH service for a specific IP
def ssh_simulation(ip):
    print(f"Starting SSH service for {ip}...")
    while True:
        command = input(f"SSH Command for {ip}: ")
        db_cursor.execute("SELECT learned_response FROM services WHERE ip=? AND service_name LIKE 'Port 22%'", (ip,))
        ssh_response = db_cursor.fetchone()
        if command.lower() == "exit":
            print(f"SSH Connection closed for {ip}.")
            break
        elif ssh_response:
            print(f"SSH Response for {ip}: {ssh_response[0]}")
        else:
            print("Default SSH response")

# Function to simulate FTP service for a specific IP
def ftp_simulation(ip):
    authorizer = DummyAuthorizer()
    authorizer.add_user("user", "12345", "/", perm="elradfmw")
    handler = FTPHandler
    handler.authorizer = authorizer
    server = FTPServer((ip, 21), handler)
    print(f"Starting FTP service for {ip} on port 21...")
    server.serve_forever()

# Function to simulate SMTP service for a specific IP
def smtp_simulation(ip):
    try:
        smtp_server = smtplib.SMTP(ip, 1025)
        smtp_server.sendmail("from@example.com", "to@example.com", "Fake SMTP message.")
        print(f"SMTP Simulation Sent from {ip}.")
    except Exception as e:
        print(f"SMTP Error for {ip}: {e}")

# Function to simulate multiple services for a specific IP
def simulate_services_for_ip(ip):
    # Simulate HTTP service
    threading.Thread(target=run_http_service, args=(ip,)).start()

    # Simulate SSH service
    threading.Thread(target=ssh_simulation, args=(ip,)).start()

    # Simulate FTP service
    threading.Thread(target=ftp_simulation, args=(ip,)).start()

    # Simulate SMTP service
    threading.Thread(target=smtp_simulation, args=(ip,)).start()

# Main function to read learned IPs and start simulation for each one
def simulate_learned_devices():
    db_cursor.execute("SELECT DISTINCT ip FROM services")
    learned_ips = db_cursor.fetchall()
    for ip_record in learned_ips:
        ip = ip_record[0]
        print(f"Simulating services for learned IP: {ip}")
        simulate_services_for_ip(ip)

# Start simulation
if __name__ == "__main__":
    simulate_learned_devices()
