from scripts.helpful_scripts import get_account
from brownie import PredictionMarket, config, network


def deploy_predictionMarket():
    (admin, market) = (get_account(), get_account())

    predictionMarket = PredictionMarket.deploy(
        market,
        {"from": admin},
        publish_source=config["networks"][network.show_active()]["verify"],
    )

    return predictionMarket


def main():
    deploy_predictionMarket()
