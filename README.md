# Sample Hardhat Project

This project demonstrates a basic Hardhat use case. It comes with a sample contract, a test for that contract, and a Hardhat Ignition module that deploys that contract.

Try running some of the following tasks:

```shell
npx hardhat help
npx hardhat test
REPORT_GAS=true npx hardhat test
npx hardhat node
npx hardhat ignition deploy ./ignition/modules/Lock.js
```

## E-Voting with MetaMask (local development)

The Streamlit app keeps the Python blockchain simulation and adds a separate
MetaMask flow for the `EVotingInventaris` contract on Hardhat Localhost.

1. Install the JavaScript dependencies with `npm install`.
2. Start the local EVM in one terminal with `npx hardhat node`.
3. In another terminal, deploy the voting contract:
   `npx hardhat run scripts/deploy.js --network localhost`.
   The deployed address and chain ID are written to `deployment.json`.
4. Add a MetaMask network with RPC `http://127.0.0.1:8545`, chain ID `31337`,
   and currency `ETH`. Import a funded development account printed by the
   local Hardhat node. The account that deployed the contract is its admin.
5. Install the Python app dependencies with
   `python -m pip install -r E-VOTING/requirements.txt`, then start it from
   the app folder with `streamlit run app.py`.

The app also offers a Python-only simulation; its results are session-local
and are separate from contract transactions. The Dashboard and Voting Results
pages read confirmed vote events from the local Hardhat node; use the results
page refresh button after a MetaMask vote. Contract voting requires the admin
to register voter IDs first. This prototype stores voter IDs and choices
publicly on-chain and does not provide ballot secrecy or bind a voter ID to a
specific wallet. Use only for local demonstrations, not real elections.
