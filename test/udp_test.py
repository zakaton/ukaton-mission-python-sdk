import socket
import time
import threading

# Server details
SERVER_IP = '192.168.1.30'  # Replace with the IP address of the remote UDP server
SERVER_PORT = 9999  # Replace with the port number of the remote UDP server

# Local details
LOCAL_IP = '0.0.0.0'  # Bind to all available network interfaces
LOCAL_PORT = 5005  # Replace with the desired local port number

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LOCAL_IP, LOCAL_PORT))

# Function to send messages


def send_message(message):
    print('sending message')
    sock.sendto(message.encode(), (SERVER_IP, SERVER_PORT))

# Function to receive messages


def receive_messages():
    while True:
        data, addr = sock.recvfrom(1024)
        print(f'Received message from {addr[0]}:{addr[1]}: {data.decode()}')


# Thread to receive messages without blocking
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

# Main loop to send ping messages every second
while True:
    # Sending a ping message with a single byte of value 0
    send_message(chr(4))
    time.sleep(1)
