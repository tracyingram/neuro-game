import time

import pytest
from mock import Mock
from sqlalchemy import create_engine

from neuro_collector.client import NeuroClient
from neuro_collector import server, recorder
from neuro_collector.server import get_server, pack_step, unpack_step


@pytest.fixture
def db(monkeypatch):
    engine = create_engine('sqlite:///:memory:')
    recorder.Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(recorder, 'engine', engine)


def test_packing_and_unpacking():
    timestamp, device, sensors = 1, 2, {'a': 1, 'b': 2}
    assert (unpack_step(pack_step(timestamp, device, sensors)) ==
            (timestamp, device, sensors))


def test_recording(monkeypatch):
    monkeypatch.setattr(time, 'time', Mock(return_value=9))

    record_sensors = Mock()
    monkeypatch.setattr(server, 'record_sensors', record_sensors)

    client = NeuroClient(4)
    collector = get_server()

    client.record_sensors({'a': 1, 'b': 2, 'c': 3})
    collector.handle_request()

    assert record_sensors.call_count == 1
    args, kwargs = record_sensors.call_args
    assert args == (9000, 4, {'a': 1, 'b': 2, 'c': 3})


@pytest.mark.usefixtures('db')
def test_record_to_database():
    session = recorder.db_session()

    assert session.query(recorder.TimeStep).count() == 0
    assert session.query(recorder.SensorValue).count() == 0

    recorder.record_sensors(1, 2, {'a': 3, 'b': 4})

    assert session.query(recorder.TimeStep).count() == 1
    assert session.query(recorder.SensorValue).count() == 2

    time_step = session.query(recorder.TimeStep).first()
    assert time_step.ts == 1
    assert time_step.device == 2

    sensor_values = session.query(recorder.SensorValue).all()
    assert sensor_values[0].step_id == sensor_values[1].step_id == time_step.id

    assert sensor_values[0].sensor == 'a'
    assert sensor_values[0].value == 3

    assert sensor_values[1].sensor == 'b'
    assert sensor_values[1].value == 4
