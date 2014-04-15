import os
import SocketServer
import struct
from datetime import datetime
from threading import Thread

from neuro_collector.recorder import (record_sensors, export_data, init_db,
                                      reset_db)


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

    init_db()

    def exporter():
        while True:
            try:
                print datetime.now()
                name = raw_input('Type a name and press Enter to export '
                                 '(leave blank to restart recording): ').strip()
                if name:
                    filename = name + '.xls'
                    if export_data(filename):
                        print 'Saved to', filename
                    else:
                        print 'No data to save!'

                reset_db()
                print 'Reset database'
                print
            except (KeyboardInterrupt, SystemExit, EOFError):
                print 'Quitting...'
                os._exit(0)

    _export_thread = Thread(target=exporter)
    _export_thread.daemon = True
    _export_thread.start()

    server = get_server()
    server.serve_forever()
