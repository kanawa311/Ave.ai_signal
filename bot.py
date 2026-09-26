import os
import asyncio
import httpx
from aiohttp import web
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

# INJIN WANKI: Wannan zai goge duk wani boyayyen harafi daga Environment Variables dinka
def clean_key(key_name, default_val=''):
    val = os.environ.get(key_name, default_val)
    return str(val).replace('\u200e', '').replace('\u200f', '').strip()

API_ID = int(clean_key('TELEGRAM_API_ID', '0'))
API_HASH = clean_key('TELEGRAM_API_HASH')
SESSION_STRING = clean_key('TELEGRAM_SESSION_STRING')
TRADING_BOT = clean_key('TRADING_BOT_USERNAME', '@trojan_on_solana')

AVE_UDID = clean_key('AVE_UDID')
X_AUTH = clean_key('X_AUTH_TOKEN')

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

AVE_API_URL = "https://primpom.com/v2api/signals/v2/public/list/v2?pageNO=1&pageSize=20&chain=solana"

seen_tokens = set()

async def handle_web_request(request):
    return web.Response(text="Ave.ai Sniper Bot yana aiki lafiya lau!")

async def start_dummy_server():
    app = web.Application()
    app.add_routes([web.get('/', handle_web_request)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Server ya tashi a port {port}")

def get_headers():
    return {
        "Accept": "application/json, text/plain, */*",
        "ave-platform": "h5",
        "app-version-name": "1.0.0",
        "lang": "en", 
        "lang-zone": "en", 
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
        "ave-udid": AVE_UDID,
        "X-Auth": X_AUTH
    }

async def fetch_and_send_signals():
    print("🚀 An fara farautar CA (An sa kariyar kar ya sayi tsofaffi!)...")
    
    is_first_run = True 
    
    async with httpx.AsyncClient() as http_client:
        while True:
            try:
                response = await http_client.get(AVE_API_URL, headers=get_headers(), timeout=5.0)
                res = response.json()
                
                if res.get("status") == 1:
                    signals = res.get("data", [])
                    
                    for signal in signals:
                        token_address = signal.get("token") or signal.get("address")
                        
                        if token_address and token_address not in seen_tokens:
                            seen_tokens.add(token_address)
                            
                            if not is_first_run:
                                print(f"🚨 SABO: {token_address}")
                                await client.send_message(TRADING_BOT, token_address)
                                print(f"✅ An aika CA zuwa {TRADING_BOT}")
                                await asyncio.sleep(0.5)
                    
                    if is_first_run:
                        print("🛡️ An kwashe tsofaffin tokens an sa a memory. Yanzu zai jira sabbi kawai...")
                        is_first_run = False
                            
                    if len(seen_tokens) > 1000:
                        seen_tokens.clear()
                        is_first_run = True 
                        print("🧹 An goge memory don kar ya cika, an sake kunna kariya.")
                        
                else:
                    print(f"❌ API Error: {res.get('msg')}")
                
                await asyncio.sleep(1.0)
                
            except Exception as e:
                print(f"⚠️ Kuskure: {e}")
                await asyncio.sleep(3.0)

async def main():
    await start_dummy_server()
    await client.start()
    print("✅ Telegram ta hadu!")
    await fetch_and_send_signals()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
