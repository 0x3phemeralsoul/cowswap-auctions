from web3 import Web3
from dotenv import load_dotenv
import os, json, sys
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
    logger.add("logs/getUninternalizedCallData_{time:YYYY-MM-DD}.log", level=os.getenv("LOGGER_LEVEL"), rotation="100 MB")

    # Replace 'YOUR_DATABASE_URL' with the actual SQLite database URL
    database_url = os.getenv("DATABASE_URL", "sqlite:///cowswap-auctions.db")
    engine = create_engine(database_url, echo=os.getenv('VERBOSE_DB') == 'True')
    Base = automap_base()
    Base.prepare(autoload_with=engine)

    CallData = Base.classes.call_data
    UninternalizedCallDataToken = Base.classes.uninternalized_call_data_tokens
    UninternalizedCallDataClearingPrice= Base.classes.uninternalized_call_data_clearing_prices
    UninternalizedCallDataTrade = Base.classes.uninternalized_call_data_trades
    UninternalizedCallDataInteraction = Base.classes.uninternalized_call_data_interactions

    session = Session(engine)

    # Query all transactions from the table
    CallDatas = session.query(CallData).all()


    # Get the RPC endpoint from the environment variable
    rpc_endpoint = os.getenv("RPC_ENDPOINT")

    # Check if RPC endpoint is provided
    if not rpc_endpoint:
        raise ValueError("RPC_ENDPOINT is missing in the .env file")

    web3 = Web3(Web3.HTTPProvider(rpc_endpoint))


    with open('SettlementContract.json') as f:
        abi = json.load(f)



    settlementContract = web3.eth.contract(address=os.getenv("contract_address"), abi=abi)

    # Query missing inserts
    logger.info("Running query to remove entries already processed. Takes several seconds")
    calldata_query = text("SELECT * from call_data where call_data.solutionId not in (SELECT uninternalized_call_data_clearing_prices.solution_id from uninternalized_call_data_clearing_prices)")

    CallDatas = session.execute(calldata_query).all()
    logger.info(f"Entries to process {len(CallDatas)}")
    session.commit()



    # Fetch API data for each transaction
    for calldata in CallDatas:
        logger.debug(f"Call data: {calldata.callData}")
        logger.info(f" call data type:{type(calldata.callData)}")
        toDecode = calldata.callData
        solutionId = calldata.solutionId
        logger.info(f"Solution ID: {solutionId}")
        # Decode input data using Contract object's decode_function_input() method
        func_obj, func_params = settlementContract.decode_function_input(toDecode)

        # store tokens
        for address in func_params['tokens']:
            exists = session.query(UninternalizedCallDataToken.address).filter_by(address=address).first() is not None
            if(not exists):
                token = UninternalizedCallDataToken(address=address)
                session.add(token)

        # store clearing prices
        for price in func_params['clearingPrices']:
            clearing_price = UninternalizedCallDataClearingPrice(price=str(price), solution_id=solutionId)
            session.add(clearing_price)

        # store trades
        for trade_data in range(len(func_params['trades'])):
            logger.info(f"starting trades {trade_data}-----------------------------------------------------")
            logger.info(f"buyAmount type: {type(str(func_params['trades'][trade_data]['buyTokenIndex']))}")
            trades= UninternalizedCallDataTrade(
            sell_token_index= func_params['trades'][trade_data]['sellTokenIndex'],
            buy_token_index= str(func_params['trades'][trade_data]['buyTokenIndex']),
            receiver= func_params['trades'][trade_data]['receiver'],
            sell_amount= str(func_params['trades'][trade_data]['sellAmount']),
            buy_amount= str(func_params['trades'][trade_data]['buyAmount']),
            valid_to= func_params['trades'][trade_data]['validTo'],
            app_data= str(func_params['trades'][trade_data]['appData'].hex()),
            fee_amount= str(func_params['trades'][trade_data]['feeAmount']),
            flags= func_params['trades'][trade_data]['flags'],
            executed_amount= str(func_params['trades'][trade_data]['executedAmount']),
            signature=str(func_params['trades'][trade_data]['signature'].hex()),
            solution_id=solutionId)
            session.add(trades)

        for interaction_data in range(len(func_params['interactions'])):
            logger.info(f"interaction lentgh {interaction_data}: {len(func_params['interactions'][interaction_data])}")
            if(len(func_params['interactions'][interaction_data]) == 0):
                interaction = UninternalizedCallDataInteraction(
                    target='NULL',
                    value=0,
                    uninternalized_call_data='NULL',
                    solution_id=solutionId,
                    interactionPos=interaction_data
                )
                session.add(interaction)
            else:
                for interaction_set in range(len(func_params['interactions'][interaction_data])):

                    interaction = UninternalizedCallDataInteraction(
                        target=func_params['interactions'][interaction_data][interaction_set]['target'],
                        value=str(func_params['interactions'][interaction_data][interaction_set]['value']),
                        uninternalized_call_data=func_params['interactions'][interaction_data][interaction_set]['callData'].hex(),
                        solution_id=solutionId,
                        interactionPos=interaction_data
                    )
                    session.add(interaction)
            
        session.commit()
    
    # Close the session
    session.close()

if __name__ == "__main__":
    main()