import time
from payout_scraper import fetch_payouts

import asyncio

async def log_pairs_forever():
    while True:
        pairs = await fetch_payouts()
        print("[LOG] Fetched pairs:", pairs)
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(log_pairs_forever())
