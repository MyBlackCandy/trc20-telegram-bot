import requests
import time
import os

TG_TOKEN = os.getenv("BOT_TOKEN")
TG_CHAT_ID = os.getenv("CHAT_ID")
TRON_ADDRESSES = os.getenv("TRON_ADDRESS", "").split(",")

LAST_TX_FILE = "last_trx_id_multi.txt"

def get_latest_trc20_tx(address):
    url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20?limit=1"
    headers = {"accept": "application/json"}
    try:
        r = requests.get(url, headers=headers).json()
        print(f"📦 ตรวจล่าสุด ({address}):", r.get("data")[0]["transaction_id"] if r.get("data") else "ไม่มี")
        if r.get("data"):
            return r["data"][0]
    except Exception as e:
        print(f"❌ ERROR API:", e)
    return None

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, data=data)
        print("📤 ส่ง Telegram:", res.status_code)
    except Exception as e:
        print(f"❌ ERROR Telegram:", e)

def load_last_txids():
    if os.path.exists(LAST_TX_FILE):
        with open(LAST_TX_FILE, "r") as f:
            lines = f.read().splitlines()
            return dict(line.split("=", 1) for line in lines if "=" in line)
    return {}

def save_last_txids(txid_map):
    with open(LAST_TX_FILE, "w") as f:
        for addr, txid in txid_map.items():
            f.write(f"{addr}={txid}\n")

def format_tx_message(tx, watch_addr):
    symbol = tx["token_info"]["symbol"]
    value = int(tx["value"]) / (10 ** int(tx["token_info"]["decimals"]))
    from_addr = tx["from"]
    to_addr = tx["to"]
    tx_id = tx["transaction_id"]
    direction = "📥 เข้า" if to_addr == watch_addr else "📤 ออก"
    link = f"https://tronscan.org/#/transaction/{tx_id}"
    return (
        f"🔔 *{direction}* `{value}` {symbol}\n"
        f"👤 *จาก:* `{from_addr}`\n"
        f"👥 *ถึง:* `{to_addr}`\n"
        f"🔗 [ดูบน Tronscan]({link})"
    )

def monitor():
    print("▶️ เริ่มตรวจสอบ TRC20 หลาย address ทุก 30 วินาที")
    print("📌 MONITOR:", TRON_ADDRESSES)
    print("📨 ไปที่ CHAT_ID:", TG_CHAT_ID)

    last_txid_map = load_last_txids()

    while True:
        updated = False
        for addr in TRON_ADDRESSES:
            addr = addr.strip()
            if not addr:
                continue
            tx = get_latest_trc20_tx(addr)
            if not tx:
                continue
            txid = tx["transaction_id"]
            if last_txid_map.get(addr) != txid:
                msg = format_tx_message(tx, addr)
                send_telegram_message(msg)
                last_txid_map[addr] = txid
                updated = True
        if updated:
            save_last_txids(last_txid_map)
        time.sleep(30)

if __name__ == "__main__":
    monitor()
