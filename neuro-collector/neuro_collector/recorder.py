from sqlalchemy import Table, MetaData, Column, Integer, ForeignKey
from sqlalchemy.dialects.mysql import DOUBLE


metadata = MetaData()

time_steps = Table('time_steps', metadata,
    Column('id', Integer, primary_key=True),
    Column('ts', Integer),
    Column('device', Integer),
)

sensor_data = Table('sensor_data', metadata,
    Column('step_id', ForeignKey('time_steps.id'), primary_key=True),
    Column('sensor', Integer, primary_key=True),
    Column('value', DOUBLE),
)


def record_sensors(timestamp, device, values):
    # TODO: database
    print timestamp, device, values
