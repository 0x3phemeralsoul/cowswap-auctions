import requests
import os, sys
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from dotenv import load_dotenv
from loguru import logger

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Setting logging
    
    logger.add(sys.stdout, level=os.getenv("LOGGER_LEVEL"))
    logger.add("logs/getContractNames_{time:YYYY-MM-DD}.log", level=os.getenv("LOGGER_LEVEL"), rotation="100 MB")

    # Replace 'YOUR_DATABASE_URL' with the actual SQLite database URL
    database_url = os.getenv("DATABASE_URL", "sqlite:///cowswap-auctions.db")
    engine = create_engine(database_url, echo=os.getenv('LOGGER_LEVEL') == 'TRACE')
    Base = automap_base()
    Base.prepare(autoload_with=engine)

    ContractNames = Base.classes.contract_names
    CallDataInteraction = Base.classes.call_data_interactions
    UninternalizedCallDataInteraction = Base.classes.uninternalized_call_data_interactions

    session = Session(engine)


    # Example: Query all transactions from the table
    contracts = session.query(CallDataInteraction.target).distinct().all()

    # Iterate through distinct targets and make API requests
    for target in contracts:
        target_address = target[0]

        # Construct the API URL. This API provides contract name. 
        # A better endpoint is the metadata API which contains the public name tags that Etherscan has created but it costs 800+ USD/month. 
        # An alternative is to fetch this through Dune API which has the public name tags I think.
        api_url = f"https://{os.getenv('EXPLORER_URL')}/api?module=contract&action=getsourcecode&address={target_address}&apikey={os.getenv('EXPLORER_API')}"

        # Make the API request
        response = requests.get(api_url)
        data = response.json()

        # Process the API response as needed
        if data['status'] == '1':
            # Extract relevant information from the response
            name = data['result'][0]['ContractName']

            # Process or print the source code as needed
            logger.info(f"CallData: Source code for target address {target_address}:\n{name}\n")
            #if address already exists in contract_names, then skip
            exists = session.query(ContractNames.address).filter_by(address=target_address).first() is not None
            if(not exists):
                newName = ContractNames(address=target_address,contract_name=name, tag='')
                session.add(newName)
                session.commit()
            else:
                logger.info(f"CallData:Contract {target_address} already exists -----------------skipping")
        else:
            logger.info(f"CallData:API request failed for target address {target_address}. Error: {data['message']}, {data['result']}")

    # Example: Query all transactions from the table
    contracts = session.query(UninternalizedCallDataInteraction.target).distinct().all()

    # Iterate through distinct targets and make API requests
    for target in contracts:
        target_address = target[0]

        # Construct the API URL
        api_url = f"https://"+os.getenv('EXPLORER_URL')+"/api?module=contract&action=getsourcecode&address={target_address}&apikey={EXPLORER_API_key}"

        # Make the API request
        response = requests.get(api_url)
        data = response.json()

        # Process the API response as needed
        if data['status'] == '1':
            # Extract relevant information from the response
            name = data['result'][0]['ContractName']

            # Process or print the source code as needed
            logger.info(f"UninternalizedCallData: Source code for target address {target_address}:\n{name}\n")
            #if address already exists in contract_names, then skip
            exists = session.query(ContractNames.address).filter_by(address=target_address).first() is not None
            if(not exists):
                newName = ContractNames(address=target_address,contract_name=name, tag='')
                session.add(newName)
                session.commit()
            else:
                logger.info(f"UninternalizedCallData:Contract {target_address} already exists -----------------skipping")
        else:
            logger.info(f"UninternalizedCallData:API request failed for target address {target_address}. Error: {data['message']}, {data['result']}")


if __name__ == "__main__":
    main()