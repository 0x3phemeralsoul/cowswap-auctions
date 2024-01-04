from web3 import Web3
from dotenv import load_dotenv
import os, json
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, update, text
from loguru import logger




def main():
    # Load environment variables from .env file
    load_dotenv()

    # Setting logging



    # Replace 'YOUR_DATABASE_URL' with the actual SQLite database URL
    database_url = os.getenv("DATABASE_URL", "sqlite:///cowswap-auctions.db")
    engine = create_engine(database_url, echo=os.getenv('VERBOSE_DB') == 'True')
    Base = automap_base()
    Base.prepare(autoload_with=engine)

    ContractName = Base.classes.contract_names
    session = Session(engine)

    # Query all transactions from the table
    Contracts = session.query(ContractName).all()

    # Query missing inserts
    logger.info("Running query to remove entries already processed. Takes several seconds")
    contracts_query = text("SELECT * from contract_names where tag = ''")

    Contracts = session.execute(contracts_query).all()
    logger.info(f"Entries to process {len(Contracts)}")
    session.commit()

    # Load environment variables from .env file
    load_dotenv()

    # Get the RPC endpoint from the environment variable
    rpc_endpoint = os.getenv("RPC_ENDPOINT")

    # Check if RPC endpoint is provided
    if not rpc_endpoint:
        raise ValueError("RPC_ENDPOINT is missing in the .env file")

    web3 = Web3(Web3.HTTPProvider(rpc_endpoint))

    with open('erc20.json') as f:
        abi = json.load(f)




    with engine.connect() as connection:

        for contract in Contracts:
            toFetch = contract.address
            tag = contract.tag
            if(tag == ''):
                contractData = web3.eth.contract(address=toFetch, abi=abi)
                try:

                    logger.info(f"Contract address {toFetch} and symbol: {contractData.functions.symbol().call()}")
                    if(contractData.functions.symbol().call() != ''):
                        update_tag = (
                        update(ContractName)
                        .values(tag='ERC20')
                        .where(ContractName.address == toFetch)
                        )
                        connection.execute(update_tag)
                        
                except Exception as error:
                    logger.info(f"Contract address {toFetch} and name:{contract.contract_name} is not ERC20")
            else:
                logger.info(f"Already tagged")

        connection.commit()
    # Close the session
    session.close()



if __name__ == "__main__":
    main()
