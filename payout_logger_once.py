import asyncio
from payout_scraper_debug import fetch_payouts  # Make sure you're using the debug version

async def run_once():
    pairs = await fetch_payouts()
    print("[RESULT]", pairs)

if __name__ == "__main__":
    asyncio.run(run_once())
