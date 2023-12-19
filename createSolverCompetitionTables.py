from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Replace 'YOUR_DATABASE_URL' with the actual SQLite database URL
database_url = os.getenv("DATABASE_URL", "sqlite:///cowswap-auctions.db")

Base = declarative_base()

class Auction(Base):
    __tablename__ = 'auction'

    auctionId = Column(Integer, primary_key=True)
    transactionHash = Column(String)
    gasPrice = Column(Integer)
    auctionStartBlock = Column(Integer)
    liquidityCollectedBlock = Column(Integer)
    competitionSimulationBlock = Column(Integer)

    orders = relationship('Order', back_populates='auction')
    prices = relationship('Price', back_populates='auction')
    solutions = relationship('Solution', back_populates='auction')

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    orderHash = Column(String)
    auctionId = Column(Integer, ForeignKey('auction.auctionId'))

    auction = relationship('Auction', back_populates='orders')

class Price(Base):
    __tablename__ = 'prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tokenAddress = Column(String)
    price = Column(String)
    auctionId = Column(Integer, ForeignKey('auction.auctionId'))

    auction = relationship('Auction', back_populates='prices')

class Solution(Base):
    __tablename__ = 'solutions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    solver = Column(String)
    solverAddress = Column(String)
    scoreProtocolWithSolverRisk = Column(String)
    ranking = Column(Integer)
    objective_total = Column(Float)
    objective_surplus = Column(Float)
    objective_fees = Column(Float)
    objective_cost = Column(Float)
    objective_gas = Column(Integer)
    auctionId = Column(Integer, ForeignKey('auction.auctionId'))

    auction = relationship('Auction', back_populates='solutions')
    clearingPrices = relationship('ClearingPrice', back_populates='solution')
    orders = relationship('SolutionOrder', back_populates='solution')
    callData = relationship('CallData', back_populates='solution')

class ClearingPrice(Base):
    __tablename__ = 'clearing_prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tokenAddress = Column(String)
    price = Column(String)
    solutionId = Column(Integer, ForeignKey('solutions.id'))

    solution = relationship('Solution', back_populates='clearingPrices')

class SolutionOrder(Base):
    __tablename__ = 'solution_orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    orderId = Column(String)
    executedAmount = Column(String)
    solutionId = Column(Integer, ForeignKey('solutions.id'))

    solution = relationship('Solution', back_populates='orders')

class CallData(Base):
    __tablename__ = 'call_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    callData = Column(String)
    uninternalizedCallData = Column(String)
    solutionId = Column(Integer, ForeignKey('solutions.id'))

    solution = relationship('Solution', back_populates='callData')

# Create SQLite database engine
engine = create_engine(database_url)

# Create tables in the database
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Insert sample data
auction = Auction(
    auctionId=7874433,
    transactionHash="0x8470d6bdacb9ee8f536b880cb380cdb92b978782ac9ab04a857afbdc855c7bb1",
    gasPrice=36359446938,
    auctionStartBlock=18513439,
    liquidityCollectedBlock=18513440,
    competitionSimulationBlock=18513442
)

session.add(auction)

# Insert more sample data for other tables...

# Commit the changes
session.commit()

order1 = Order(orderHash="0x2aafd29f463390065a8e867ece33cfca9c3a11742adb5d089b570b821dceed191732951b80c737dbb8f367e83e530623bb612e5466214a88", auction=auction)
order2 = Order(orderHash="0xe0e6b605dfd26976895e4ddedfb90929838a3164e3d98774cc1cf69fea1ea1d54334703b0b74e2045926f82f4158a103fce1df4f655aae41", auction=auction)
order3 = Order(orderHash="0x9d51dd6e92e28004d983a5662a6f6e0e03c245d20ebb0db96e1ac9d7aba5a11de3dff97e14f3a55228ed2f614114bf6b27a7677b65692d40", auction=auction)
order4 = Order(orderHash="0xc610be8a1a1edd654ded997925e3cb7031a48db5b4ecc9aeb994dd6b6af9e7033b60aaf68792530806a2e4ce68df4788844f1efa655b7307", auction=auction)

session.add_all([order1, order2, order3, order4])

price1 = Price(tokenAddress="0x000000007a58f5f58e697e51ab0357bc9e260a04", price="1629696672461435", auction=auction)
price2 = Price(tokenAddress="0x0001a500a6b18995b03f44bb040a5ffc28e45cb0", price="445032508420722", auction=auction)
price3 = Price(tokenAddress="0x00c83aecc790e8a4453e5dd3b0b4b3680501a7a7", price="15025110752646", auction=auction)
price4 = Price(tokenAddress="0x0100546f2cd4c9d97f798ffc9755e47865ff7ee6", price="814329966665857024", auction=auction)
price5 = Price(tokenAddress="0x01597e397605bf280674bf292623460b4204c375", price="11197076520527", auction=auction)
price6 = Price(tokenAddress="0x01ba67aac7f75f647d94220cc98fb30fcc5105bf", price="37359899689183", auction=auction)

session.add_all([price1, price2, price3, price4, price5, price6])

solution1 = Solution(
    solver="NaiveSolver",
    solverAddress="0x1a7a08423ab83e7939bf1df95952347d425e0a0a",
    scoreProtocolWithSolverRisk="1804681145715019",
    ranking=12,
    objective_total=1856627925630890.5,
    objective_surplus=226264219743156.25,
    objective_fees=6970802912694236,
    objective_cost=5340439206806502,
    objective_gas=146879,
    auction=auction
)

session.add(solution1)

clearing_price1 = ClearingPrice(tokenAddress="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", price="5393247737105425615747", solution=solution1)
clearing_price2 = ClearingPrice(tokenAddress="0xd9016a907dc0ecfa3ca425ab20b6b785b42f2373", price="45029197087305764", solution=solution1)

session.add_all([clearing_price1, clearing_price2])

solution_order1 = SolutionOrder(orderId="0x807416e7f9e45cea6ed05a3d018bf65af9269728a398bf1ad0a0b82818c6f60d2a467b8f134122c8b94035713e0f1160b160c1576548fa02", executedAmount="45029197087305764", solution=solution1)

session.add(solution_order1)

call_data1 = CallData(
    callData="0x13d79a0b000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000003600000000000000000000000000000000000000000000000000000000000000002000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000d9016a907dc0ecfa3ca425ab20b6b785b42f237300000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000001245e59023f0837cb83000000000000000000000000000000000000000000000000009ff9d0f0e8f02400000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000002a467b8f134122c8b94035713e0f1160b160c157000000000000000000000000000000000000000000000000009ff9d0f0e8f024000000000000000000000000000000000000000000000122e4fb515f22441d8500000000000000000000000000000000000000000000000000000000000001",
    uninternalizedCallData="0x13d79a0b000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000003600000000000000000000000000000000000000000000000000000000000000002000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000d9016a907dc0ecfa3ca425ab20b6b785b42f237300000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000001245e59023f0837cb83000000000000000000000000000000000000000000000000009ff9d0f0e8f02400000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000002a467b8f134122c8b94035713e0f1160b160c157000000000000000000000000000000000000000000000000009ff9d0f0e8f024000000000000000000000000000000000000000000000122e4fb515f22441d8500000000000000000000000000000000000000000000000000000000000001",
    solution=solution1
)

session.add(call_data1)

# Commit the changes to the database
session.commit()

# Query and print sample data from the database
print("Sample data from the database:")
print("Auction:", session.query(Auction).first().__dict__)
print("Orders:", [order.__dict__ for order in session.query(Order).all()])
print("Prices:", [price.__dict__ for price in session.query(Price).all()])
print("Solutions:", [solution.__dict__ for solution in session.query(Solution).all()])
print("Clearing Prices:", [clearing_price.__dict__ for clearing_price in session.query(ClearingPrice).all()])
print("Solution Orders:", [solution_order.__dict__ for solution_order in session.query(SolutionOrder).all()])
print("Call Data:", [call_data.__dict__ for call_data in session.query(CallData).all()])




# Delete all data from the tables
session.query(Auction).delete()
session.query(Order).delete()
session.query(Price).delete()
session.query(Solution).delete()
session.query(ClearingPrice).delete()
session.query(SolutionOrder).delete()
session.query(CallData).delete()

# Commit the changes
session.commit()

# Close the session
session.close()
