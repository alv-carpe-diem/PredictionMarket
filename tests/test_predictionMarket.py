from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account
from scripts.deploy import deploy_predictionMarket
from brownie import accounts, exceptions, network
from web3 import Web3
import pytest


class SIDE:
    Marcos = 0
    Pacquiao = 1


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    # Arrange
    predictionMarket = deploy_predictionMarket()

    # Act
    # 2000 eth / usd
    # usdEntryFee is 50
    # 2000/1 = 50/x => x=0.025
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = predictionMarket.getEntranceFee()
    # Assert
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    # Arrange
    predictionMarket = deploy_predictionMarket()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        predictionMarket.placeBet(
            SIDE.Marcos,
            {"from": accounts[1], "value": predictionMarket.getEntranceFee()},
        )


def test_can_start_and_placeBet():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    # Arrange
    owner = get_account()
    gambler1 = accounts[1]
    predictionMarket = deploy_predictionMarket()

    # Act
    predictionMarket.startMarket({"from": owner})
    predictionMarket.placeBet(
        SIDE.Marcos, {"from": gambler1, "value": predictionMarket.getEntranceFee()}
    )

    # Assert
    assert predictionMarket.s_players(0) == gambler1


def test_can_report_result():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    predictionMarket = deploy_predictionMarket()
    owner = get_account()
    gambler1 = accounts[1]
    # Act
    predictionMarket.startMarket({"from": owner})
    predictionMarket.placeBet(
        SIDE.Marcos, {"from": gambler1, "value": predictionMarket.getEntranceFee()}
    )
    predictionMarket.reportResult(SIDE.Marcos, SIDE.Pacquiao, {"from": owner})
    # Assert
    assert predictionMarket.market_state() == 3


def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    # Arrange
    owner = get_account()
    (gambler1, gambler2, gambler3, gambler4) = accounts[1:5]
    predictionMarket = deploy_predictionMarket()

    # Act
    predictionMarket.startMarket({"from": owner})
    predictionMarket.placeBet(
        SIDE.Marcos, {"from": gambler1, "value": predictionMarket.getEntranceFee()}
    )
    predictionMarket.placeBet(
        SIDE.Pacquiao, {"from": gambler2, "value": predictionMarket.getEntranceFee()}
    )
    predictionMarket.placeBet(
        SIDE.Marcos, {"from": gambler3, "value": predictionMarket.getEntranceFee()}
    )
    predictionMarket.placeBet(
        SIDE.Marcos, {"from": gambler4, "value": predictionMarket.getEntranceFee()}
    )

    balanceBefore = {
        "gambler1": gambler1.balance(),
        "gambler2": gambler2.balance(),
        "gambler3": gambler3.balance(),
        "gambler4": gambler4.balance(),
    }

    predictionMarket.reportResult(SIDE.Marcos, SIDE.Pacquiao, {"from": owner})

    balanceAfter = {
        "gambler1": gambler1.balance(),
        "gambler2": gambler2.balance(),
        "gambler3": gambler3.balance(),
        "gambler4": gambler4.balance(),
    }

    # Assert
    assert (
        balanceAfter["gambler1"] - balanceBefore["gambler1"]
    ) > predictionMarket.getEntranceFee()
    assert (balanceAfter["gambler2"] - balanceBefore["gambler2"]) == 0
    assert (
        balanceAfter["gambler3"] - balanceBefore["gambler3"]
    ) > predictionMarket.getEntranceFee()
    assert (
        balanceAfter["gambler4"] - balanceBefore["gambler4"]
    ) > predictionMarket.getEntranceFee()


def test_bet_and_betspergambler_arrays():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    # Arrange
    owner = get_account()
    (gambler1, gambler2, gambler3, gambler4) = accounts[1:5]
    predictionMarket = deploy_predictionMarket()

    # Act
    predictionMarket.startMarket({"from": owner})
    predictionMarket.placeBet(
        SIDE.Marcos, {"from": gambler1, "value": predictionMarket.getEntranceFee()}
    )
    predictionMarket.placeBet(
        SIDE.Pacquiao, {"from": gambler2, "value": predictionMarket.getEntranceFee()}
    )
    predictionMarket.placeBet(
        SIDE.Marcos, {"from": gambler3, "value": predictionMarket.getEntranceFee()}
    )
    predictionMarket.placeBet(
        SIDE.Marcos, {"from": gambler4, "value": predictionMarket.getEntranceFee()}
    )

    # Assert
    assert predictionMarket.Bets(SIDE.Marcos) == 3 * predictionMarket.getEntranceFee()
    assert predictionMarket.Bets(SIDE.Pacquiao) == predictionMarket.getEntranceFee()

    assert (
        predictionMarket.MyBets(SIDE.Marcos, {"from": gambler1})
        == predictionMarket.getEntranceFee()
    )

    assert predictionMarket.MyBets(SIDE.Pacquiao, {"from": gambler1}) == 0
