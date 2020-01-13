# coding: utf-8
from sqlalchemy import Column, Enum, Float, ForeignKey, Index, String, TIMESTAMP, Table, Text, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Log(Base):
    __tablename__ = 'log'

    log_id = Column(INTEGER(11), primary_key=True)
    message = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False, index=True, server_default=text("CURRENT_TIMESTAMP"))


t_order_state = Table(
    'order_state', metadata,
    Column('order_id', INTEGER(11), server_default=text("'0'")),
    Column('device_id', INTEGER(11)),
    Column('unique_id', String(32)),
    Column('resource_id', INTEGER(11)),
    Column('quantity', Float(asdecimal=True)),
    Column('bid', Float(asdecimal=True)),
    Column('current', Float(asdecimal=True)),
    Column('duration', Float(asdecimal=True)),
    Column('created', TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")),
    Column('price_id', INTEGER(11)),
    Column('closed', TIMESTAMP),
    Column('state', String(7))
)


t_order_status = Table(
    'order_status', metadata,
    Column('order_id', INTEGER(11), server_default=text("'0'")),
    Column('device_id', INTEGER(11)),
    Column('unique_id', String(32)),
    Column('resource_id', INTEGER(11)),
    Column('quantity', Float(asdecimal=True)),
    Column('bid', Float(asdecimal=True)),
    Column('current', Float(asdecimal=True)),
    Column('duration', Float(asdecimal=True)),
    Column('created', TIMESTAMP, server_default=text("'0000-00-00 00:00:00'")),
    Column('price_id', INTEGER(11)),
    Column('closed', TIMESTAMP),
    Column('state', String(7)),
    Column('status', INTEGER(1)),
    Column('margin', Float(asdecimal=True))
)


class System(Base):
    __tablename__ = 'system'

    system_id = Column(INTEGER(11), primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class Config(Base):
    __tablename__ = 'config'

    config_id = Column(INTEGER(11), primary_key=True)
    system_id = Column(ForeignKey('system.system_id', ondelete='CASCADE', onupdate='RESTRICT'), nullable=False, index=True)
    name = Column(String(32), nullable=False)
    value = Column(Text)
    created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    system = relationship('System')


class Resource(Base):
    __tablename__ = 'resource'

    resource_id = Column(INTEGER(11), primary_key=True)
    system_id = Column(ForeignKey('system.system_id', ondelete='CASCADE', onupdate='RESTRICT'), nullable=False, index=True)
    name = Column(String(32), nullable=False)
    quantity_unit = Column(Text, nullable=False)
    price_unit = Column(Text, nullable=False)
    created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    system = relationship('System')


class User(Base):
    __tablename__ = 'user'

    user_id = Column(INTEGER(11), primary_key=True)
    system_id = Column(ForeignKey('system.system_id', ondelete='CASCADE', onupdate='RESTRICT'), nullable=False, index=True)
    name = Column(String(32), nullable=False)
    role = Column(Enum('ADMINISTRATOR', 'OPERATOR', 'ACCOUNTING', 'CUSTOMER', 'TEST'), nullable=False)
    email = Column(Text, nullable=False)
    sha1pwd = Column(Text)
    created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    system = relationship('System')


class Device(Base):
    __tablename__ = 'device'

    device_id = Column(INTEGER(11), primary_key=True)
    user_id = Column(ForeignKey('user.user_id', ondelete='CASCADE', onupdate='RESTRICT'), nullable=False, index=True)
    name = Column(String(32), nullable=False)
    unique_id = Column(String(32), nullable=False, unique=True)
    created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship('User')


class Preference(Base):
    __tablename__ = 'preference'

    preference_id = Column(INTEGER(11), primary_key=True)
    user_id = Column(ForeignKey('user.user_id', ondelete='CASCADE', onupdate='RESTRICT'), nullable=False, index=True)
    name = Column(String(32), nullable=False)
    value = Column(Text)
    created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship('User')


class Price(Base):
    __tablename__ = 'price'

    price_id = Column(INTEGER(11), primary_key=True)
    resource_id = Column(ForeignKey('resource.resource_id', ondelete='CASCADE', onupdate='RESTRICT'), nullable=False, index=True)
    price = Column(Float(asdecimal=True), nullable=False)
    quantity = Column(Float(asdecimal=True), nullable=False)
    margin = Column(Float(asdecimal=True))
    created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    resource = relationship('Resource')


class Token(Base):
    __tablename__ = 'token'
    __table_args__ = (
        Index('i_token_userid_created', 'user_id', 'created'),
    )

    token_id = Column(INTEGER(11), primary_key=True)
    user_id = Column(ForeignKey('user.user_id', ondelete='CASCADE', onupdate='RESTRICT'))
    unique_id = Column(String(32), nullable=False, unique=True)
    is_valid = Column(Enum('False', 'True'), server_default=text("'True'"))
    created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship('User')


class Meter(Base):
    __tablename__ = 'meter'
    __table_args__ = (
        Index('u_meter_deviceid_priceid_created', 'device_id', 'price_id', 'created', unique=True),
    )

    meter_id = Column(INTEGER(11), primary_key=True)
    device_id = Column(ForeignKey('device.device_id', ondelete='CASCADE', onupdate='RESTRICT'), nullable=False)
    price_id = Column(ForeignKey('price.price_id', ondelete='CASCADE', onupdate='RESTRICT'), nullable=False, index=True)
    quantity = Column(Float(asdecimal=True), nullable=False, comment='produce<0, consume>0, =0 is invalid')
    created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    device = relationship('Device')
    price = relationship('Price')


class Order(Base):
    __tablename__ = 'order'

    order_id = Column(INTEGER(11), primary_key=True)
    device_id = Column(ForeignKey('device.device_id', ondelete='CASCADE', onupdate='RESTRICT'), nullable=False, index=True)
    unique_id = Column(String(32), nullable=False, unique=True)
    resource_id = Column(ForeignKey('resource.resource_id', ondelete='CASCADE', onupdate='RESTRICT'), nullable=False, index=True)
    quantity = Column(Float(asdecimal=True), nullable=False, comment='ask/sell<0, offer/buy>0, =0 is invalid')
    bid = Column(Float(asdecimal=True), comment='<0 is invalid')
    current = Column(Float(asdecimal=True), comment='NULL if current=quantity')
    duration = Column(Float(asdecimal=True), comment='only used for orderbook mechanism')
    created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    price_id = Column(ForeignKey('price.price_id', ondelete='CASCADE', onupdate='RESTRICT'), index=True)
    closed = Column(TIMESTAMP)

    device = relationship('Device')
    price = relationship('Price')
    resource = relationship('Resource')


class Setting(Base):
    __tablename__ = 'setting'

    setting_id = Column(INTEGER(11), primary_key=True)
    device_id = Column(ForeignKey('device.device_id', ondelete='CASCADE', onupdate='RESTRICT'), nullable=False, index=True)
    name = Column(String(32), nullable=False)
    value = Column(Text)
    created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    device = relationship('Device')


class Transaction(Base):
    __tablename__ = 'transaction'

    transaction_id = Column(INTEGER(11), primary_key=True)
    meter_id = Column(ForeignKey('meter.meter_id', ondelete='CASCADE', onupdate='RESTRICT'), index=True)
    amount = Column(Float(asdecimal=True))
    balance = Column(Float(asdecimal=True))
    created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    meter = relationship('Meter')
