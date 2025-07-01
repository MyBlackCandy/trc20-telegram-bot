import os
import time
import requests

TG_TOKEN = os.getenv("BOT_TOKEN")
TG_CHAT_ID = os.getenv("CHAT_ID")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETH_ADDRESSES = os.getenv("ETH_ADDRESS", "").split(",")
TRON_ADDRESSES = os.getenv("TRON_ADDRESS", "").split(",")
BTC_ADDRESSES = os.getenv("BTC_ADDRESS", "").split(",")

LAST_TX_FILE = "last_seen.txt"

def send_message(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = {"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram ERROR:", e)

def get_price(symbol):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}").json()
        return float(r["price"])
    except:
        return 0

def get_latest_eth_tx(address):
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey={ETHERSCAN_API_KEY}"
    try:
        r = requests.get(url).json()
        for tx in r.get("result", []):
            return tx
    except:
        pass
    return None

def get_latest_tron_tx(address):
    url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20?limit=1"
    try:
        r = requests.get(url, headers={"accept": "application/json"}).json()
        for tx in r.get("data", []):
            return tx
    except:
        pass
    return None

def get_latest_btc_tx(address):
    url = f"https://blockchain.info/rawaddr/{address}"
    try:
        r = requests.get(url).json()
        for tx in r.get("txs", []):
            for out in tx["out"]:
                if out.get("addr") == address:
                    return tx
    except:
        pass
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
        eth_price = get_price("ETHUSDT")
        btc_price = get_price("BTCUSDT")

        # ETH
        for eth in ETH_ADDRESSES:
            eth = eth.strip()
            tx = get_latest_eth_tx(eth)
            if tx and tx.get("hash") and tx["hash"] != last_seen.get(eth):
                value_eth = int(tx["value"]) / 1e18
                usd = value_eth * eth_price
                direction = "入" if tx["to"].lower() == eth.lower() else "出"
                msg = f"""🟢 *ETH {direction}*
👤 从: `{tx['from']}`
👥 到: `{tx['to']}`
💰 {value_eth:.6f} ETH ≈ ${usd:,.2f}"""
                send_message(msg)
                last_seen[eth] = tx["hash"]
                updated = True

        # TRON
        for tron in TRON_ADDRESSES:
            tron = tron.strip()
            tx = get_latest_tron_tx(tron)
            if tx and tx.get("transaction_id") and tx["transaction_id"] != last_seen.get(tron):
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

        # BTC
        for btc in BTC_ADDRESSES:
            btc = btc.strip()
            tx = get_latest_btc_tx(btc)
            if tx and tx.get("hash") and tx["hash"] != last_seen.get(btc):
                total = sum(out["value"] for out in tx["out"] if out.get("addr") == btc) / 1e8
                usd_val = total * btc_price
                from_addr = tx.get("inputs", [{}])[0].get("prev_out", {}).get("addr", "不明")
                msg = f"""🟢 *BTC 入金*
👤 从: `{from_addr}`
👥 到: `{btc}`
💰 {total:.8f} BTC ≈ ${usd_val:,.2f}
🧾 TXID: `{tx['hash']}`"""
                send_message(msg)
                last_seen[btc] = tx["hash"]
                updated = True

        if updated:
            save_last_txids(last_seen)
        time.sleep(10)

if __name__ == "__main__":
    main()
