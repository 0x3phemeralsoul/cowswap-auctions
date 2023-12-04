from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker,Session
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

database_url = os.getenv("DATABASE_URL", "sqlite:///cowswap-auctions.db")
engine = create_engine(database_url, echo=os.getenv('VERBOSE_DB') == 'True')
Base = declarative_base()
Base = automap_base()
Base.prepare(autoload_with=engine)
Interaction = Base.classes.call_data_interactions
session = Session(engine)


class ContractName(Base):
    __tablename__ = 'contract_names'

    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True, nullable=False)
    contract_name = Column(String)
    tag = Column(String)

# Create tables in the database
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Commit the changes after deletion
session.commit()

# Close the session
session.close()

