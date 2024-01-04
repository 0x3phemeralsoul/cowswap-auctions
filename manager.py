import getSettlementHashes, getSolverCompetitions, getCallData, getUninternalizedCallData, getContractNames, getOrdersByUid, tagContracts
from dotenv import load_dotenv
from loguru import logger
import os, sys



def main():
    # Load environment variables from .env file
    load_dotenv()

    # Setting logging
    logger.remove(0)
    logger.add(sys.stdout, level=os.getenv("LOGGER_LEVEL"))
    logger.add("logs/manager_{time:YYYY-MM-DD}.log", level=os.getenv("LOGGER_LEVEL"), rotation="100 MB")
    while True:
        logger.info("Start getSettlementHashes")
        getSettlementHashes.main()
        logger.info("Start getSolverCompetitions")
        getSolverCompetitions.main()
        logger.info("Start getCallData")
        getCallData.main()
        logger.info("Start getUninternalizedCallData")
        getUninternalizedCallData.main()
        logger.info("Start getContractNames")
        getContractNames.main()
        logger.info("Start getOrdersByUid")
        getOrdersByUid.main()
        logger.info("Start tagContracts")
        tagContracts.main()


if __name__ == "__main__":
    main()