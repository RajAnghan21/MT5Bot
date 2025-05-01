import aiohttp
import os

KEYS_FILE = 'keys.txt'
ROUND_ROBIN_FILE = 'key_index.txt'
USAGE_FILE = 'api_usage.txt'

def load_keys():
    with open(KEYS_FILE, 'r') as f:
        return [k.strip() for k in f if k.strip()]

def get_next_key_index(num_keys):
    if not os.path.exists(ROUND_ROBIN_FILE):
        with open(ROUND_ROBIN_FILE, 'w') as f: f.write("0")
        return 0
    with open(ROUND_ROBIN_FILE, 'r') as f:
        idx = int(f.read().strip())
    next_idx = (idx + 1) % num_keys
    with open(ROUND_ROBIN_FILE, 'w') as f:
        f.write(str(next_idx))
    return next_idx

def increment_usage():
    count = 0
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, 'r') as f:
            count = int(f.read().strip() or "0")
    with open(USAGE_FILE, 'w') as f:
        f.write(str(count + 1))

async def fetch_candles(pair, interval):
    keys = load_keys()
    if not keys:
        return []
    key = keys[get_next_key_index(len(keys))]
    url = f"https://api.twelvedata.com/time_series?symbol={pair}&interval={interval}&outputsize=30&apikey={key}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()
                increment_usage()
                if "values" in data:
                    return data["values"]
    except:
        return []
    return []
