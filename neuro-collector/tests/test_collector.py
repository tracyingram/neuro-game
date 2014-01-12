from mock import Mock
import time

from neuro_client import NeuroClient
from neuro_collector import server
from neuro_collector.server import get_server


def test_recording(monkeypatch):
    monkeypatch.setattr(time, 'time', Mock(return_value=9))

    record_sensors = Mock()
    monkeypatch.setattr(server, 'record_sensors', record_sensors)

    client = NeuroClient(4)
    collector = get_server()

    client.record_sensors([1, 2, 3])
    collector.handle_request()

    assert record_sensors.call_count == 1
    args, kwargs = record_sensors.call_args
    assert args == (9000, 4, [1, 2, 3])


def test_record_to_database():
    # Create test database, ensure record_sensors puts in a new row with our data
    raise NotImplementedError()
