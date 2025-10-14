import os, sys, traceback, requests
from bs4 import BeautifulSoup

def send_telegram(msg: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("DEBUG: Telegram creds missing, skipping.")
        return
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": msg},
            timeout=15
        )
        print("Telegram response:", r.status_code, r.text)
    except Exception as e:
        print("Telegram send failed:", e)

def main():
    try:
        target = os.getenv("TARGET_URL")
        if not target:
            print("ERROR: TARGET_URL secret set nahi hai.")
            sys.exit(2)

        print("DEBUG: TARGET_URL =", target)
        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(target, headers=headers, timeout=20)
        print("DEBUG: HTTP status:", resp.status_code)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        price_tag = soup.select_one(".price") or soup.select_one("span.price") or soup.select_one("#price")
        if not price_tag:
            print("WARNING: price selector returned None")
            print("PAGE SNIPPET (first 1000 chars):")
            print(resp.text[:1000])
        price = price_tag.get_text(strip=True) if price_tag else "NOT FOUND"
        print("DEBUG: Found price:", price)

        send_telegram(f"Price for {target}: {price}")
        print("DEBUG: Completed")
        return 0
    except requests.exceptions.RequestException as re:
        print("REQUEST ERROR:", re); traceback.print_exc(); sys.exit(1)
    except SystemExit:
        raise
    except Exception as e:
        print("UNHANDLED EXCEPTION:", e); traceback.print_exc(); sys.exit(1)

if __name__ == "__main__":
    sys.exit(main() or 0)
