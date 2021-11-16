import math
from web3.main import Web3
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account
from brownie import network, accounts, config
import pytest
from scripts.deploy import deploy_predictionMarket


class SIDE:
    Marcos = 0
    Pacquiao = 1


def test_can_pick_winner_correctly_testnet():
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for integration testing")
    owner = get_account()
    gambler1 = accounts.add(config["wallets"]["from_key2"])
    predictionMarket = deploy_predictionMarket()

    # Act
    balanceBefore = gambler1.balance()
    predictionMarket.startMarket({"from": owner})
    tx = predictionMarket.placeBet(
        SIDE.Marcos,
        {
            "from": gambler1,
            "value": predictionMarket.getEntranceFee(),
        },
    )
    tx.wait(1)

    result_tx = predictionMarket.reportResult(
        SIDE.Marcos, SIDE.Pacquiao, {"from": owner}
    )
    result_tx.wait(1)

    # No win
    balanceAfter = gambler1.balance()

    # Assert
    # Round down to factor gas fee
    assert math.floor(Web3.fromWei(abs(balanceAfter - balanceBefore), "ether")) == 0
