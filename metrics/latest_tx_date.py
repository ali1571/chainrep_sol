# File: X:\code\chainrep_sol\metrics\last_tx_date.py
import aiohttp
import asyncio
import async_timeout
from datetime import datetime, timezone
from main import validate_wallet_address
import logging

# Suppress noisy aiohttp connection closure errors
logging.getLogger('aiohttp.client').setLevel(logging.CRITICAL)

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"



async def get_last_tx_date(wallet_address: str) -> datetime | None:
    """
    Returns the datetime of the most recent transaction made by a Solana wallet.
    Uses async requests for efficiency and fetches only the first page of transactions.
    """
    if not validate_wallet_address(wallet_address):
        print(f"[ERROR] Invalid wallet address: {wallet_address}")
        return None

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            wallet_address,
            {"limit": 1}  # Fetch only the most recent transaction
        ]
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with async_timeout.timeout(10):
                async with session.post(SOLANA_RPC_URL, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()

                    signatures = data.get("result", [])
                    if not signatures:
                        return None  # No transactions found

                    block_time = signatures[0].get("blockTime")
                    if block_time:
                        return datetime.fromtimestamp(block_time, tz=timezone.utc)
                    else:
                        print(f"[ERROR] No blockTime found for transaction: {signatures[0]['signature']}")
                        return None

        except aiohttp.ClientResponseError as e:
            print(f"[ERROR] HTTP error fetching transactions: {e}")
            return None
        except aiohttp.ClientError as e:
            print(f"[ERROR] Network error fetching transactions: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return None


print(get_last_tx_date("EzPJzK8CvXo3LYKKWk1VincskRbx7jcG3mb2qvjRnFSy"))
if __name__ == "__main__":
    get_last_tx_date("EzPJzK8CvXo3LYKKWk1VincskRbx7jcG3mb2qvjRnFSy")