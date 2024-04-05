import socket
import subprocess
import logging
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure TCP server to listen for messages from other containers
def start_server():
    host = '0.0.0.0'
    port = 12345  # Port to receive messages from other containers
    backlog = 5
    buffer_size = 1024

    # Create TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(backlog)

    logging.info(f"Coordinator server listening on port {port}...")

    # Wait for messages from other containers
    message_count = 0
    n_workers = int(os.getenv('NUMBER_WORKERS', '4'))
    while message_count < n_workers:  # change this to be dynamically set based on the number of workers
        client_socket, address = server_socket.accept()
        message = client_socket.recv(buffer_size).decode()
        logging.debug(f"Received message: {message}")
        client_socket.close()
        message_count += 1

    logging.info("Received messages from all containers. Activating port 1234...")

    # Activate port 1234 (launch HTTP server, etc.)
    activate_port()

def activate_port():
    # Here you can add any command you want to execute to activate port 1234
    # For example, you could start an HTTP server using the command `python -m http.server 1234`
    try:
        subprocess.run(["python", "-m", "http.server", "1234"], check=True)
        logging.info("Port 1234 has been successfully activated.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error activating port 1234: {e}")

# Call the function to start the server and activate the port
start_server()
