from web3 import Web3
from dotenv import load_dotenv
import os, json
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, update

# Replace 'YOUR_DATABASE_URL' with the actual SQLite database URL
database_url = os.getenv("DATABASE_URL", "sqlite:///cowswap-auctions.db")
engine = create_engine(database_url, echo=os.getenv('VERBOSE_DB') == 'True')
Base = automap_base()
Base.prepare(autoload_with=engine)

ContractName = Base.classes.contract_names
session = Session(engine)

# Query all transactions from the table
Contracts = session.query(ContractName).all()

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

                print(f"Contract address {toFetch} and symbol: {contractData.functions.symbol().call()}")
                if(contractData.functions.symbol().call() != ''):
                    update_tag = (
                    update(ContractName)
                    .values(tag='ERC20')
                    .where(ContractName.address == toFetch)
                    )
                    connection.execute(update_tag)
                    connection.commit()
            except Exception as error:
                print(f"Contract address {toFetch} and name:{contract.contract_name} is not ERC20")
        else:
            print(f"Already tagged")

