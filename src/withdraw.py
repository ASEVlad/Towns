import os
import hmac
import time
import random
import base64
import requests
from web3 import Web3
from typing import List
from loguru import logger
from binance import Client
from dotenv import load_dotenv


def okx_data(api_key, secret_key, passphras, request_path="/api/v5/account/balance?ccy=USDT", body='', meth="GET"):

    try:
        import datetime
        def signature(
            timestamp: str, method: str, request_path: str, secret_key: str, body: str = ""
        ) -> str:
            if not body:
                body = ""

            message = timestamp + method.upper() + request_path + body
            mac = hmac.new(
                bytes(secret_key, encoding="utf-8"),
                bytes(message, encoding="utf-8"),
                digestmod="sha256",
            )
            d = mac.digest()
            return base64.b64encode(d).decode("utf-8")

        dt_now = datetime.datetime.utcnow()
        ms = str(dt_now.microsecond).zfill(6)[:3]
        timestamp = f"{dt_now:%Y-%m-%dT%H:%M:%S}.{ms}Z"

        base_url = "https://www.okex.com"
        headers = {
            "Content-Type": "application/json",
            "OK-ACCESS-KEY": api_key,
            "OK-ACCESS-SIGN": signature(timestamp, meth, request_path, secret_key, body),
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": passphras,
            'x-simulated-trading': '0'
        }
    except Exception as ex:
        print(f'[-] OKX DATA ERROR: {ex}')
    return base_url, request_path, headers


def okx_withdraw(wallet: str, withdraw_range: list, token: str, chain: str, retry=0):
    load_dotenv()
    OKX_API_KEY = os.getenv("OKX_API_KEY")
    OKX_API_SECRET = os.getenv("OKX_API_SECRET")
    OKX_API_PASSWORD = os.getenv("OKX_API_PASSWORD")

    amount_from = withdraw_range[0]
    amount_to = withdraw_range[1]
    SYMBOL = token
    if "arbitrum" in chain.lower(): chain = "Arbitrum One"
    if "base" in chain.lower(): chain = "Base"

    try:
        # take FEE for withdraw
        _, _, headers = okx_data(OKX_API_KEY, OKX_API_SECRET, OKX_API_PASSWORD, request_path=f"/api/v5/asset/currencies?ccy={SYMBOL}", meth="GET")
        response = requests.get(f"https://www.okx.cab/api/v5/asset/currencies?ccy={SYMBOL}", timeout=10, headers=headers)
        for lst in response.json()['data']:
            if lst['chain'] == f'{SYMBOL}-{chain}':
                FEE = lst['minFee']

        while True:
            # CHECK MAIN BALANCE
            _, _, headers = okx_data(OKX_API_KEY, OKX_API_SECRET, OKX_API_PASSWORD,
                                     request_path=f"/api/v5/asset/balances?ccy={SYMBOL}", meth="GET")
            main_balance = requests.get(f'https://www.okx.cab/api/v5/asset/balances?ccy={SYMBOL}', timeout=10,
                                        headers=headers)
            main_balance = main_balance.json()
            main_balance = float(main_balance["data"][0]['availBal'])
            print(f'OKX total balance | {main_balance} {SYMBOL}')

            if amount_from > main_balance:
                print(f'OKX not enough balance ({main_balance} < {amount_from}), waiting 10 secs...')
                time.sleep(10)
                continue

            if amount_to > main_balance:
                print(f'you want to withdraw MAX {amount_to} but have only {round(main_balance, 7)}')
                amount_to = main_balance

            AMOUNT = round(random.uniform(amount_from, amount_to), 5)
            break

        body = {"ccy":SYMBOL, "amt":AMOUNT, "fee":FEE, "dest":"4", "chain":f"{SYMBOL}-{chain}", "toAddr":wallet}
        _, _, headers = okx_data(OKX_API_KEY, OKX_API_SECRET, OKX_API_PASSWORD, request_path=f"/api/v5/asset/withdrawal", meth="POST", body=str(body))
        a = requests.post("https://www.okx.cab/api/v5/asset/withdrawal",data=str(body), timeout=10, headers=headers)
        result = a.json()
        # cprint(result, 'blue')

        if result['code'] == '0':
            print(f"[+] OKX withdraw success => {wallet} | {AMOUNT} {SYMBOL}")
            return AMOUNT
        else:
            error = result['msg']
            print(f"[-] OKX withdraw unsuccess => {wallet} | error : {error}")
            if retry < 2:
                return okx_withdraw(wallet=wallet, token=token, chain=chain, withdraw_range=withdraw_range, retry=retry+1)

    except Exception as error:
        print(f"[-] OKX withdraw unsuccess => {wallet} | error : {error}")

        try: print(f'response: {response.json()}')
        except: pass

        if retry < 2:
            print(f"try again in 10 sec. => {wallet}")
            time.sleep(10)
            if 'Insufficient balance' in str(error): return okx_withdraw(wallet=wallet, token=token, chain=chain, withdraw_range=withdraw_range, retry=retry)

            return okx_withdraw(wallet=wallet, withdraw_range=withdraw_range, token=token, chain=chain, retry=retry+1)


def binance_withdraw(wallet: str, withdraw_range: List, token: str = "ETH", network: str = "BASE"):
    try:
        binance_client = binance_client_init()

        ETH_to_send = random.uniform(withdraw_range[0], withdraw_range[1])
        check_binance_balance(binance_client, "ETH", ETH_to_send)
        time.sleep(0.5)

        binance_client.withdraw(
            coin=token,
            network=network.upper(),
            address=wallet,
            amount=round(ETH_to_send, 6)
        )

        logger.info(f"Binance: {ETH_to_send :.6f} ETH has been sent to wallet")
        return ETH_to_send
    except Exception as e:
        logger.error(f"Binance: {e}")

def check_binance_balance(binance_client: Client, symbol: str, amount_to_check: float):
    balance = float(binance_client.get_asset_balance(asset=symbol)["free"])
    if balance < amount_to_check * 0.98:
        logger.error(f"Binance: NOT ENOUGH FUNDS. {symbol} balance is {balance:.2f} ETH")
        raise

def binance_client_init() -> Client:
    try:
        load_dotenv()
        API_KEY = os.getenv("BINANCE_API_KEY")
        API_SECRET = os.getenv("BINANCE_API_SECRET")
        binance_client = Client(API_KEY, API_SECRET)

        return binance_client
    except Exception as e:
        logger.error(f"Binance: {e}")
        raise

import time
from web3 import Web3

# RPC URLs for supported networks
RPC_URLS = {
    "BASE": "https://mainnet.base.org",
    "ARBITRUM": "https://arb1.arbitrum.io/rpc",
}

def wait_for_balance(wallet: str, check_balance: float, network: str = "base", max_time_to_wait: int = 30) -> bool:
    """
    Waits until the wallet's ETH balance on the given network is at least 95% of the check_balance,
    or until max_time_to_wait seconds have passed.

    Parameters:
    - wallet (str): Wallet address to check.
    - check_balance (float): Desired ETH balance to wait for (in ETH).
    - network (str): Either 'base' or 'arbitrum'.
    - max_time_to_wait (int): Max seconds to wait before giving up.

    Returns:
    - bool: True if the balance condition was met, False if timeout occurred.
    """
    if network.upper() not in {"BASE", "ARBITRUM"}:
        raise ValueError("Invalid network. Only 'base' or 'arbitrum' are supported.")

    web3 = Web3(Web3.HTTPProvider(RPC_URLS[network.upper()]))
    if not web3.is_connected():
        raise ConnectionError(f"Failed to connect to {network} network.")

    required_balance_wei = Web3.to_wei(check_balance * 0.95, 'ether')
    deadline = time.time() + max_time_to_wait

    while time.time() < deadline:
        balance_wei = web3.eth.get_balance(wallet)
        if balance_wei >= required_balance_wei:
            logger.info(f"Wallet {wallet} is filled. Current funds: {Web3.from_wei(balance_wei, 'ether')} ETH")
            return True
        else:
            time.sleep(3)

    logger.warning(f"Funds still not arrived on wallet {wallet} after {max_time_to_wait} seconds. Giving up..")
    return False
