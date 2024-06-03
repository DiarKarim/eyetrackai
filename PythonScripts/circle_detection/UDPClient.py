# This is for when we transmit the coordinates to the motor! Diar mentioned using UDP so why not try something out?

import socket
import pickle

class UDPClient:
    def __init__(self, udp_ip, udp_port) -> None:
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def send_coordinates(self, coordinates):
        data = pickle.dumps(coordinates) # Serialises the data into a byte stream to send over to the arduino
        self.socket.sendto(data, (self.udp_ip, self.udp_port)) # Sends the byte stream