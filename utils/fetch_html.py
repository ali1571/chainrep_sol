import requests
from bs4 import BeautifulSoup
import time
import random

'''
Ideas for Later Enhancements
Add proxy support or rotate headers
Raise/log errors in a debug.log
Add HEAD requests to test endpoint availability
'''

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/113.0.0.0 Safari/537.36"
    )
}

MAX_RETRIES = 3
RETRY_DELAY = [1, 2, 3]  # seconds


def get_html(url: str, sleep_on_success=True) -> BeautifulSoup:
    """Fetch HTML from a URL and return BeautifulSoup object."""
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                if sleep_on_success:
                    time.sleep(random.uniform(0.5, 1.2))
                return BeautifulSoup(resp.text, "html.parser")
            else:
                print(f"[WARN] Non-200 status {resp.status_code} on attempt {attempt + 1}")
        except Exception as e:
            print(f"[ERROR] Request error on attempt {attempt + 1}: {e}")

        time.sleep(RETRY_DELAY[min(attempt, len(RETRY_DELAY) - 1)])

    print(f"[FAIL] Could not fetch HTML from {url} after {MAX_RETRIES} retries.")
    return None

'''
soup = get_html('https://solscan.io/')
print(soup)
url = f"https://solscan.io/account/{address}"
soup = get_html(url)
EziVYi3Sv5kJWxmU77PnbrT8jmkVuqwdiFLLzZpLVEn7
'''
