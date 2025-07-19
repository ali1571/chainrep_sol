import requests
import json
import time
ALCHEMY_RPC_URL = "https://solana-mainnet.g.alchemy.com/v2/j-yxBJanUHFF1MSU9zablLOWczr8-IGW"


INPUT_FILE = "../metrics/kakashi UTT"
OUTPUT_FILE = "kakashiUTTnames"

def load_mints(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def get_mint_metadata(mint_address):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAsset",
        "params": {
            "id": mint_address
        }
    }

    try:
        response = requests.post(ALCHEMY_RPC_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        result = data.get("result", {})

        name = result.get("content", {}).get("metadata", {}).get("name")
        symbol = result.get("content", {}).get("metadata", {}).get("symbol")
        return {
            "mint": mint_address,
            "name": name,
            "symbol": symbol
        }
    except Exception as e:
        print(f"[WARN] Failed to fetch metadata for {mint_address}: {e}")
        return {
            "mint": mint_address,
            "name": None,
            "symbol": None
        }

def fetch_all_metadata(mints):
    metadata = []
    for i, mint in enumerate(mints):
        print(f"[{i+1}/{len(mints)}] Fetching metadata for {mint}...")
        result = get_mint_metadata(mint)
        metadata.append(result)
        time.sleep(5)  # Avoid rate limits
    return metadata

if __name__ == "__main__":
    mints = load_mints(INPUT_FILE)
    results = fetch_all_metadata(mints)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Token metadata saved to {OUTPUT_FILE}")
