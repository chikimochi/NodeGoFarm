import requests
import time
import random
from datetime import datetime, timedelta

# Daftar user-agent untuk menghindari deteksi bot
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
]

# Menyimpan waktu terakhir check-in
LAST_CHECKIN = None


def get_ip():
    url = "https://api.bigdatacloud.net/data/client-ip"
    headers = {"user-agent": random.choice(USER_AGENTS)}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("ipString", "Tidak ditemukan")
    except requests.RequestException:
        return "Gagal mendapatkan IP"
    return "Tidak ditemukan"


def get_tokens():
    with open("token.txt", "r") as file:
        return [f"Bearer {line.strip()}" if not line.startswith("Bearer ") else line.strip() for line in file if line.strip()]


def fetch_user_data(token):
    url = "https://nodego.ai/api/user/me"
    headers = {"authorization": token, "user-agent": random.choice(USER_AGENTS)}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None


def daily_checkin(token):
    global LAST_CHECKIN
    if LAST_CHECKIN and datetime.now() - LAST_CHECKIN < timedelta(hours=12):
        return "✅ Sudah check-in hari ini."
    
    url = "https://nodego.ai/api/user/checkin"
    headers = {"authorization": token, "user-agent": random.choice(USER_AGENTS)}
    response = requests.post(url, headers=headers)
    
    if response.status_code == 200:
        LAST_CHECKIN = datetime.now()
        return "✅ Check-in berhasil!"
    elif response.status_code == 400:
        return "✅ Sudah check-in hari ini."
    return "❌ Check-in gagal."


def send_ping(token):
    url = "https://nodego.ai/api/user/nodes/ping"
    headers = {"authorization": token, "user-agent": random.choice(USER_AGENTS)}
    payload = {"type": "extension"}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        return "✅ Ping berhasil!"
    return f"⚠️ Ping gagal! Status: {response.status_code}"


def process_account(token, index):
    user_data = fetch_user_data(token)
    if not user_data or "metadata" not in user_data:
        print(f"⚠️ Token #{index + 1} tidak valid atau tidak bisa mendapatkan data.")
        return
    
    email = user_data["metadata"].get("email", "Tidak ditemukan")
    nodes = user_data["metadata"].get("nodes", [])
    today_point = sum(node.get("todayPoint", 0) for node in nodes)
    total_point = sum(node.get("totalPoint", 0) for node in nodes)
    
    print(f"\n🔹 Token #{index + 1}:")
    print(f"📧 Email: {email}")
    print(f"📊 Today Point: {today_point}")
    print(f"💰 Total Point: {total_point}")
    
    checkin_status = daily_checkin(token)
    print(checkin_status)
    
    delay_before_ping = random.randint(40, 45)
    print(f"⏳ Menunggu {delay_before_ping} detik sebelum ping...")
    time.sleep(delay_before_ping)
    
    print(send_ping(token))
    
    delay_between_accounts = random.randint(5, 10)
    print(f"⏳ Menunggu {delay_between_accounts} detik sebelum akun berikutnya...")
    time.sleep(delay_between_accounts)


if __name__ == "__main__":
    print("🚀 Selamat datang di Airdrop ID - Auto Task NodeGo!")
    
    while True:
        ip_address = get_ip()
        print(f"🌍 IP Publik: {ip_address}\n")
        
        tokens = get_tokens()
        for index, token in enumerate(tokens):
            process_account(token, index)
        
        print("🔄 Menunggu 10 detik sebelum mengulang...")
        time.sleep(10)
