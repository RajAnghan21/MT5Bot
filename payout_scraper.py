from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

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

    for div in soup.find_all("div", class_="row traded"):
        symbol_div = div.find("div", class_="symbol")
        payout_div = div.find("div", class_="payout__in")

        if symbol_div and payout_div:
            pair = symbol_div.get_text(strip=True)
            payout_text = payout_div.get_text(strip=True).replace('%', '')

            try:
                payout = int(payout_text)
                if 85 <= payout <= 95 and '/' in pair and 'OTC' not in pair.upper():
                    valid_pairs.append(pair)
            except ValueError:
                continue

    return valid_pairs
