import datetime
from sqlalchemy import exc
from web.extensions import db
from web.models.pv import Pv
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
    # transformer
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

    # addresses
    try:
        addr = Address(address_id=1,
                       address='Main Street 1',
                       city='Aspen',
                       country='USA',
                       postal_code='00000')
        db.session.add(addr)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('address already exists')

    try:
        addr = Address(address_id=2,
                       address='Main Street 2',
                       city='Aspen',
                       country='USA',
                       postal_code='00000')
        db.session.add(addr)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('address already exists')

    try:
        addr = Address(address_id=3,
                       address='Main Street 3',
                       city='Aspen',
                       country='USA',
                       postal_code='00000')
        db.session.add(addr)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('address already exists')

    try:
        addr = Address(address_id=4,
                       address='Main Street 4',
                       city='Aspen',
                       country='USA',
                       postal_code='00000')
        db.session.add(addr)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('address already exists')

    try:
        addr = Address(address_id=5,
                       address='Main Street 5',
                       city='Aspen',
                       country='USA',
                       postal_code='00000')
        db.session.add(addr)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('address already exists')

    try:
        addr = Address(address_id=6,
                       address='Main Street 6',
                       city='Aspen',
                       country='USA',
                       postal_code='00000')
        db.session.add(addr)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('address already exists')

    # service_locations
    try:
        sl = ServiceLocation(service_location_id=1,
                             address_id=1,
                             map_location='somewhere',
                             is_active=False,
                             is_archived=False)
        db.session.add(sl)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('service location already exists')

    try:
        sl = ServiceLocation(service_location_id=2,
                             address_id=2,
                             map_location='somewhere',
                             is_active=False,
                             is_archived=False)
        db.session.add(sl)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('service location already exists')

    try:
        sl = ServiceLocation(service_location_id=3,
                             address_id=3,
                             map_location='somewhere',
                             is_active=False,
                             is_archived=False)
        db.session.add(sl)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('service location already exists')

    try:
        sl = ServiceLocation(service_location_id=4,
                             address_id=4,
                             map_location='somewhere',
                             is_active=False,
                             is_archived=False)
        db.session.add(sl)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('service location already exists')

    try:
        sl = ServiceLocation(service_location_id=5,
                             address_id=5,
                             map_location='somewhere',
                             is_active=False,
                             is_archived=False)
        db.session.add(sl)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('service location already exists')

    try:
        sl = ServiceLocation(service_location_id=6,
                             address_id=6,
                             map_location='somewhere',
                             is_active=False,
                             is_archived=False)
        db.session.add(sl)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('service location already exists')

    # market
    try:
        market = Market(market_id=1,
                        source='Ercot',
                        ts=300.0,
                        p_max=10000.0,
                        is_active=False,
                        is_archived=False)
        db.session.add(market)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('market already exists')

    # home_hubs
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
        hh = HomeHub(home_hub_id=2,
                     service_location_id=2,
                     market_id=1,
                     is_active=True,
                     is_archived=False)
        db.session.add(hh)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('home hub already exists')

    try:
        hh = HomeHub(home_hub_id=3,
                     service_location_id=3,
                     market_id=1,
                     is_active=True,
                     is_archived=False)
        db.session.add(hh)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('home hub already exists')

    try:
        hh = HomeHub(home_hub_id=4,
                     service_location_id=4,
                     market_id=1,
                     is_active=True,
                     is_archived=False)
        db.session.add(hh)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('home hub already exists')

    try:
        hh = HomeHub(home_hub_id=5,
                     service_location_id=5,
                     market_id=1,
                     is_active=True,
                     is_archived=False)
        db.session.add(hh)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('home hub already exists')

    try:
        hh = HomeHub(home_hub_id=6,
                     service_location_id=6,
                     market_id=1,
                     is_active=True,
                     is_archived=False)
        db.session.add(hh)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('home hub already exists')

    # utility
    try:
        util = Utility(utility_id=1,
                       name='HCE',
                       subscription_start=datetime.datetime.now(),
                       subscription_end=datetime.datetime.now())
        db.session.add(util)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('utility already exists')

    # meter
    try:
        meter = Meter(meter_id=1,
                      utility_id=1,
                      service_location_id=1,
                      home_hub_id=1,
                      transformer_id=1,
                      alternate_meter_id=1,
                      feeder='IEEE123',
                      substation='HCE-Xcel',
                      meter_type=MeterType.RESIDENTIAL,
                      is_active=False,
                      is_archived=False)
        db.session.add(meter)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('meter already exists')

    try:
        meter = Meter(meter_id=2,
                      utility_id=1,
                      service_location_id=2,
                      home_hub_id=2,
                      transformer_id=1,
                      feeder='IEEE123',
                      substation='HCE-Xcel',
                      meter_type=MeterType.RESIDENTIAL,
                      is_active=False,
                      is_archived=False)
        db.session.add(meter)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('meter already exists')

    try:
        meter = Meter(meter_id=3,
                      utility_id=1,
                      service_location_id=3,
                      home_hub_id=3,
                      transformer_id=1,
                      feeder='IEEE123',
                      substation='HCE-Xcel',
                      meter_type=MeterType.RESIDENTIAL,
                      is_active=False,
                      is_archived=False)
        db.session.add(meter)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('meter already exists')

    try:
        meter = Meter(meter_id=4,
                      utility_id=1,
                      service_location_id=4,
                      home_hub_id=4,
                      transformer_id=1,
                      feeder='IEEE123',
                      substation='HCE-Xcel',
                      meter_type=MeterType.RESIDENTIAL,
                      is_active=False,
                      is_archived=False)
        db.session.add(meter)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('meter already exists')

    try:
        meter = Meter(meter_id=5,
                      utility_id=1,
                      service_location_id=5,
                      home_hub_id=5,
                      transformer_id=1,
                      feeder='IEEE123',
                      substation='HCE-Xcel',
                      meter_type=MeterType.RESIDENTIAL,
                      is_active=False,
                      is_archived=False)
        db.session.add(meter)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('meter already exists')

    try:
        meter = Meter(meter_id=6,
                      utility_id=1,
                      service_location_id=6,
                      home_hub_id=6,
                      transformer_id=1,
                      feeder='IEEE123',
                      substation='HCE-Xcel',
                      meter_type=MeterType.RESIDENTIAL,
                      is_active=False,
                      is_archived=False)
        db.session.add(meter)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('meter already exists')

    # Rate
    try:
        rate = Rate(rate_id=1, description='net_metering')
        db.session.add(rate)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('rate already exists')


    try:
        at = AlertType(
            alert_type_id=1,
            utility_id=1,
            name='YELLOW_ALARM_LOAD',
            limit=1.0,
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
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
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
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
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
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
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
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
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
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
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
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
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
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
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
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
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
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
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
        db.session.add(at)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('alert type already exists')

    # user
    try:
        user = User(
            id=1,
            email='test@test.com',
            email_confirmed_at=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
            first_name='fname',
            last_name='lname',
            address_id=1,
            utility_id=1,
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
        db.session.add(user)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('user already exists')

    # Pv
    try:
        pv = Pv(
            pv_id=1,
            home_hub_id=1,
            meter_id=1,
            q_rated=4000,
            is_active=1,
            is_archived=0,
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
        db.session.add(pv)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('PV already exists')

    try:
        pv = Pv(
            pv_id=2,
            home_hub_id=2,
            meter_id=2,
            q_rated=4000,
            is_active=1,
            is_archived=0,
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
        db.session.add(pv)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('PV already exists')

    try:
        pv = Pv(
            pv_id=3,
            home_hub_id=3,
            meter_id=3,
            q_rated=4000,
            is_active=1,
            is_archived=0,
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
        db.session.add(pv)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('PV already exists')

    try:
        pv = Pv(
            pv_id=4,
            home_hub_id=4,
            meter_id=4,
            q_rated=4000,
            is_active=1,
            is_archived=0,
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
        db.session.add(pv)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('PV already exists')

    try:
        pv = Pv(
            pv_id=5,
            home_hub_id=5,
            meter_id=5,
            q_rated=4000,
            is_active=1,
            is_archived=0,
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
        db.session.add(pv)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('PV already exists')

    try:
        pv = Pv(
            pv_id=6,
            home_hub_id=6,
            meter_id=6,
            q_rated=4000,
            is_active=1,
            is_archived=0,
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now())
        db.session.add(pv)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        print('PV already exists')

    # # meterinterval
    # try:
    #     mi = MeterInterval(
    #         meter_interval_id=1,
    #         meter_id=1,
    #         rate_id=1,
    #         start_time=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
    #         end_time=datetime.datetime.fromisoformat('2020-01-01T00:05:23'),
    #         e=1.0,
    #         qmtp=1.0,
    #         p_bid=1.0,
    #         q_bid=1.0,
    #         mode_market=0,
    #         mode_dispatch=0,
    #         is_bid=True)
    #     db.session.add(mi)
    #     db.session.commit()
    # except exc.IntegrityError:
    #     db.session.rollback()
    #     print('meter interval already exists')
    #
    # # MarketInterval
    # try:
    #     mai = MarketInterval(
    #         market_interval_id=1,
    #         market_id=1,
    #         p_exp=1.0,
    #         p_dev=1.0,
    #         p_clear=1.0,
    #         q_clear=1.0,
    #         alpha=1.0,
    #         start_time=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
    #         end_time=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
    #     db.session.add(mai)
    #     db.session.commit()
    # except exc.IntegrityError:
    #     db.session.rollback()
    #     print('market interval already exists')
    #
    # # HceBids
    # try:
    #     hceb = HceBids(
    #         bid_id=1,
    #         start_time=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
    #         end_time=datetime.datetime.fromisoformat('2020-01-01T00:05:23'),
    #         comment='asdfasdf',
    #         market_id=1)
    #     db.session.add(hceb)
    #     db.session.commit()
    # except exc.IntegrityError:
    #     db.session.rollback()
    #     print('hce bids already exists')
    #
    # # transformerinterval
    # try:
    #     tri = TransformerInterval(
    #         transformer_interval_id=1,
    #         transformer_id=1,
    #         import_capacity=1.0,
    #         export_capacity=1.0,
    #         q=1.0,
    #         start_time=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
    #         end_time=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
    #     db.session.add(tri)
    #     db.session.commit()
    # except exc.IntegrityError:
    #     db.session.rollback()
    #     print('transformer interval already exists')
    #
    # # alerts
    # try:
    #     alert = Alert(
    #         alert_id=1,
    #         alert_type_id=1,
    #         assigned_to='test@test.com',
    #         description='sdjfd',
    #         status='open',
    #         context='feeder',
    #         context_id='1',
    #         resolution = 'fdjgh')
    #     db.session.add(alert)
    #     db.session.commit()
    # except exc.IntegrityError:
    #     db.session.rollback()
    #     print('alert already exists')
    #
    # try:
    #     alert = Alert(
    #         alert_id=2,
    #         alert_type_id=1,
    #         assigned_to='test@test.com',
    #         description='sdjfd',
    #         status='open',
    #         context='feeder',
    #         context_id='1',
    #         resolution='fdjgh')
    #     db.session.add(alert)
    #     db.session.commit()
    # except exc.IntegrityError:
    #     db.session.rollback()
    #     print('alert already exists')
    #
    # # notifications
    # try:
    #     notification = Notification(
    #         notification_id=1,
    #         alert_type_id=1,
    #         email="test@test.com",
    #         is_active=False,
    #         created_by=1,
    #         updated_at=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
    #         created_at=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
    #     db.session.add(notification)
    #     db.session.commit()
    # except exc.IntegrityError:
    #     db.session.rollback()
    #     print('notification already exists')
    #
    # try:
    #     notification = Notification(
    #         notification_id=2,
    #         alert_type_id=1,
    #         email="test@test.com",
    #         is_active=False,
    #         created_by=1,
    #         updated_at=datetime.datetime.fromisoformat('2020-01-01T00:05:00'),
    #         created_at=datetime.datetime.fromisoformat('2020-01-01T00:05:23'))
    #     db.session.add(notification)
    #     db.session.commit()
    # except exc.IntegrityError:
    #     db.session.rollback()
    #     print('notification already exists')
