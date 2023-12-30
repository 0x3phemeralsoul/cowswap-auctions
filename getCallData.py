from web3 import Web3
from dotenv import load_dotenv
import os, json, sys
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from loguru import logger

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Setting logging
    logger.remove(0)
    logger.add(sys.stdout, level=os.getenv("LOGGER_LEVEL"))
    logger.add("logs/getCallData_{time:YYYY-MM-DD}.log", level=os.getenv("LOGGER_LEVEL"), rotation="100 MB")

    # Replace 'YOUR_DATABASE_URL' with the actual SQLite database URL
    database_url = os.getenv("DATABASE_URL", "sqlite:///cowswap-auctions.db")
    engine = create_engine(database_url, echo=os.getenv('LOGGER_LEVEL') == 'TRACE')
    Base = automap_base()
    Base.prepare(autoload_with=engine)

    CallData = Base.classes.call_data
    CallDataToken = Base.classes.call_data_tokens
    CallDataClearingPrice= Base.classes.call_data_clearing_prices
    CallDataTrade = Base.classes.call_data_trades
    CallDataInteraction = Base.classes.call_data_interactions

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





    # Fetch API data for each transaction
    for calldata in CallDatas:
        logger.debug(f"Call data: {calldata.callData}")
        logger.debug(f" call data type:{type(calldata.callData)}")
        toDecode = calldata.callData
        solutionId = calldata.solutionId
        logger.info(f"Solution ID: {solutionId}")
        # Decode input data using Contract object's decode_function_input() method
        func_obj, func_params = settlementContract.decode_function_input(toDecode)
        # pprint.pprint(f"Func_objc: {func_obj}")
        #if solutionID already exists in call_data_tables, then skip
        #TODO: do a query to remove all IDS already in DB and only go through new ones, to avoid iterating over full table
        exists = session.query(CallDataClearingPrice.solution_id).filter_by(solution_id=solutionId).first() is not None
        logger.info(f"SolutionID {solutionId} already exists -----------------skipping")
        if(not exists):
            # store tokens
            for address in func_params['tokens']:
                exists = session.query(CallDataToken.address).filter_by(address=address).first() is not None
                if(not exists):
                    token = CallDataToken(address=address)
                    session.add(token)
            session.commit()
            # store clearing prices
            for price in func_params['clearingPrices']:
                clearing_price = CallDataClearingPrice(price=str(price), solution_id=solutionId)
                session.add(clearing_price)

            # store trades
            for trade_data in range(len(func_params['trades'])):
                logger.info(f"starting trades {trade_data}-----------------------------------------------------")
                logger.debug(f"buyAmount type: {type(str(func_params['trades'][trade_data]['buyTokenIndex']))}")
                trades= CallDataTrade(
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
                    interaction = CallDataInteraction(
                        target='NULL',
                        value=0,
                        call_data='NULL',
                        solution_id=solutionId,
                        interactionPos=interaction_data
                    )
                    session.add(interaction)
                else:
                    for interaction_set in range(len(func_params['interactions'][interaction_data])):

                        interaction = CallDataInteraction(
                            target=func_params['interactions'][interaction_data][interaction_set]['target'],
                            value=str(func_params['interactions'][interaction_data][interaction_set]['value']),
                            call_data=func_params['interactions'][interaction_data][interaction_set]['callData'].hex(),
                            solution_id=solutionId,
                            interactionPos=interaction_data
                        )
                        session.add(interaction)
            
        session.commit()

if __name__ == "__main__":
    main()