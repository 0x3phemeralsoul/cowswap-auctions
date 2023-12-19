from sqlalchemy import create_engine, Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship, sessionmaker,Session
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

database_url = os.getenv("DATABASE_URL", "sqlite:///cowswap-auctions.db")
engine = create_engine(database_url, echo=os.getenv('VERBOSE_DB') == 'True')
Base = declarative_base()
Base = automap_base()
Base.prepare(autoload_with=engine)
Solution = Base.classes.solutions
session = Session(engine)


class UninternalizedCallDataToken(Base):
    __tablename__ = 'uninternalized_call_data_tokens'

    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True, nullable=False)

class UninternalizedCallDataClearingPrice(Base):
    __tablename__ = 'uninternalized_call_data_clearing_prices'

    id = Column(Integer, primary_key=True)
    price = Column(String, nullable=False)

    solution_id = Column(Integer, ForeignKey('solutions.id'))
    solution = relationship('Solution', back_populates='UninternalizedCallDataClearingPrice')

class UninternalizedCallDataTrade(Base):
    __tablename__ = 'uninternalized_call_data_trades'

    id = Column(Integer, primary_key=True)
    sell_token_index = Column(Integer, nullable=False)
    buy_token_index = Column(Integer, nullable=False)
    receiver = Column(String, nullable=False)
    sell_amount = Column(String, nullable=False)
    buy_amount = Column(String, nullable=False)
    valid_to = Column(BigInteger, nullable=False)
    app_data = Column(String)
    fee_amount = Column(String, nullable=False)
    flags = Column(Integer, nullable=False)
    executed_amount = Column(String, nullable=False)
    signature = Column(String)

    """ sell_token_id = Column(Integer, ForeignKey('uninternalized_call_data_tokens.id'))
    sell_token = relationship('UninternalizedCallDataToken', back_populates='UninternalizedCallDataTrade')

    buy_token_id = Column(Integer, ForeignKey('uninternalized_call_data_tokens.id'))
    buy_token = relationship('UninternalizedCallDataToken', back_populates='UninternalizedCallDataTrade') """

    solution_id = Column(Integer, ForeignKey('solutions.id'))
    solution = relationship('Solution', back_populates='UninternalizedCallDataTrade')

class UninternalizedCallDataInteraction(Base):
    __tablename__ = 'uninternalized_call_data_interactions'

    id = Column(Integer, primary_key=True)
    target = Column(String, nullable=False)
    value = Column(String, nullable=True)
    uninternalized_call_data = Column(String, nullable=True)
    interactionPos = Column(Integer)

    """ target_token_id = Column(Integer, ForeignKey('uninternalized_call_data_tokens.id'))
    target_token = relationship('UninternalizedCallDataToken', back_populates='UninternalizedCallDataInteraction') """

    solution_id = Column(Integer, ForeignKey('solutions.id'))
    solution = relationship('Solution', back_populates='UninternalizedCallDataInteraction')


# Create tables in the database
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()



""" # Insert sample data
tokens_data = ['0x162bb2Bb5FB03976a69dD25bB9afcE6140dB1433',
               '0x2b81945875f892afF04AF0A298d35FB2cF848c7b',
               '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
               '0xDEf1CA1fb7FBcDC777520aa7f396b4E015F497aB']

for address in tokens_data:
    token = UninternalizedCallDataToken(address=address)
    session.add(token)

clearing_prices_data = [16734140676112384, 93972312915968, 98966320943104, 10000000000]

for price in clearing_prices_data:
    clearing_price = UninternalizedCallDataClearingPrice(price=price)
    session.add(clearing_price)

# Example inserts for Trade table
example_trades_data = [
    {
        'sell_token_index': 2,
        'buy_token_index': 3,
        'receiver': '0xf733AB0f071a0a64817F9Fb36a00c0FB308e4649',
        'sell_amount': 93849545758977365,
        'buy_amount': 927921776037168126115,
        'valid_to': 1699962397,
        'app_data': b'\x8f(/t\xcb\xa2\xfdtS\xc3NB\xc9\xc0\xd6F\x13}3\x95\x110\xc3\xbd\xfc\xc2"\xb4\xb4\xdb\xb3%',
        'fee_amount': 6150454241022635,
        'flags': 0,
        'executed_amount': 93849545758977365,
        'signature': b'\xbb\xde{l\'\xed\x9d\xbf\xfa]es\xa5j\xae\xfb\xc6\xdd|\xf6\xf7\xfb\x05\xf9\x10j\xee\x84aM\x04L\x1a6\xd5\xb2?,\xc9\x9f\xa4Wk&\xaf\xca\xb3\x9c"\xad\x06"f\x9e\xae;\xabL\xd8\xd8\x8d\x18\x0c\x89\x1b'
    },
    {
        'sell_token_index': 0,
        'buy_token_index': 1,
        'receiver': '0x00BB1654Ff52b4d59e68A304a7f4e2625462d585',
        'sell_amount': 2172043278055378,
        'buy_amount': 355594691916790396,
        'valid_to': 1699962378,
        'app_data': b'F\x9b\xe3I\x01\x89\x85i\x99?\xd5\x88$3\xe6\x9dv\xe3F\xdc\x01\xaf\xa1\x97\xb6F\x11-\x95\x9fg\xf8',
        'fee_amount': 42218154919597,
        'flags': 0,
        'executed_amount': 2172043278055378,
        'signature': b'\x16\x05\xc9\xba\xe0\xd8S:*\xb9p\x08\x04\x9cM\xf8(`\xc2\n\xf9|\xfa\xba.\xecv\xb2\xb5\xa5\x1f\xa5@\xed5\x1eb}R\x87\xc4\xd6\x89!\xce\xe3a'
    }
]

for trade_data in example_trades_data:
    trade = UninternalizedCallDataTrade(**trade_data)
    session.add(trade)

# Example inserts for Interaction table
example_interactions_data = [
    {
        'target': '0x1111111254EEB25477B68fb85Ed929f73A960582',
        'value': 0,
        'uninternalized_call_data': b'\xe4I\x02.\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01Mk\xaa%K\xadU\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xb7v<\x06w\xd2'
    },
    {
        'target': '0x162bb2Bb5FB03976a69dD25bB9afcE6140dB1433',
        'value': 0,
        'uninternalized_call_data': b'\xa9\x05\x9c\xbb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x86\xf5\xd5\x9ahqp\xcfC\x15\x00\xd7\x00q\x06\x00\\\\\xec.\xe9\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xb7v<\x06w\xd2'
    },
    # Add more interactions if needed
]

for interaction_data in example_interactions_data:
    interaction = UninternalizedCallDataInteraction(**interaction_data)
    session.add(interaction)


# Commit the changes
session.commit() """

""" # Delete all data from tables
session.query(UninternalizedCallDataToken).delete()
session.query(UninternalizedCallDataClearingPrice).delete()
session.query(UninternalizedCallDataTrade).delete()
session.query(UninternalizedCallDataInteraction).delete() """

# Commit the changes after deletion
session.commit()

# Close the session
session.close()
