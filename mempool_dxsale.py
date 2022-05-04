from web3 import Web3
from pyuniswap.pyuniswap import Token
import time
import json
from datetime import datetime
import threading
from sys import exit
import logging.config
import os

Trini_Limit_low = 600
logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "default",
            "filename": "bot.log.log",
            "mode": "a",
            "encoding": "utf-8"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "console",
            "file"
        ]
    }
})
LOGGER = logging.getLogger()


def show_log(msg):
    LOGGER.info(msg)

class MEMPOOL:
    def __init__(self):
        f = open('config.json')
        data = json.load(f)
        self.provider = data['provider']
        self.w3 = None
        self.provider_wss = data['provider_wss']
        self.wallet_address = data['address']
        self.private_key = data['private_key']
        self.trailing_stop = int(data["trailing_stop"])
        self.new_token = data["new_token_address"]
        self.slippage = int(data["slippage"]) / 100
        gas_price_count = int(data["gas_price"])
        self.gas_price = 1000000000 * gas_price_count
        self.gas_limit = int(data["gas_limit"])
        self.amount = data["amount"] * pow(10, 18)
        self.new_token_presale = data["new_token_server"].lower()
        self.find_token_flag = False

    def connect_wallet(self):
        show_log('Connect wallet...')
        self.current_token = Token(self.new_token, self.provider)
        self.current_token.connect_wallet(self.wallet_address, self.private_key)  # craete token
        self.current_token.set_gaslimit(self.gas_limit)
        if self.current_token.is_connected():
            show_log('Wallet Connected')
            self.w3 = self.current_token.web3
            self.ws_web3 = Web3(Web3.WebsocketProvider(self.provider_wss))
            show_log("WSS is connected : {}".format(self.ws_web3.isConnected()))

    def handle_event(self):
        try:
            self.sell()
        except:
            pass
        return

    def buy(self):  # address:token address.amount:amount for BNB with wei unit
        self.buy_price = 0
        buy_flag = False
        while not buy_flag:
            try:
                start_time = time.time()
                result = self.current_token.send_buy_transaction(self.signed_tx)
                show_log(time.time() - start_time)
                buy_flag = True
                show_log("Buy token: {}".format(result))
            except Exception as error:
                print(error)
                pass
    def sell(self):
        balance = self.current_token.balance()
        sell_flag = False
        while not sell_flag:
            try:
                transaction_addreses = self.current_token.sell(balance, slippage=self.slippage, timeout=2100,
                                                               gas_price=self.gas_price)  # sell token as amount
                show_log("Sell transaction address {}".format(transaction_addreses))
                sell_flag = True
            except:
                pass

    def run(self):
        try:
            self.connect_wallet()
            self.signed_tx = self.current_token.buy(int(self.amount), slippage=self.slippage, timeout=2100,
                                                    gas_price=self.gas_price)  # buy token as amount
            self.handle_event()
        except Exception as err:
            show_log('error; {}'.format(err))


if __name__ == '__main__':
    bot = MEMPOOL()
    bot.run()
