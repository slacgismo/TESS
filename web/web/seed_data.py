import datetime
from sqlalchemy import exc
from web.extensions import db
from web.models.rate import Rate
from web.models.user import User
from web.models.alert import Alert
from web.models.market import Market
from web.models.address import Address
from web.models.utility import Utility
from web.models.home_hub import HomeHub
from web.models.hce_bids import HceBids
from web.models.alert_type import AlertType
from web.models.meter import Meter, MeterType
from web.models.transformer import Transformer
from web.models.notification import Notification
from web.models.meter_interval import MeterInterval
from web.models.market_interval import MarketInterval
from web.models.transformer_interval import TransformerInterval
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
            mode_market=0,
            mode_dispatch=0,
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

    try:
        tri = TransformerInterval(
            transformer_interval_id=1,
            transformer_id=1,
            import_capacity=1.0,
            export_capacity=1.0,
            q=1.0,
            start_time=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            end_time=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
        db.session.add(tri)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('transformer interval already exists')

    try:
        at = AlertType(
            alert_type_id=1,
            utility_id=1,
            name='YELLOW_ALARM_LOAD',
            limit=1.0,
            updated_at=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            created_at=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
        db.session.add(at)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('alert type already exists')

    try:
        at = AlertType(
            alert_type_id=2,
            utility_id=1,
            name='RED_ALARM_LOAD',
            limit=3.0,
            updated_at=datetime.datetime.fromisoformat('2020-01-01T00:05:32'),
            created_at=datetime.datetime.fromisoformat('2020-01-01T00:05:35'))
        db.session.add(at)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('alert type already exists')

    try:
        at = AlertType(
            alert_type_id=3,
            utility_id=1,
            name='YELLOW_ALARM_PRICE',
            limit=3.0,
            updated_at=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            created_at=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
        db.session.add(at)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('alert type already exists')

    try:
        at = AlertType(
            alert_type_id=4,
            utility_id=1,
            name='RED_ALARM_PRICE',
            limit=3.0,
            updated_at=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            created_at=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
        db.session.add(at)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('alert type already exists')

    try:
        at = AlertType(
            alert_type_id=5,
            utility_id=1,
            name='PRICE_ALERT',
            limit=3.0,
            updated_at=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            created_at=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
        db.session.add(at)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('alert type already exists')

    try:
        at = AlertType(
            alert_type_id=6,
            utility_id=1,
            name='IMPORT_CAPACITY',
            limit=3.0,
            updated_at=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            created_at=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
        db.session.add(at)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('alert type already exists')

    try:
        at = AlertType(
            alert_type_id=7,
            utility_id=1,
            name='EXPORT_CAPACITY',
            limit=3.0,
            updated_at=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            created_at=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
        db.session.add(at)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('alert type already exists')

    try:
        at = AlertType(
            alert_type_id=8,
            utility_id=1,
            name='RESOURCE_DEPLETION',
            limit=3.0,
            updated_at=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            created_at=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
        db.session.add(at)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('alert type already exists')

    try:
        at = AlertType(
            alert_type_id=9,
            utility_id=1,
            name='TELECOMM_ALERT',
            limit=3.0,
            updated_at=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            created_at=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
        db.session.add(at)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('alert type already exists')

    try:
        at = AlertType(
            alert_type_id=10,
            utility_id=1,
            name='PEAK_EVENT',
            limit=3.0,
            updated_at=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            created_at=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
        db.session.add(at)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('alert type already exists')

    try:
        user = User(
            id=1,
            email='test@test.com',
            email_confirmed_at=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            first_name='fname',
            last_name='lname',
            address_id=1,
            utility_id=1,
            updated_at=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            created_at=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
        db.session.add(user)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('user already exists')

    try:
        alert = Alert(
            alert_id=1,
            alert_type_id=1,
            assigned_to='test@test.com',
            description='sdjfd',
            status='open',
            context='feeder',
            context_id='1',
            resolution = 'fdjgh')
        db.session.add(alert)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('alert already exists')

    try:
        alert = Alert(
            alert_id=2,
            alert_type_id=1,
            assigned_to='test@test.com',
            description='sdjfd',
            status='open',
            context='feeder',
            context_id='1',
            resolution='fdjgh')
        db.session.add(alert)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('alert already exists')

    try:
        notification = Notification(
            notification_id=1,
            alert_type_id=1,
            email="test@test.com",
            is_active=False,
            created_by=1,
            updated_at=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            created_at=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
        db.session.add(notification)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('notification already exists')

    try:
        notification = Notification(
            notification_id=2,
            alert_type_id=1,
            email="test@test.com",
            is_active=False,
            created_by=1,
            updated_at=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            created_at=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
        db.session.add(notification)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('notification already exists')
