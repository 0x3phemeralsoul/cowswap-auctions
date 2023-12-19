from web3 import Web3
from dotenv import load_dotenv
import os
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

# Replace 'YOUR_DATABASE_URL' with the actual SQLite database URL
database_url = os.getenv("DATABASE_URL", "sqlite:///"+os.getenv('DB_NAME'))
engine = create_engine(database_url, echo=os.getenv('VERBOSE_DB') == 'True')
Base = automap_base()
Base.prepare(autoload_with=engine)

Transaction = Base.classes.transactions
session = Session(engine)


# Load environment variables from .env file
load_dotenv()

# Get the RPC endpoint from the environment variable
rpc_endpoint = os.getenv("RPC_ENDPOINT")

# Check if RPC endpoint is provided
if not rpc_endpoint:
    raise ValueError("RPC_ENDPOINT is missing in the .env file")

web3 = Web3(Web3.HTTPProvider(rpc_endpoint))



contract_address = os.getenv("contract_address")

# Specify blocks to fetch
START_BLOCK=os.getenv("START_BLOCK")
END_BLOCK=os.getenv("END_BLOCK")

for block in range(int(START_BLOCK), int(END_BLOCK)): 
    block = web3.eth.get_block(block, full_transactions=True) 
    for transaction in block.transactions:
        if(transaction["to"] == contract_address):
            print(transaction["hash"].hex(), ",", block["number"])
            exists = session.query(Transaction.tx_hash).filter_by(tx_hash=transaction["hash"].hex()).first() is not None
            if(not exists):
            # Insert row
                tx_receipt= web3.eth.get_transaction_receipt(transaction['hash'].hex())
                new_transaction = Transaction(tx_hash=transaction["hash"].hex(), chain_id=1, block_number=block["number"], gasUsed=tx_receipt['gasUsed'], effectiveGasPrice=tx_receipt['effectiveGasPrice'])
                print('DB Commit output:', session.add(new_transaction)) 
                session.commit()

session.close()
