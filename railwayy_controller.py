import requests, time, os, json

RAILWAY_URL = os.getenv("RAILWAY_WORKER_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not RAILWAY_URL or not OPENROUTER_API_KEY:
    print("Missing environment variables!")
    exit()

print("🚀 StudySmart AI Railway Controller starting...")

def start_batch():
    r = requests.post(f"{RAILWAY_URL}/start")
    print("Start response:", r.status_code, r.text)

def poll_status():
    while True:
        try:
            s = requests.get(f"{RAILWAY_URL}/status")
            data = s.json()
            print("Progress:", json.dumps(data, indent=2))
            if data.get("done"): break
        except Exception as e:
            print("Error:", e)
        time.sleep(30)

start_batch()
poll_status()
print("✅ All lessons generated successfully!")