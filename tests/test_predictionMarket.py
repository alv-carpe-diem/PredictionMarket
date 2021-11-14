from scripts.helpful_scripts import get_account
from brownie import PredictionMarket, accounts, exceptions
from web3 import Web3
import pytest


class SIDE:
    Marcos = 0
    Pacquiao = 1


def test_can_bet_and_withdraw_win():
    # Arrange
    admin = get_account()
    market = accounts[1]
    (gambler1, gambler2, gambler3, gambler4) = accounts[2:6]
    predictionMarket = PredictionMarket.deploy(market, {"from": admin})

    # Act
    tx1 = predictionMarket.placeBet(
        SIDE.Marcos, {"from": gambler1, "value": Web3.toWei(1, "ether")}
    )
    tx1.wait(1)

    tx2 = predictionMarket.placeBet(
        SIDE.Pacquiao, {"from": gambler2, "value": Web3.toWei(2, "ether")}
    )
    tx2.wait(1)

    tx3 = predictionMarket.placeBet(
        SIDE.Marcos, {"from": gambler3, "value": Web3.toWei(1, "ether")}
    )
    tx3.wait(1)

    tx4 = predictionMarket.placeBet(
        SIDE.Marcos, {"from": gambler4, "value": Web3.toWei(3, "ether")}
    )
    tx4.wait(1)

    balanceBefore = {
        "gambler1": gambler1.balance(),
        "gambler2": gambler2.balance(),
        "gambler3": gambler3.balance(),
        "gambler4": gambler4.balance(),
    }

    result_tx = predictionMarket.reportResult(
        SIDE.Marcos, SIDE.Pacquiao, {"from": market}
    )

    # Withdrawing gains for winners
    gamblersWon = [gambler1, gambler3, gambler4]
    for gambler in gamblersWon:
        tx = predictionMarket.withdraw({"from": gambler})
        tx.wait(1)

    balanceAfter = {
        "gambler1": gambler1.balance(),
        "gambler2": gambler2.balance(),
        "gambler3": gambler3.balance(),
        "gambler4": gambler4.balance(),
    }

    # Assert
    assert (balanceAfter["gambler1"] - balanceBefore["gambler1"]) > Web3.toWei(
        1, "ether"
    )
    assert (balanceAfter["gambler2"] - balanceBefore["gambler2"]) == 0
    assert (balanceAfter["gambler3"] - balanceBefore["gambler3"]) > Web3.toWei(
        1, "ether"
    )
    assert (balanceAfter["gambler4"] - balanceBefore["gambler4"]) > Web3.toWei(
        3, "ether"
    )


def test_only_market_can_reportResult():
    # Arrange
    admin = get_account()
    market = accounts[1]
    (gambler1, gambler2, gambler3, gambler4) = accounts[2:6]
    predictionMarket = PredictionMarket.deploy(market, {"from": admin})
    # Act/Assert
    with pytest.raises(exceptions.VirtualMachineError):
        predictionMarket.reportResult(SIDE.Marcos, SIDE.Pacquiao, {"from": gambler1})
