import requests
import os, time, sys
from dotenv import load_dotenv
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from loguru import logger


def fetch_api_data(tx_hash):
    # Checking the production env
    while True:
        try:
            api_url = "https://api.cow.fi/"+os.getenv('CHAIN')+"/api/v1/solver_competition/by_tx_hash/"+tx_hash
            response = requests.get(api_url)

            if response.status_code == 200:
                # Parse the JSON response
                api_data = response.json()
                return api_data
            else:
                logger.info(f"PRODUCTION: Error fetching API data for tx_hash {tx_hash} Status Code: {response.status_code}")

                # checking the Barn env
                api_url = "https://barn.api.cow.fi/"+os.getenv('CHAIN')+"/api/v1/solver_competition/by_tx_hash/"+tx_hash
                response = requests.get(api_url)

                if response.status_code == 200:
                    # Parse the JSON response
                    api_data = response.json()
                    return api_data
                else:
                    logger.info(f"BARN: Error fetching API data for tx_hash {tx_hash} Status Code: {response.status_code}")
                    return None
        except Exception as error:
            logger.debug(f"ERROR: {error}")
            time.sleep(5)
            continue
    

def main():
    # Load environment variables from .env file
    load_dotenv()
    # Setting logging
    #logger.remove(0)
    #logger.add(sys.stdout, level=os.getenv("LOGGER_LEVEL"))
    logger.add("logs/getSolverCompetitions_{time:YYYY-MM-DD}.log", level=os.getenv("LOGGER_LEVEL"), rotation="100 MB")

    # Replace 'YOUR_DATABASE_URL' with the actual SQLite database URL
    database_url = os.getenv("DATABASE_URL", "sqlite:///cowswap-auctions.db")
    engine = create_engine(database_url, echo=os.getenv('VERBOSE_DB') == 'True')
    Base = automap_base()
    Base.prepare(autoload_with=engine)

    Auction = Base.classes.auction
    Order = Base.classes.orders
    Price = Base.classes.prices
    Solution = Base.classes.solutions
    ClearingPrice = Base.classes.clearing_prices
    SolutionOrder = Base.classes.solution_orders
    CallData = Base.classes.call_data

    session = Session(engine)


    # Query missing inserts
    logger.info("Running query to remove entries already processed. Takes several seconds")
    query = text("SELECT * FROM transactions where tx_hash not in(SELECT auction.transactionHash from auction)")
    transactions = session.execute(query).all()
    logger.info(f"Entries to process {len(transactions)}")
    session.commit()

    # Fetch API data for each transaction
    for transaction in transactions:
        tx_hash = transaction.tx_hash


        api_data = fetch_api_data(tx_hash)
        
        if api_data:
            # Process the API data as needed
            logger.info(f"API Data for tx_hash {tx_hash}")
            auction = Auction(
                auctionId=api_data['auctionId'],
                transactionHash=api_data['transactionHash'],
                # gasPrice=api_data['gasPrice'],
                auctionStartBlock=api_data['auctionStartBlock'],
                # liquidityCollectedBlock=api_data['liquidityCollectedBlock'],
                competitionSimulationBlock=api_data['competitionSimulationBlock']
            )
            logger.info(f"TxHash: {api_data['transactionHash']}")
            session.add(auction)
            # session.commit()
            for orders in range(len(api_data['auction']['orders'])):
                order = Order(orderHash=api_data['auction']['orders'][orders], auction=auction)
                session.add(order)
            # session.commit()
            tokens = [*api_data['auction']['prices']]
            for prices in range(len(tokens)):
                logger.debug(f"TokenAddress {prices}: {tokens[prices]}")
                price = Price(tokenAddress=tokens[prices], price=api_data['auction']['prices'][tokens[prices]], auction=auction)
                session.add(price)
            # session.commit()

            for solutions in range(len(api_data['solutions'])):
                if 'scoreProtocolWithSolverRisk' in api_data['solutions']:
                    scoreProtocolWithSolverRisk=api_data['solutions'][solutions]['scoreProtocolWithSolverRisk']
                else:
                    scoreProtocolWithSolverRisk='NA'
                solution = Solution(
                    solver=api_data['solutions'][solutions]['solver'],
                    solverAddress=api_data['solutions'][solutions]['solverAddress'],
                    scoreProtocolWithSolverRisk=scoreProtocolWithSolverRisk,
                    ranking=api_data['solutions'][solutions]['ranking'],
                    # objective_total=api_data['solutions'][solutions]['objective']['total'],
                    # objective_surplus=api_data['solutions'][solutions]['objective']['surplus'],
                    # objective_fees=api_data['solutions'][solutions]['objective']['fees'],
                    # objective_cost=api_data['solutions'][solutions]['objective']['cost'],
                    # objective_gas=api_data['solutions'][solutions]['objective']['gas'],
                    auction=auction
                )
                session.add(solution)
                #session.commit()
                tokens = [*api_data['solutions'][solutions]['clearingPrices']]
                for clearing_prices in range(len(tokens)):
                    clearing_price= ClearingPrice(tokenAddress=tokens[clearing_prices], price=api_data['solutions'][solutions]['clearingPrices'][tokens[clearing_prices]], solutions=solution)
                    session.add(clearing_price)
                # session.commit()
                for solution_orders in range(len(api_data['solutions'][solutions]['orders'])):
                    solution_order = SolutionOrder(orderId=api_data['solutions'][solutions]['orders'][solution_orders]['id'], executedAmount=api_data['solutions'][solutions]['orders'][solution_orders]['executedAmount'], solutions=solution)
                    session.add(solution_order)
                # session.commit()

            callData = api_data['solutions'][solutions]['callData']
            if ('uninternalizedCallData' in api_data['solutions'][solutions]):
                uninternalizedCallData = api_data['solutions'][solutions]['uninternalizedCallData']
                call_data = CallData(
                callData=callData,
                uninternalizedCallData=uninternalizedCallData,
                solutions=solution
                )
            else:
                call_data = CallData(
                    callData=callData,
                    uninternalizedCallData='',
                    solutions=solution
                )
            session.add(call_data)
            # Commit the changes
        
        session.commit() 
        # Close the session
        session.close()
   

if __name__ == "__main__":
    main()
