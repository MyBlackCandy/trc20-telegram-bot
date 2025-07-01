# 🚀 Crypto Income Bot — แจ้งเตือนธุรกรรมเข้าออก ETH, TRC20, BTC แบบ Real-Time ผ่าน Telegram

โปรเจกต์นี้เป็น Telegram Bot สำหรับตรวจจับการโอนเงินเข้า/ออกของเหรียญ:

- 🟣 Ethereum (ETH)
- 🔵 Tron (TRC20 เช่น USDT)
- 🟠 Bitcoin (BTC)

โดยบอทจะตรวจสอบ address ที่คุณกำหนด และส่งข้อความแจ้งเตือนเข้าไปยัง Telegram group หรือ chat ตาม `CHAT_ID` ที่ตั้งค่าไว้

---

## 🎯 คุณสมบัติหลัก

✅ แจ้งเตือนเฉพาะธุรกรรมใหม่ (ไม่ซ้ำ)  
✅ รองรับทั้ง "入" (เงินเข้า) และ "出" (เงินออก)  
✅ แสดงยอดเหรียญ และมูลค่าใน USD (จาก Binance)  
✅ ทำงานอัตโนมัติแบบ loop ทุก 30 วินาที  
✅ รองรับการรันบน Railway หรือ Local

---

## 📂 โครงสร้างโปรเจกต์
crypto-income-bot/
│
├── bot.py # โค้ดหลักของบอท
├── last_seen.txt # เก็บธุรกรรมล่าสุดที่บอทเคยแจ้งไปแล้ว
├── requirements.txt # ไลบรารีที่ต้องติดตั้ง
├── README.md # คู่มือการใช้งาน


---

## ⚙️ ตัวแปรที่ต้องตั้งค่า (Environment Variables)

| ชื่อตัวแปร         | คำอธิบาย |
|--------------------|----------|
| `BOT_TOKEN`        | Bot Token ที่ได้จาก BotFather |
| `CHAT_ID`          | chat_id ของผู้ใช้งานหรือกลุ่ม |
| `ETH_ADDRESS`      | รายการ Ethereum address (คั่นด้วย `,`) |
| `TRON_ADDRESS`     | รายการ TRC20 address (คั่นด้วย `,`) |
| `BTC_ADDRESS`      | รายการ BTC address (คั่นด้วย `,`) |
| `ETHERSCAN_API_KEY`| API Key จาก [etherscan.io](https://etherscan.io/myapikey) |

> ❗ ค่าทั้งหมดสามารถตั้งบน `.env` (ถ้าใช้งาน Local) หรือใน Railway Dashboard ได้

---

## 💻 วิธีติดตั้งและใช้งาน (Local)

1. **Clone โปรเจกต์**

```bash
git clone https://github.com/yourname/crypto-income-bot.git
cd crypto-income-bot
