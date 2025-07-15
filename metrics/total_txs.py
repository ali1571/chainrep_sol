import requests
import time

SOLANA_RPC_URL = "https://solana-mainnet.g.alchemy.com/v2/j-yxBJanUHFF1MSU9zablLOWczr8-IGW"

def get_total_transactions(wallet_address: str, max_pages: int = 100, delay: float = 2.0):
    total_txs = 0
    before_signature = None
    not_end = True
    page = 1
    #for page in range(max_pages):
    while not_end:

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
            response = requests.post(SOLANA_RPC_URL, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            signatures = data.get("result", [])
            if not signatures:
                not_end = False
                break

            total_txs += len(signatures)
            before_signature = signatures[-1]["signature"]

            print(f"Page {page}: {len(signatures)} txs")
            page +=1
            time.sleep(delay)  # <-- CRUCIAL TO AVOID 429s

        except requests.exceptions.RequestException as e:
            print(f"[WARN] Request failed: {e}")
            time.sleep(delay * 2)  # Double delay on error
            continue

    return total_txs


# Example usage
if __name__ == "__main__":
    wallet = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"  # Solana placeholder
    start = time.time()
    count = get_total_transactions(wallet)
    end = time.time()
    print(f"\nTotal transactions for {wallet}: {count}")
    print(f"Time taken: {round(end - start, 2)}s")
