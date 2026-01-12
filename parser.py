import os, requests, sys

TOKEN = os.getenv('TG_TOKEN', '7521422533:AAE2UaEpXpH8yh22gM2nAy3iQKg2EqAkYts')
CHAT = os.getenv('TG_CHAT', '819701342')

def send(msg):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    try:
        r = requests.post(url, json={
            'chat_id': CHAT,
            'text': msg,
            'parse_mode': 'HTML'
        }, timeout=10)
        print(f"Status: {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

print("=== START ===")
print(f"Token: ***{TOKEN[-4:]}")
print(f"Chat: {CHAT}")

if send("✅ <b>РАБОТАЕТ!</b>\nПарсер запущен с GitHub Actions"):
    print("✅ SUCCESS")
    sys.exit(0)
else:
    print("❌ FAILED")
    sys.exit(1)
