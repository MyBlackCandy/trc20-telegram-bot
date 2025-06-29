import os
import time
import requests

TG_TOKEN = os.getenv("BOT_TOKEN")
TG_CHAT_ID = os.getenv("CHAT_ID")
ETH_ADDRESSES = os.getenv("ETH_ADDRESS", "").split(",")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
TRON_ADDRESSES = os.getenv("TRON_ADDRESS", "").split(",")

LAST_TX_FILE = "last_eth_tron.txt"

def get_latest_eth_tx(address):
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey={ETHERSCAN_API_KEY}"
    try:
        r = requests.get(url).json()
        txs = r.get("result", [])
        if txs:
            return txs[0]
    except Exception as e:
        print("ETH ERROR:", e)
    return None

def get_latest_trc20_tx(address):
    url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20?limit=1"
    try:
        r = requests.get(url, headers={"accept": "application/json"}).json()
        txs = r.get("data", [])
        if txs:
            return txs[0]
    except Exception as e:
        print("TRON ERROR:", e)
    return None

def send_message(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = {"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("TG ERROR:", e)

def load_last_txids():
    if os.path.exists(LAST_TX_FILE):
        with open(LAST_TX_FILE, "r") as f:
            lines = f.read().splitlines()
            return dict(line.split("=", 1) for line in lines if "=" in line)
    return {}

def save_last_txids(txid_map):
    with open(LAST_TX_FILE, "w") as f:
        for addr, txid in txid_map.items():
            f.write(f"{addr}={txid}
")

def main():
    last_map = load_last_txids()
    while True:
        updated = False
        for eth in ETH_ADDRESSES:
            eth = eth.strip()
            tx = get_latest_eth_tx(eth)
            if tx and tx["hash"] != last_map.get(eth):
                link = f"https://etherscan.io/tx/{tx['hash']}"
                send_message(f"🔔 *ETH {tx['from']} → {tx['to']}*
💰 {int(tx['value'])/1e18:.6f} ETH
🔗 [TX Link]({link})")
                last_map[eth] = tx["hash"]
                updated = True
        for tron in TRON_ADDRESSES:
            tron = tron.strip()
            tx = get_latest_trc20_tx(tron)
            if tx and tx["transaction_id"] != last_map.get(tron):
                val = int(tx["value"]) / (10**int(tx["token_info"]["decimals"]))
                symbol = tx["token_info"]["symbol"]
                txid = tx["transaction_id"]
                link = f"https://tronscan.org/#/transaction/{txid}"
                send_message(f"🔔 *TRON {tx['from']} → {tx['to']}*
💰 {val} {symbol}
🔗 [TX Link]({link})")
                last_map[tron] = txid
                updated = True
        if updated:
            save_last_txids(last_map)
        time.sleep(30)

if __name__ == "__main__":
    main()
