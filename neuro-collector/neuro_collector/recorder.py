from sqlalchemy import (Column, Integer, ForeignKey, create_engine, Float,
                        String)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (scoped_session, create_session, relationship,
                            backref)

try:
    from . import settings
except ImportError:
    raise Exception('No settings.py config file found. Please copy the '
                    'settings.py.example file to "settings.py" and edit the '
                    'DATABASE_URI to match your setup.')


Base = declarative_base()

class TimeStep(Base):
    __tablename__ = 'time_steps'

    id = Column('id', Integer, primary_key=True)
    ts = Column('ts', Integer)
    device = Column('device', Integer)


class SensorValue(Base):
    __tablename__ = 'sensor_values'

    step_id = Column('step_id', ForeignKey('time_steps.id'), primary_key=True)
    sensor = Column('sensor', String(), primary_key=True)
    value = Column('value', Float)

    step = relationship(TimeStep, backref=backref('values', lazy='joined'))


class Record(Base):
    __tablename__ = 'records'

    id = Column('id', Integer, primary_key=True)
    ts = Column('ts', Float)

    sensor0 = Column('sensor0', Float)
    sensor1 = Column('sensor1', Float)
    sensor2 = Column('sensor2', Float)
    sensor3 = Column('sensor3', Float)
    sensor4 = Column('sensor4', Float)
    sensor5 = Column('sensor5', Float)
    sensor6 = Column('sensor6', Float)
    sensor7 = Column('sensor7', Float)
    sensor8 = Column('sensor8', Float)
    sensor9 = Column('sensor9', Float)
    sensor10 = Column('sensor10', Float)
    sensor11 = Column('sensor11', Float)
    sensor12 = Column('sensor12', Float)
    sensor13 = Column('sensor13', Float)
    sensor14 = Column('sensor14', Float)
    sensor15 = Column('sensor15', Float)
    sensor16 = Column('sensor16', Float)
    sensor17 = Column('sensor17', Float)
    sensor18 = Column('sensor18', Float)
    sensor19 = Column('sensor19', Float)


engine = None
db_session = scoped_session(lambda: create_session(bind=engine))


def init_db():
    global engine
    engine = create_engine(settings.DATABASE_URI)
    Base.metadata.create_all(bind=engine)


def record_sensors(timestamp, device, sensors):
    if engine is None:
        init_db()

    session = db_session()
    step = TimeStep(ts=timestamp, device=device)
    session.add(step)

    for sensor, value in sensors.iteritems():
        session.add(SensorValue(step=step, sensor=sensor, value=value))

    session.flush()
