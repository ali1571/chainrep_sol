import requests
import json
import time
import random

SOLANA_RPC_URL = "https://solana-mainnet.g.alchemy.com/v2/j-yxBJanUHFF1MSU9zablLOWczr8-IGW"


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


def get_unique_mints(wallet_address, max_pages=100):
    unique_mints = set()
    before_signature = None
    pagecount =0

    for page in range(max_pages):
        print(pagecount)
        pagecount+=1
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [wallet_address, {"limit": 1000, **({"before": before_signature} if before_signature else {})}]
        }

        try:
            response = make_request_with_retry(SOLANA_RPC_URL, payload, 5)
            signatures = response.json().get("result", [])

            if not signatures:
                break

            for sig in signatures:
                tx_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [sig["signature"], {"encoding": "jsonParsed","maxSupportedTransactionVersion": 0}]
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
                            if mint not in unique_mints:
                                with open('kakashimints', 'a') as f:
                                    f.write(f"{mint} \n")
                                unique_mints.add(mint)
                                print(mint)
                            else:
                                continue

                except:
                    continue
                time.sleep(0.2)



            before_signature = signatures[-1]["signature"]
            time.sleep(0.2)  # Small delay

        except:
            time.sleep(0.5)
            break

    return list(unique_mints)

def fetch_mintData(mint):
    metadata = []
    print('fetching mintdata for mint: ', mint)
    mint_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAsset",
        "params": {
            "id": mint
        }
    }

    try:
        response = requests.post(SOLANA_RPC_URL, json=mint_payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        result = data.get("result", {})

        name = result.get("content", {}).get("metadata", {}).get("name")
        symbol = result.get("content", {}).get("metadata", {}).get("symbol")
        return {
            "mint": mint,
            "name": name,
            "symbol": symbol
        }
    except Exception as e:
        print(f"[WARN] Failed to fetch metadata for {mint}: {e}")
        return {
            "mint": mint,
            "name": None,
            "symbol": None
        }


if __name__ == "__main__":
    wallet = "5h7yzwmrGoG2BmxNCqNR2EnSv1LWCFo7n6SKSh5ZWkfE"
    mint_result = get_unique_mints(wallet)
    mints = mint_result


'''
    # Output as JSON
    result = {
        "mints": mints,
    }
    print(json.dumps(result, indent=2))


'''


'''
    name = tx_data.get("content", {}).get("metadata", {}).get("name")
    symbol = tx_data.get("content", {}).get("metadata", {}).get("symbol")
    mint_stat = {
        "mint": mint,
        "name": name,
        "symbol": symbol
    }

    print(mint_stat)
    metadata.append(mint_stat)
'''