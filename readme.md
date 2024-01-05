# install
create a cowswap-auctions.db file which will be empty
## Table creation
 run the files in the bellow sequence as the tables have foreign key dependencies
 ```
 python3 createTransactionsTable.py
 python3 createSolverCompetitionTables.py
 python3 createCallDataTables.py
 python3 createUninternalizaedCallDataTables.py
 python3 createContractNameTable.py
 python3 createOrdersbyUIDTable.py
 ```
## Table population
### get hashes from each on-chain batch auction settlement
```
python3 getSettlementHashes.py
```
### for each settlement now let's get the full competition data with winner and losers

```
python3 getSolverCompetitions.py
```
### let's decode the call data from the solutions provided by solvers
```
python3 getCallData.py
python3 getUninternalizedCallData.py
```

### let's extract the contracts that each solution is interacting with. This will give us token contracts (the interaction is a transferFrom() call cuz these are CoWs) and also we will get contracts from DEXes which are the liquidity sources that each solver has integrated with to solve non-CoWs in the batches.

```
python3 getContractNames.py
```
This script populates the TAG conlumn with ERC20 for token interactions, for other interactions I've manually populated the collumn in order to identify the liquidity source used by the solver.

### let's get all the transactions that users submitted for each batch auction so we can calculate COWs opportunities and check them against the COWs that were submitted on solutions

before running the below command you might want to create an index on Orders.orderHash column as that table has over 10M rows.

```
python3 getOrdersByUid.py
```

# env template
- rename .env.example to .env
- set the RPC endpoint
- set the Etherscan API Key
- VERBOSE_DB can be set to True in order for the DB to output every statement/Commit for debugging purposes.


# note
if you set the CHUNK_SIZE too little, like 10 blocks and there are no settlement transactions during those blocks, no new block is added to the Transactions table, and the getSettlementHashes always checks the highest block in Transactions, so if no new block is added, the next time the loop iterates it will pick again the same block + 10 blocks(and we know those 10 blocks didn't bring any new blocks, hence infinite loop on those 10 blocks). Pick CHUNK_SIZE like 50 blocks or so.