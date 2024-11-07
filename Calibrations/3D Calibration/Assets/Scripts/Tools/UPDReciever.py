import socket

# Set up the server
server_ip = "127.0.0.1"
server_port = 8000
buffer_size = 1024

# Create a UDP socket
udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server_socket.bind((server_ip, server_port))

print(f"UDP server up and listening on {server_ip}:{server_port}")

# Listen for incoming datagrams
while True:
    bytes_address_pair = udp_server_socket.recvfrom(buffer_size)
    message = bytes_address_pair[0]
    client_msg = message.decode("utf-8")
    
    print(client_msg)

