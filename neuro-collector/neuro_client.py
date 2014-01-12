import math
import socket
import time

from neuro_collector import ADDRESS, pack_step


class NeuroClient(object):
    def __init__(self, device):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect(ADDRESS)
        self.device = device

    def record_sensors(self, sensors):
        self.socket.send(pack_step(math.floor(time.time() * 1000),
                                   self.device, sensors))
