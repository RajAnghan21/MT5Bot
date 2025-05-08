from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# CONFIG: Filter range
MIN_PAYOUT = 85
MAX_PAYOUT = 95

POCKET_OPTION_URL = "https://m.pocketoption.com/en/assets-current/"

async def fetch_payouts():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(POCKET_OPTION_URL, timeout=90000)
            await page.wait_for_timeout(10000)

            html = await page.content()
            await browser.close()
            return parse_payouts(html)
    except Exception as e:
        print(f"[PAYOUT] Error fetching payouts: {e}")
        return []

def parse_payouts(html):
    soup = BeautifulSoup(html, 'html.parser')
    valid_pairs = []

    print("------ DEBUG START ------")
    rows = soup.find_all("div", class_="row traded")
    print("Total 'row traded' divs found:", len(rows))

    for div in rows:
        symbol_div = div.find("div", class_="symbol")
        payout_div = div.find("div", class_="payout__in")

        if symbol_div and payout_div:
            pair = symbol_div.get_text(strip=True)
            payout_text = payout_div.get_text(strip=True).replace('%', '')

            try:
                payout = int(payout_text)
                is_forex = '/' in pair
                is_not_otc = 'OTC' not in pair.upper()
                if MIN_PAYOUT <= payout <= MAX_PAYOUT and is_forex and is_not_otc:
                    print(f"[PASS] {pair} | {payout}%")
                    valid_pairs.append(pair)
                else:
                    print(f"[SKIP] {pair} | {payout}%")
            except ValueError:
                print(f"[ERROR] Skipping invalid payout: {payout_text}")

    print("------ FINAL FILTERED PAIRS ------")
    print(valid_pairs)
    print("------ DEBUG END ------")
    return valid_pairs
