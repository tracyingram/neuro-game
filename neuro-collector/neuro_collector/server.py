import array
import SocketServer
import struct

from .recorder import record_sensors


PACKET = struct.Struct('QB')
ADDRESS = ('127.0.0.1', 6556)


class SensorDataHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data, socket = self.request
        timestamp, device = PACKET.unpack(data[:PACKET.size])
        values = array.array('d', data[PACKET.size:])
        record_sensors(timestamp, device, list(values))


def get_server():
    return SocketServer.UDPServer(ADDRESS, SensorDataHandler)


def serve_forever():
    server = get_server()
    server.serve_forever()
