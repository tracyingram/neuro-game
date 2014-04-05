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
    timestamp, device, sensors = 1, 'poop', {'a': 1, 'b': 2}
    assert (unpack_step(pack_step(timestamp, device, sensors)) ==
            (timestamp, device, sensors))


def test_recording(monkeypatch):
    monkeypatch.setattr(time, 'time', Mock(return_value=9))

    record_sensors = Mock()
    monkeypatch.setattr(server, 'record_sensors', record_sensors)

    client = NeuroClient('taco')
    collector = get_server()

    client.record_sensors({'a': 1, 'b': 2, 'c': 3})
    collector.handle_request()

    assert record_sensors.call_count == 1
    args, kwargs = record_sensors.call_args
    assert args == (9000, 'taco', {'a': 1, 'b': 2, 'c': 3})


@pytest.mark.usefixtures('db')
def test_record_to_database():
    session = recorder.db_session()

    assert session.query(recorder.Record).count() == 0

    recorder.record_sensors(1, 'apples', {'a': 3, 'b': 4})

    assert session.query(recorder.Record).count() == 1

    record = session.query(recorder.Record).first()
    assert record.ts == 1
    assert record.device == 'apples'
    assert record.sensor0 == 3
    assert record.sensor1 == 4

    header = session.query(recorder.Header).first()
    assert header.device == 'apples'
    assert header.columns == '"a","b"'
