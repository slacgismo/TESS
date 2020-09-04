import datetime
from sqlalchemy import exc
from web.extensions import db
from web.models.rate import Rate
from web.models.market import Market
from web.models.address import Address
from web.models.utility import Utility
from web.models.home_hub import HomeHub
from web.models.hce_bids import HceBids
from web.models.meter import Meter, MeterType
from web.models.transformer import Transformer
from web.models.meter_interval import MeterInterval
from web.models.market_interval import MarketInterval
from web.models.service_location import ServiceLocation


def seed():
    try:
        transformer = Transformer(
            transformer_id=1,
            feeder='feeder_one',
            capacity=1,
        )
        db.session.add(transformer)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('transformer already exists')

    try:
        addr = Address(address_id=1,
                       address='asdfasdf',
                       city='RWC',
                       country='USA',
                       postal_code='94065')
        db.session.add(addr)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('address already exists')

    try:
        sl = ServiceLocation(service_location_id=1,
                             alternate_service_location_id='1234asdf',
                             address_id=1,
                             map_location='RWC',
                             is_active=True,
                             is_archived=False)
        db.session.add(sl)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('service location already exists')

    try:
        market = Market(market_id=1,
                        source='asdf',
                        ts=1.0,
                        p_max=1.0,
                        is_active=True,
                        is_archived=False)
        db.session.add(market)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('market already exists')

    try:
        hh = HomeHub(home_hub_id=1,
                     service_location_id=1,
                     market_id=1,
                     is_active=True,
                     is_archived=False)
        db.session.add(hh)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('home hub already exists')

    try:
        util = Utility(utility_id=1,
                       name='utilName',
                       subscription_start=datetime.datetime.now(),
                       subscription_end=datetime.datetime.now())
        db.session.add(util)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('utility already exists')

    try:
        meter = Meter(meter_id=1,
                      utility_id=1,
                      service_location_id=1,
                      home_hub_id=1,
                      transformer_id=1,
                      alternate_meter_id=1,
                      feeder='asdf',
                      substation='asdf',
                      meter_type=MeterType.COMMERCIAL,
                      is_active=True,
                      is_archived=False)
        db.session.add(meter)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('meter already exists')

    try:
        rate = Rate(rate_id=1, description='rate one')
        db.session.add(rate)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('rate already exists')

    try:
        mi = MeterInterval(
            meter_interval_id=1,
            meter_id=1,
            rate_id=1,
            start_time=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            end_time=datetime.datetime.fromisoformat('2020-01-01T00:05:23'),
            e=1.0,
            qmtp=1.0,
            p_bid=1.0,
            q_bid=1.0,
            mode=0,
            is_bid=True)
        db.session.add(mi)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('meter interval already exists')

    try:
        mai = MarketInterval(
            market_interval_id=1,
            market_id=1,
            p_exp=1.0,
            p_dev=1.0,
            p_clear=1.0,
            q_clear=1.0,
            alpha=1.0,
            start_time=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            end_time=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
        db.session.add(mai)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('market interval already exists')

    try:
        hceb = HceBids(
            bid_id=1,
            start_time=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            end_time=datetime.datetime.fromisoformat('2020-01-01T00:05:23'),
            comment='asdfasdf',
            market_id=1)
        db.session.add(hceb)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('hce bids already exists')
