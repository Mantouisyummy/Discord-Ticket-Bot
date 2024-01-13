from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine(
    'sqlite:///./database.db', connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base = declarative_base()

def create_table():
    Base.metadata.create_all(bind=engine)

def create_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session