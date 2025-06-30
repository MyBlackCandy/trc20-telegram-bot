import os
import time
import requests

TG_TOKEN = os.getenv("BOT_TOKEN")
TG_CHAT_ID = os.getenv("CHAT_ID")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETH_ADDRESSES = os.getenv("ETH_ADDRESS", "").split(",")
TRON_ADDRESSES = os.getenv("TRON_ADDRESS", "").split(",")

LAST_TX_FILE = "last_seen.txt"

def send_message(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = {"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram ERROR:", e)

def get_latest_eth_tx(address):
    try:
        url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey={ETHERSCAN_API_KEY}"
        res = requests.get(url).json()
        txs = res.get("result", [])
        return txs[0] if txs else None
    except Exception as e:
        print("ETH API ERROR:", e)
    return None

def get_latest_tron_tx(address):
    try:
        url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20?limit=1"
        res = requests.get(url, headers={"accept": "application/json"}).json()
        txs = res.get("data", [])
        return txs[0] if txs else None
    except Exception as e:
        print("TRON API ERROR:", e)
    return None

def load_last_txids():
    if not os.path.exists(LAST_TX_FILE):
        return {}
    with open(LAST_TX_FILE, "r") as f:
        return dict(line.strip().split("=", 1) for line in f if "=" in line)

def save_last_txids(txid_map):
    with open(LAST_TX_FILE, "w") as f:
        for k, v in txid_map.items():
            f.write(f"{k}={v}\n")

def main():
    last_seen = load_last_txids()
    while True:
        updated = False

        for eth in ETH_ADDRESSES:
            eth = eth.strip()
            tx = get_latest_eth_tx(eth)
            if isinstance(tx, dict) and tx.get("hash") and tx["hash"] != last_seen.get(eth):
                direction = "入" if tx["to"].lower() == eth.lower() else "出"
                msg = f"""🟢 *ETH {direction}*
👤 从: `{tx['from']}`
👥 到: `{tx['to']}`
💰 {int(tx['value']) / 1e18:.6f} ETH"""
                send_message(msg)
                last_seen[eth] = tx["hash"]
                updated = True

        for tron in TRON_ADDRESSES:
            tron = tron.strip()
            tx = get_latest_tron_tx(tron)
            if isinstance(tx, dict) and tx.get("transaction_id") and tx["transaction_id"] != last_seen.get(tron):
                val = int(tx["value"]) / (10**int(tx["token_info"]["decimals"]))
                symbol = tx["token_info"]["symbol"]
                direction = "入" if tx["to"] == tron else "出"
                msg = f"""🟢 *TRC20 {direction}*
👤 从: `{tx['from']}`
👥 到: `{tx['to']}`
💰 {val:.6f} {symbol}"""
                send_message(msg)
                last_seen[tron] = tx["transaction_id"]
                updated = True

        if updated:
            save_last_txids(last_seen)
        time.sleep(30)

if __name__ == "__main__":
    main()
