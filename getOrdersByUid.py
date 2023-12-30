import requests
import os, sys
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
import dateutil.parser
from loguru import logger
from dotenv import load_dotenv



   
def fetch_order_api_data(order_hash):
    api_url = f"https://api.cow.fi/"+os.getenv('CHAIN')+"/api/v1/orders/{order_hash}"
    response = requests.get(api_url)

    if response.status_code == 200:
        # Parse the JSON response
        api_data = response.json()
        return api_data
    else:
        print(f"Error fetching API data for tx_hash {order_hash}. Status Code: {response.status_code}")
        return None

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Setting logging
    logger.remove(0) 
    logger.add(sys.stdout, level=os.getenv("LOGGER_LEVEL"))
    logger.add("logs/getOrdersByUid_{time:YYYY-MM-DD}.log", level=os.getenv("LOGGER_LEVEL"), rotation="100 MB")

    # Replace 'YOUR_DATABASE_URL' with the actual SQLite database URL
    database_url = os.getenv("DATABASE_URL", "sqlite:///cowswap-auctions.db")
    engine = create_engine(database_url, echo=os.getenv('LOGGER_LEVEL') == 'TRACE')
    Base = automap_base()
    Base.prepare(autoload_with=engine)

    OrderByUid = Base.classes.orders_by_uid
    # Order = Base.classes.orders

    session = Session(engine)


    # Example: Query all transactions from the table
    logger.info("Running query to remove entries already processed. Takes several seconds")
    orders_query = text("SELECT DISTINCT orderHash FROM orders where orderHash not in (SELECT DISTINCT uid FROM orders_by_uid)")
 
    orders = session.execute(orders_query).all()
    logger.info(f"Entries to process {len(orders)}")
    session.commit()
    # Fetch API data for each transaction
    for order in orders:
        order_hash = order.orderHash
        solver_competition_api_data = fetch_order_api_data(order_hash)
        
        if solver_competition_api_data:
            # Process the API data as needed
            logger.info(f"API Data for order_hash {order_hash}")
            order = OrderByUid(
            creation_date = dateutil.parser.isoparse(solver_competition_api_data["creationDate"]),
            owner = solver_competition_api_data["owner"], 
            uid = solver_competition_api_data["uid"],
            available_balance = solver_competition_api_data["availableBalance"],
            executed_buy_amount = solver_competition_api_data["executedBuyAmount"],
            executed_sell_amount = solver_competition_api_data["executedSellAmount"],
            executed_sell_amount_before_fees = solver_competition_api_data["executedSellAmountBeforeFees"],
            executed_fee_amount = solver_competition_api_data["executedFeeAmount"],
            invalidated = solver_competition_api_data["invalidated"] == 'true' if True else False ,
            status = solver_competition_api_data["status"],
            class_ = solver_competition_api_data["class"],
            executed_surplus_fee = solver_competition_api_data["executedSurplusfee"] if ('executedSurplusfee' in solver_competition_api_data)  else '',
            settlement_contract = solver_competition_api_data["settlementContract"],
            full_fee_amount = solver_competition_api_data["fullFeeAmount"],
            solver_fee = solver_competition_api_data["solverFee"],
            is_liquidity_order = True if solver_competition_api_data["isLiquidityOrder"] == 'true' else False ,
            full_app_data = solver_competition_api_data["fullAppData"],
            sell_token = solver_competition_api_data["sellToken"],
            buy_token = solver_competition_api_data["buyToken"],
            receiver = solver_competition_api_data["receiver"],
            sell_amount = solver_competition_api_data["sellAmount"],
            buy_amount = solver_competition_api_data["buyAmount"],
            valid_to = solver_competition_api_data["validTo"],
            app_data =solver_competition_api_data["appData"],
            fee_amount = solver_competition_api_data["feeAmount"],
            kind = solver_competition_api_data["kind"],
            partially_fillable = True if solver_competition_api_data["partiallyFillable"] == 'true' else False ,
            sell_token_balance = solver_competition_api_data["sellTokenBalance"],
            buy_token_balance = solver_competition_api_data["buyTokenBalance"],
            signing_scheme = solver_competition_api_data["signingScheme"],
            signature = solver_competition_api_data["signature"],
            interactions = solver_competition_api_data["interactions"],
            )
            session.add(order)
            
            
    session.commit()
    # Close the session
    session.close()
   

if __name__ == "__main__":
    main()
