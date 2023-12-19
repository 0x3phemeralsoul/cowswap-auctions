import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, DateTime, Boolean, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import dateutil.parser
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Replace 'YOUR_DATABASE_URL' with the actual SQLite database URL
database_url = os.getenv("DATABASE_URL", "sqlite:///cowswap-auctions.db")

Base = declarative_base()

class OrderByUid(Base):
    __tablename__ = 'orders_by_uid'

    id = Column(Integer, primary_key=True, autoincrement=True)
    # rows from the https://api.cow.fi/"+os.getenv('CHAIN')+"/api/v1/orders/ API endpoint
    creation_date = Column(DateTime)
    owner = Column(String)
    uid = Column(String)
    available_balance = Column(Integer)
    executed_buy_amount = Column(String)
    executed_sell_amount = Column(String)
    executed_sell_amount_before_fees = Column(String)
    executed_fee_amount = Column(String)
    invalidated = Column(Boolean)
    status = Column(String)
    class_ = Column(String)  # Note: Using "class_" instead of "class" as it's a reserved word
    executed_surplus_fee = Column(String)
    settlement_contract = Column(String)
    full_fee_amount = Column(String)
    solver_fee = Column(String)
    is_liquidity_order = Column(Boolean)
    full_app_data = Column(JSON)
    sell_token = Column(String)
    buy_token = Column(String)
    receiver = Column(String)
    sell_amount = Column(String)
    buy_amount = Column(String)
    valid_to = Column(Integer)
    app_data = Column(String)
    fee_amount = Column(String)
    kind = Column(String)
    partially_fillable = Column(Boolean)
    sell_token_balance = Column(String)
    buy_token_balance = Column(String)
    signing_scheme = Column(String)
    signature = Column(String)
    interactions = Column(JSON)



# Create SQLite database engine
engine = create_engine(database_url)

# Create tables in the database
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

order1 = OrderByUid(
    creation_date = dateutil.parser.isoparse('2023-10-20T21:15:05.662227Z'),
    owner = '0x1732951b80c737dbb8f367e83e530623bb612e54', 
    uid = '0x2aafd29f463390065a8e867ece33cfca9c3a11742adb5d089b570b821dceed191732951b80c737dbb8f367e83e530623bb612e5466214a88',
    available_balance = 'null',
    executed_buy_amount = 0,
    executed_sell_amount = 0,
    executed_sell_amount_before_fees = 0,
    executed_fee_amount = 0,
    invalidated = False,
    status = 'open',
    class_ = 'limit', 
    executed_surplus_fee = 0,
    settlement_contract = '0x9008d19f58aabd9ed0d60971565aa8510560ab41',
    full_fee_amount = 0,
    solver_fee = 0,
    is_liquidity_order = False,
    full_app_data = "{\"appCode\":\"CoW Swap\",\"environment\":\"production\",\"metadata\":{\"orderClass\":{\"orderClass\":\"limit\"},\"quote\":{\"slippageBips\":\"0\"}},\"version\":\"0.9.0\"}",
    sell_token = "0xfa3e941d1f6b7b10ed84a0c211bfa8aee907965e",
    buy_token = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    receiver = "0x1732951b80c737dbb8f367e83e530623bb612e54",
    sell_amount = "100000000000000",
    buy_amount = "1249800000000000000",
    valid_to = 1713457800,
    app_data = '0xf17701e13dfae0fcc7dcfffcb5f5dde0e7c232494f1678e89d900f140cd702f1',
    fee_amount = 0,
    kind = 'sell',
    partially_fillable = True,
    sell_token_balance = 'erc20',
    buy_token_balance = 'erc20',
    signing_scheme = 'eip712',
    signature = "0x52100259504603b01ab717066c97d2ec17d904dbf7b1b52b5e808e1323c3aa3861aa9a2085b8303b6a3fc1a27a710c89f27705d3129070a523f4aefb82d04ac31c",
    interactions = '{ "pre": [],"post": []}',
    )


session.add_all([order1])


print("Orders:", [order.__dict__ for order in session.query(OrderByUid).all()])





# Delete all data from the tables

session.query(OrderByUid).delete()


# Commit the changes
session.commit()

# Close the session
session.close()
