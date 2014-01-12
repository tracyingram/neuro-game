import array
import socket
import time
import math

from neuro_collector import ADDRESS, PACKET


class NeuroClient(object):
    def __init__(self, device):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect(ADDRESS)
        self.device = device

    def record_sensors(self, values):
        data = PACKET.pack(math.floor(time.time() * 1000), self.device)
        values_array = array.array('d', values)
        data += values_array.tostring()
        self.socket.send(data)
