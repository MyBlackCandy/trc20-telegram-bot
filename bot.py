import requests
import time
import os

# ENV
TG_TOKEN = os.getenv("BOT_TOKEN")
TG_CHAT_ID = os.getenv("CHAT_ID")

TRON_ADDRESSES = os.getenv("TRON_ADDRESS", "").split(",")
ETH_ADDRESSES = os.getenv("ETH_ADDRESS", "").split(",")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")

LAST_TX_FILE = "last_txid_store.txt"

def get_latest_trc20_tx(address):
    url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20?limit=1"
    headers = {"accept": "application/json"}
    try:
        r = requests.get(url, headers=headers).json()
        print(f"📦 TRON ล่าสุด ({address}):", r.get("data")[0]["transaction_id"] if r.get("data") else "ไม่มี")
        if r.get("data"):
            return {"type": "TRON", "address": address, "tx": r["data"][0]}
    except Exception as e:
        print("❌ TRON error:", e)
    return None

def get_latest_eth_tx(address):
    url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={address}&page=1&offset=1&sort=desc&apikey={ETHERSCAN_API_KEY}"
    try:
        r = requests.get(url).json()
        print(f"📦 ETH ล่าสุด ({address}):", r["result"][0]["hash"] if r.get("result") else "ไม่มี")
        if r.get("result"):
            return {"type": "ETH", "address": address, "tx": r["result"][0]}
    except Exception as e:
        print("❌ ETH error:", e)
    return None

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = {"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        res = requests.post(url, data=data)
        print("📤 ส่ง Telegram:", res.status_code)
    except Exception as e:
        print("❌ Telegram error:", e)

def load_last_txids():
    if os.path.exists(LAST_TX_FILE):
        with open(LAST_TX_FILE, "r") as f:
            lines = f.read().splitlines()
            return dict(line.split("=", 1) for line in lines if "=" in line)
    return {}

def save_last_txids(txid_map):
    with open(LAST_TX_FILE, "w") as f:
        for k, v in txid_map.items():
            f.write(f"{k}={v}\n")

def format_trc20_msg(tx, watch_addr):
    info = tx["token_info"]
    value = int(tx["value"]) / (10 ** int(info["decimals"]))
    direction = "📥 เข้า" if tx["to"] == watch_addr else "📤 ออก"
    link = f"https://tronscan.org/#/transaction/{tx['transaction_id']}"
    return (
        f"🟥 *TRON แจ้งเตือน {direction}*\n"
        f"`{value} {info['symbol']}`\n"
        f"👤 *จาก:* `{tx['from']}`\n"
        f"👥 *ถึง:* `{tx['to']}`\n"
        f"🔗 [Tronscan]({link})"
    )

def format_eth_msg(tx, watch_addr):
    value = int(tx["value"]) / (10 ** int(tx["tokenDecimal"]))
    direction = "📥 เข้า" if tx["to"].lower() == watch_addr.lower() else "📤 ออก"
    link = f"https://etherscan.io/tx/{tx['hash']}"
    return (
        f"🟦 *ETH แจ้งเตือน {direction}*\n"
        f"`{value} {tx['tokenSymbol']}`\n"
        f"👤 *จาก:* `{tx['from']}`\n"
        f"👥 *ถึง:* `{tx['to']}`\n"
        f"🔗 [Etherscan]({link})"
    )

def monitor():
    print("▶️ เริ่มตรวจสอบ TRON/ETH ทุก 30 วินาที...")
    last_txid_map = load_last_txids()

    while True:
        updated = False

        # TRON
        for addr in TRON_ADDRESSES:
            addr = addr.strip()
            if not addr:
                continue
            result = get_latest_trc20_tx(addr)
            if not result: continue
            tx = result["tx"]
            txid = tx["transaction_id"]
            key = f"TRON_{addr}"
            if last_txid_map.get(key) != txid:
                msg = format_trc20_msg(tx, addr)
                send_telegram_message(msg)
                last_txid_map[key] = txid
                updated = True

        # ETH
        for addr in ETH_ADDRESSES:
            addr = addr.strip()
            if not addr:
                continue
            result = get_latest_eth_tx(addr)
            if not result: continue
            tx = result["tx"]
            txid = tx["hash"]
            key = f"ETH_{addr}"
            if last_txid_map.get(key) != txid:
                msg = format_eth_msg(tx, addr)
                send_telegram_message(msg)
                last_txid_map[key] = txid
                updated = True

        if updated:
            save_last_txids(last_txid_map)

        time.sleep(30)

if __name__ == "__main__":
    monitor()
