import os
import hmac
import time
import random
import base64
import requests
from dotenv import load_dotenv

load_dotenv()
OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_API_SECRET = os.getenv("OKX_API_SECRET")
OKX_API_PASSWORD = os.getenv("OKX_API_PASSWORD")


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


def okx_withdraw(wallet: str, token: str, chain: str, withdraw_range: list, retry=0):

    print(f'[{wallet}] STARTING')

    amount_from = withdraw_range[0]
    amount_to = withdraw_range[1]
    SYMBOL = token


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

            AMOUNT = round(random.uniform(amount_from, amount_to), 4)
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

            return okx_withdraw(wallet=wallet, token=token, chain=chain, withdraw_range=withdraw_range, retry=retry+1)