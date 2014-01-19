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
