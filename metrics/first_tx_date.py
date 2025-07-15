import requests
import time
from datetime import datetime

SOLANA_RPC = "https://solana-mainnet.g.alchemy.com/v2/j-yxBJanUHFF1MSU9zablLOWczr8-IGW"


def get_first_valid_blocktime(wallet_address):
    print(f"[INFO] Fetching full transaction history for: {wallet_address}")

    before_signature = None
    last_page_sigs = []

    while True:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                wallet_address,
                {
                    "limit": 1000,
                    **({"before": before_signature} if before_signature else {})
                }
            ]
        }

        try:
            response = requests.post(SOLANA_RPC, json=payload, timeout=20)
            response.raise_for_status()
            sigs = response.json().get("result", [])

            if not sigs:
                break  # Reached end of history

            print(f"[INFO] Page fetched: {len(sigs)} signatures")
            before_signature = sigs[-1]["signature"]
            last_page_sigs = sigs  # Keep overwriting until last page
            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] Failed during pagination: {e}")
            return None

    if not last_page_sigs:
        print("[WARN] No transactions found.")
        return None

    print(f"[INFO] Final page has {len(last_page_sigs)} signatures.")
    print(f"[INFO] Scanning from oldest to newest in this final page...\n")

    for idx, entry in enumerate(reversed(last_page_sigs)):
        sig = entry["signature"]
        print(f"🔍 Checking signature {len(last_page_sigs) - idx} of {len(last_page_sigs)}: {sig}")

        tx_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [sig, {"encoding": "json"}]
        }

        try:
            tx_response = requests.post(SOLANA_RPC, json=tx_payload, timeout=10)
            tx_response.raise_for_status()
            tx_data = tx_response.json().get("result", {})

            block_time = tx_data.get("blockTime")
            if block_time:
                utc_time = datetime.utcfromtimestamp(block_time)
                print(f"\n✅ Found blockTime: {utc_time.strftime('%Y-%m-%d %H:%M:%S UTC')} at index {len(last_page_sigs) - idx}")
                print(f"🧾 Signature: {sig}")
                return utc_time

        except Exception as e:
            print(f"[WARN] Could not get blockTime for sig {sig}: {e}")
            continue
    return None


# ===== Example Usage =====
if __name__ == "__main__":
    wallet = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
    start = time.time()
    first_tx_time = get_first_valid_blocktime(wallet)
    end = time.time()

    if first_tx_time:
        print(f"\n🟢 First transaction for {wallet} was on: {first_tx_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    else:
        print("\n❌ Failed to get first transaction date.")

    print(f"⏱️ Took {round(end - start, 2)} seconds")