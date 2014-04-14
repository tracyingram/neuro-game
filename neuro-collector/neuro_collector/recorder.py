import xlwt
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
    device = Column('device', String(32))


class SensorValue(Base):
    __tablename__ = 'sensor_values'

    step_id = Column('step_id', ForeignKey('time_steps.id'), primary_key=True)
    sensor = Column('sensor', String(32), primary_key=True)
    value = Column('value', String(512))

    step = relationship(TimeStep, backref=backref('values', lazy='joined'))


engine = None
db_session = scoped_session(lambda: create_session(bind=engine))


def init_db():
    global engine
    engine = create_engine(settings.DATABASE_URI)
    Base.metadata.create_all(bind=engine)


def export_data(name='export.xls'):
    session = db_session()
    book = xlwt.Workbook()

    # Names of all devices in database
    devices = zip(*list(session.query(TimeStep.device).distinct()))[0]
    for device in devices:
        sheet = book.add_sheet(device)

        # Names of all sensors recorded, to build dedicated columns for each
        sensors = zip(*list(session.query(SensorValue.sensor)
                                   .join(TimeStep)
                                   .filter(TimeStep.device == device)
                                   .distinct()))[0]

        # Records the rows we'll later write to the spreadsheet
        # First row is the header
        rows = [('Timestamp',) + sensors]

        time_steps = (session.query(TimeStep).filter(TimeStep.device == device)
                                             .order_by(TimeStep.ts.asc())
                                             .values(TimeStep.id, TimeStep.ts))
        for step_id, timestamp in time_steps:
            values = dict(session.query(SensorValue)
                                 .filter(SensorValue.step_id == step_id)
                                 .values(SensorValue.sensor, SensorValue.value))
            rows.append([timestamp] + [values.get(s, '') for s in sensors])

        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                sheet.write(r, c, value)

    book.save(name)


def record_sensors(timestamp, device, sensors):
    if engine is None:
        init_db()

    session = db_session()
    step = TimeStep(ts=timestamp, device=device)
    session.add(step)

    for sensor, value in sensors.iteritems():
        session.add(SensorValue(step=step, sensor=sensor, value=value))

    session.flush()
