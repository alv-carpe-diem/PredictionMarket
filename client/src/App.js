import React, {Component} from "react"
import './App.css'
import {getWeb3} from "./getWeb3"
import map from "./artifacts/deployments/map.json"
import {getEthereum} from "./getEthereum"
import { Pie } from 'react-chartjs-2'

const SIDE = {
    Marcos: 0,
    Pacquiao: 1
};

class App extends Component {
    
    state = {
        web3: null,
        accounts: null,
        chainid: null,
        predictionMarket: null,
        betPredictions: null,
        myBets: null,
    }

    componentDidMount = async () => {

        // Get network provider and web3 instance.
        const web3 = await getWeb3()

        // Try and enable accounts (connect metamask)
        try {
            const ethereum = await getEthereum()
            ethereum.enable()
        } catch (e) {
            console.log(`Could not enable accounts. Interaction with contracts not available.
            Use a modern browser with a Web3 plugin to fix this issue.`)
            console.log(e)
        }

        // Use web3 to get the user's accounts
        const accounts = await web3.eth.getAccounts()

        // Get the current chain id
        const chainid = parseInt(await web3.eth.getChainId())

        this.setState({
            web3,
            accounts,
            chainid
        }, await this.loadInitialContracts)

    }

    loadInitialContracts = async () => {
        // <=42 to exclude Kovan, <42 to include kovan
        if (this.state.chainid < 42) {
            // Wrong Network!
            return
        }
        console.log(this.state.chainid)
        
        var _chainID = 0;
        if (this.state.chainid === 42){
            _chainID = 42;
        }
        if (this.state.chainid === 1337){
            _chainID = "dev"
        }
        console.log(_chainID)
        const predictionMarket = await this.loadContract(_chainID,"PredictionMarket")

        const bets = await Promise.all([
                    predictionMarket.methods.bets(SIDE.Pacquiao),
                    predictionMarket.methods.bets(SIDE.Marcos)
        ])
        
        const betPredictions = {
                  labels: [
                      'Marcos',
                      'Pacquiao',
                  ],
                  datasets: [{
                      data: [bets[1].toString(), bets[0].toString()],
                      backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                      ],
                      hoverBackgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                      ]
                  }]
        }
        
        const {accounts} = this.state
        const myBets = await Promise.all([
                predictionMarket.methods.betsPerGambler(accounts[0], SIDE.Marcos),
                predictionMarket.methods.betsPerGambler(accounts[0], SIDE.Pacquiao),
        ])
              
        this.setState({
                  predictionMarket,
                  betPredictions,
                  myBets,
        })

    
        if(
            typeof predictionMarket === 'undefined'
            || typeof betPredictions === 'undefined'
            || typeof myBets === 'undefined'
          ) {
            return 'Loading...';
        }

    }

    placeBet = async (side, e) => {
        const {predictionMarket, accounts} = this.state
        e.preventDefault();
        await predictionMarket.methods.placeBet(
          side
        ).send({from: accounts[0]})
    }
    
    withdrawGain = async () => {
        const {predictionMarket, accounts} = this.state
        await predictionMarket.methods.withdraw().send({from: accounts[0]})
    }

    loadContract = async (chain, contractName) => {
        // Load a deployed contract instance into a web3 contract object
        const {web3} = this.state

        // Get the address of the most recent deployment from the deployment map
        let address
        try {
            address = map[chain][contractName][0]
        } catch (e) {
            console.log(`Couldn't find any deployed contract "${contractName}" on the chain "${chain}".`)
            return undefined
        }

        // Load the artifact with the specified address
        let contractArtifact
        try {
            contractArtifact = await import(`./artifacts/deployments/${chain}/${address}.json`)
        } catch (e) {
            console.log(`Failed to load contract artifact "./artifacts/deployments/${chain}/${address}.json"`)
            return undefined
        }

        return new web3.eth.Contract(contractArtifact.abi, address)
    }

    

    render() {
        const {
            web3, accounts, chainid,
            predictionMarket, betPredictions, myBets
        } = this.state

        if (!web3) {
            return <div>Loading Web3, accounts, and contracts...</div>
        }

        // <=42 to exclude Kovan, <42 to include Kovan
        if (isNaN(chainid) || chainid < 42) {
            return <div>Wrong Network! Switch to your local RPC "Localhost: 8545" in your Web3 provider (e.g. Metamask)</div>
        }

        if (!predictionMarket) {
            return <div>Could not find a deployed contract. Check console for details.</div>
        }

        const isAccountsUnlocked = accounts ? accounts.length > 0 : false

        return (<div className='container'>
            <div className='row'>
        <div className='col-sm-12'>
          <h1 className='text-center'>Prediction Market</h1>
          <div className="jumbotron">
            <h1 className="display-4 text-center">Who will win the Phillipines election?</h1>
            <p className="lead text-center">Current odds</p>
            <div>
               <Pie data={betPredictions} />
            </div>
          </div>
        </div>
      </div>

      <div className='row'>
        <div className='col-sm-6'>
          <div className="card">
            <img src='./img/Marcos.png' />
            <div className="card-body">
              <h5 className="card-title">Marcos</h5>
              <form className="form-inline" onSubmit={e => this.placeBet(SIDE.Marcos, e)}>
                <input 
                  type="text" 
                  className="form-control mb-2 mr-sm-2" 
                  placeholder="Bet amount (ether)"
                />
                <button 
                  type="submit" 
                  className="btn btn-primary mb-2"
                >
                  Submit
                </button>
              </form>
            </div>
          </div>
        </div>

        <div className='col-sm-6'>
          <div className="card">
            <img src='./img/Pacquiao.png' />
            <div className="card-body">
              <h5 className="card-title">Pacquiao</h5>
              <form className="form-inline">
                <input 
                  type="text" 
                  className="form-control mb-2 mr-sm-2" 
                  placeholder="Bet amount (ether)"
                />
                <button 
                  type="submit" 
                  className="btn btn-primary mb-2"
                >
                  Submit
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>

      <div className='row'>
        <h2>Your bets</h2>
        <ul>
          <li>Marcos: {myBets[0].toString()} ETH (wei)</li>
          <li>Pacquiao: {myBets[1].toString()} ETH (wei)</li>
        </ul>
      </div>

    <div className='row'>
      <h2>Claim your gains, if any, after the election</h2>
      <button 
        type="submit" 
        className="btn btn-primary mb-2"
        onClick={e => this.withdrawGain()}
      >
        Submit
      </button>
    </div>
        </div>)}
}

export default App
