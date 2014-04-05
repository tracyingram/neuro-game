import SocketServer
import struct

from .recorder import record_sensors


TIMESTAMP = struct.Struct('Q')
ADDRESS = ('127.0.0.1', 6556)


def pack_step(timestamp, device, sensors):
    header = TIMESTAMP.pack(timestamp) + device + '\0'
    pieces = []
    for sensor, value in sensors.iteritems():
        pieces.append('{}\0{}\0'.format(sensor, value))
    return header + ''.join(pieces)


def unpack_step(data):
    timestamp, = TIMESTAMP.unpack(data[:TIMESTAMP.size])

    i = TIMESTAMP.size
    device_length = data[i:].index('\0')
    device = data[i:i + device_length]

    i += device_length + 1

    sensors = {}
    while i < len(data):
        sensor_length = data[i:].index('\0')
        sensor = data[i:i + sensor_length]
        i += sensor_length + 1

        value_length = data[i:].index('\0')
        value = data[i:i + value_length]
        i += value_length + 1

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
