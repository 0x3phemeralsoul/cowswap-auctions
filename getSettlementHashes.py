from web3 import Web3
from dotenv import load_dotenv
import os, time, sys
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from loguru import logger

def main():

    # Load environment variables from .env file
    load_dotenv()

    # Setting logging
    logger.remove(0)
    logger.add(sys.stdout, level=os.getenv("LOGGER_LEVEL"))
    logger.add("logs/getSettlementHashes_{time:YYYY-MM-DD}.log", level=os.getenv("LOGGER_LEVEL"), rotation="100 MB")
    # Replace 'YOUR_DATABASE_URL' with the actual SQLite database URL
    database_url = os.getenv("DATABASE_URL", "sqlite:///cowswap-auctions.db")
    engine = create_engine(database_url, echo=os.getenv('VERBOSE_DB') == 'True')
    Base = automap_base()
    Base.prepare(autoload_with=engine)

    Transaction = Base.classes.transactions
    session = Session(engine)




    # Get the RPC endpoint from the environment variable
    rpc_endpoint = os.getenv("RPC_ENDPOINT")

    # Check if RPC endpoint is provided
    if not rpc_endpoint:
        raise ValueError("RPC_ENDPOINT is missing in the .env file")

    web3 = Web3(Web3.HTTPProvider(rpc_endpoint))



    contract_address = os.getenv("contract_address")


    # Specify blocks to fetch

    highestBlockDB_query = text("SELECT block_number from transactions ORDER by block_number DESC Limit 1")

    START_BLOCK=session.execute(highestBlockDB_query).scalar_one()
    END_BLOCK=min(int(START_BLOCK+int(os.getenv("CHUNK_SIZE"))),web3.eth.get_block('latest')['number'])
    logger.info(f"Start BLOCK:{START_BLOCK}, End BLOCK:{END_BLOCK}")
    try:
        for block in range(int(START_BLOCK+1), int(END_BLOCK)): 
            block = web3.eth.get_block(block, full_transactions=True) 
            for transaction in block.transactions:
                if(transaction["to"] == contract_address):
                    logger.info(f"Tx Hash:{transaction['hash'].hex()} - Block:{block['number']}")
                    exists = session.query(Transaction.tx_hash).filter_by(tx_hash=transaction["hash"].hex()).first() is not None
                    if(not exists):
                    # Insert row
                        tx_receipt= web3.eth.get_transaction_receipt(transaction['hash'].hex())
                        new_transaction = Transaction(tx_hash=transaction["hash"].hex(), chain_id=1, block_number=block["number"], gasUsed=tx_receipt['gasUsed'], effectiveGasPrice=tx_receipt['effectiveGasPrice'])
                        logger.debug(f'DB Commit output: {session.add(new_transaction)}') 
                        
    except Exception as error:
            logger.debug(f"ERROR: {error}")
    session.commit()
    session.close()


if __name__ == "__main__":
    main()
