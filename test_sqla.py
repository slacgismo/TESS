from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from tess_db import *

engine = create_engine('mysql+pymysql://root:lmnj4ever@localhost/tess')

Session = sessionmaker(bind=engine)

session = Session()

system = System
