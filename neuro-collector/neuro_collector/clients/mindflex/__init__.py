import gevent
import serial

from ...client import NeuroClient


tickrate = 64
tick = 1.00 / tickrate

DEVICE_PATH = '/dev/ttyACM0'

SENSORS = [
     'Signal Strength',
     'Attention',
     'Meditation',
     'Delta',
     'Theta',
     'Low Alpha',
     'High Alpha',
     'Low Beta',
     'High Beta',
     'Low Gamma',
     'High Gamma',
]


if __name__ == '__main__':
    client = NeuroClient('mindflex')
    comm = serial.Serial(DEVICE_PATH)

    while True:
        csv = comm.readline()
        if not csv:
            continue

        str_data = csv.split(',')
        if len(str_data) != len(SENSORS):
            continue

        data = map(float, str_data)
        sensors = dict(zip(SENSORS, data))

        client.record_sensors(sensors)

        gevent.sleep(tick)
