import gevent

from . import emotiv
from ..devices import DEVICES
from ...client import NeuroClient


tickrate = 64
tick = 1.00 / tickrate


if __name__ == '__main__':
    client = NeuroClient(DEVICES['emotiv'])

    headset = emotiv.Emotiv()
    gevent.spawn(headset.setup)
    gevent.sleep(1)

    try:
        while True:
            packet = headset.dequeue()

            data = {}
            for sensor, info in packet.sensors.items():
                data[sensor + ' Quality'] = info['quality']
                data[sensor + ' Value'] = info['value']

            client.record_sensors(data)

            gevent.sleep(tick)
    except KeyboardInterrupt:
        headset.close()
    finally:
        headset.close()
