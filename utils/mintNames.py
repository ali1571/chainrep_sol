import requests
import json
import time
import random
ALCHEMY_RPC_URL = "https://solana-mainnet.g.alchemy.com/v2/j-yxBJanUHFF1MSU9zablLOWczr8-IGW"


INPUT_FILE = "../metrics/kakashi UTT"
OUTPUT_FILE = "kakashiUTTnames"

def make_request_with_retry(rpc, payload, attempts):
    for tries in range(attempts):
        try:
            response = requests.post(rpc, json = payload, timeout =10)

            if response.ok and response.content:
                if "error" not in response.json():
                    return response
            if response.status_code ==400:
                raise Exception ("your request is wrong")
            elif response.status_code ==401:
                raise Exception("wrong api key")
            elif response.status_code ==403:
                raise Exception ("you arent allowed to access this")
            elif response.status_code ==404:
                raise Exception ("this page doesnt exist lol")

            response.raise_for_status()

            data = response.json()
            if "error" in data:
                raise Exception(f"API error: {data['error']}")

            return response


        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [429, 502, 503, 504]:
                if tries == attempts -1:
                    raise Exception (f'HTTP {e.response.status_code} error after {attempts} attempts')
                else:
                    time.sleep(2 ** tries)
                    continue
        except requests.exceptions.Timeout:
            if tries == attempts - 1:
                raise Exception (f"Request timed out after {attempts} attempts. Network too slow or API overloaded.")
            else:
                time.sleep(2 ** tries)
                continue
        except requests.exceptions.ConnectionError:
            if tries == attempts - 1:
                raise Exception (f"Connection failed after {attempts} attempts. Check internet or API endpoint.")
            else:
                time.sleep(2 ** tries)
                continue
        except json.JSONDecodeError:
            if tries == attempts - 1:
                raise Exception (f"Invalid JSON response after {attempts} attempts. API returned malformed data.")
            else:
                time.sleep(2 ** tries+ random.uniform(0, 0.5))
                continue

    raise Exception(f"Failed to get response after {attempts} attempts")

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
        response = make_request_with_retry(ALCHEMY_RPC_URL, payload, 5)
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
        print(result)
        with open(OUTPUT_FILE, "a") as f:
            f.write(f"{result}\n")
        metadata.append(result)
        time.sleep(5)  # Avoid rate limits
    return metadata

if __name__ == "__main__":
    mints = load_mints(INPUT_FILE)
    results = fetch_all_metadata(mints)



    print(f"\n✅ Token metadata saved to {OUTPUT_FILE}")
