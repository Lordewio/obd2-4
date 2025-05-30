from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Create engine and session
engine = create_engine('postgresql://localhost/obd2_db')
Session = sessionmaker(bind=engine)

# Create all tables
def init_db():
    Base.metadata.create_all(engine)

# Get session
def get_session():
    return Session()
