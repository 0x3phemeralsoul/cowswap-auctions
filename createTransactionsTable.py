from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Replace 'YOUR_DATABASE_URL' with the actual SQLite database URL
database_url = os.getenv("DATABASE_URL", "sqlite:///cowswap-auctions.db")

# Define the SQLAlchemy model
Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tx_hash = Column(String, nullable=False, unique=True)
    chain_id = Column(Integer, nullable=False)
    block_number = Column(Integer, nullable=False)

# Create SQLite database engine
engine = create_engine(database_url)

# Create the transactions table
Base.metadata.create_all(bind=engine)

# Create a Session
Session = sessionmaker(bind=engine)
session = Session()

# Example: Add a transaction to the table
example_tx = Transaction(tx_hash='0x123456789abcdef', chain_id=1, block_number=12345)
session.add(example_tx)
session.commit()

# Example: Query and print the added transaction
queried_transaction = session.query(Transaction).filter_by(tx_hash=example_tx.tx_hash).first()
if queried_transaction:
    print(f"Example Transaction: ID: {queried_transaction.id}, Tx Hash: {queried_transaction.tx_hash}, Chain ID: {queried_transaction.chain_id}, Block Number: {queried_transaction.block_number}")

    # Example: Delete the added transaction
    session.delete(queried_transaction)
    session.commit()

    print("Example Transaction deleted.")

# Close the session
session.close()
