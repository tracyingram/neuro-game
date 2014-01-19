import SocketServer
import struct

from .recorder import record_sensors


HEADER = struct.Struct('QB')
ADDRESS = ('127.0.0.1', 6556)


def pack_step(timestamp, device, sensors):
    header = HEADER.pack(timestamp, device)
    pieces = []
    for sensor, value in sensors.iteritems():
        pieces.append('\0'.join((sensor, struct.pack('f', value))))
    return header + ''.join(pieces)


def unpack_step(data):
    timestamp, device = HEADER.unpack(data[:HEADER.size])

    sensors = {}
    i = HEADER.size
    value_size = struct.calcsize('f')
    while i < len(data):
        sensor_length = data[i:].index('\0')
        sensor = data[i:i + sensor_length]
        i += sensor_length + 1
        value, = struct.unpack('f', data[i:i + value_size])
        i += value_size

        sensors[sensor] = value

    return timestamp, device, sensors


class SensorDataHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data, socket = self.request
        timestamp, device, sensors = unpack_step(data)
        record_sensors(timestamp, device, sensors)


def get_server():
    return SocketServer.UDPServer(ADDRESS, SensorDataHandler)


if __name__ == '__main__':
    print 'Serving on {}:{}'.format(*ADDRESS)

    server = get_server()
    server.serve_forever()
