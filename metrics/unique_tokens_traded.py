import requests
import json
import time

SOLANA_RPC_URL = "https://solana-mainnet.g.alchemy.com/v2/j-yxBJanUHFF1MSU9zablLOWczr8-IGW"


def get_unique_mints(wallet_address, max_pages=100):
    unique_mints = set()
    before_signature = None

    for page in range(max_pages):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [wallet_address, {"limit": 1000, **({"before": before_signature} if before_signature else {})}]
        }

        try:
            response = requests.post(SOLANA_RPC_URL, json=payload)
            signatures = response.json().get("result", [])

            if not signatures:
                break

            for sig in signatures:
                tx_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [sig["signature"], {"encoding": "jsonParsed"}]
                }

                try:
                    tx_resp = requests.post(SOLANA_RPC_URL, json=tx_payload)
                    tx_data = tx_resp.json().get("result", {})

                    # Get all token balances
                    post_balances = tx_data.get("meta", {}).get("postTokenBalances", [])
                    pre_balances = tx_data.get("meta", {}).get("preTokenBalances", [])

                    # Extract mints from both pre and post balances
                    for balance in post_balances + pre_balances:
                        mint = balance.get("mint")
                        if mint:
                            unique_mints.add(mint)
                            time.sleep(0.2)
                except:
                    continue

            before_signature = signatures[-1]["signature"]
            time.sleep(0.2)  # Small delay

        except:
            time.sleep(0.5)
            break

    return list(unique_mints)


if __name__ == "__main__":
    wallet = "5h7yzwmrGoG2BmxNCqNR2EnSv1LWCFo7n6SKSh5ZWkfE"
    mints = get_unique_mints(wallet)

    # Output as JSON
    result = {"mints": mints}
    print(json.dumps(result, indent=2))