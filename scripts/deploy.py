from scripts.helpful_scripts import get_account, get_contract
from brownie import PredictionMarket, config, network


def deploy_predictionMarket():
    owner = get_account()

    predictionMarket = PredictionMarket.deploy(
        owner,
        get_contract("eth_usd_price_feed").address,
        {"from": owner},
        publish_source=config["networks"][network.show_active()]["verify"],
    )

    return predictionMarket


def main():
    deploy_predictionMarket()
