import asyncio
import logging
import aiohttp
from datetime import datetime, timezone
from metrics.total_txs import get_total_transactions
from metrics.first_tx_date import get_first_tx_date
from metrics.latest_tx_date import get_last_tx_date
from metrics.unique_tokens_traded import get_unique_tokens_traded
import base58
import re

# Configure logging

def validate_wallet_address(wallet_address: str) -> bool:
    """
    Validate a Solana wallet address (base58, 32-44 characters).
    """
    try:
        if not (32 <= len(wallet_address) <= 44):
            return False
        base58.b58decode(wallet_address)
        return bool(re.match(r'^[1-9A-HJ-NP-Za-km-z]+$', wallet_address))
    except Exception:
        return False

async def main():
    wallet = "EzPJzK8CvXo3LYKKWk1VincskRbx7jcG3mb2qvjRnFSy"


    async with aiohttp.ClientSession() as session:
        # Get total transactions
        try:
            tx_count = await get_total_transactions(wallet, max_pages=5)
            if tx_count is not None:
                logging.info(f"Total transactions for {wallet}: {tx_count}")
            else:
                logging.error(f"Failed to fetch total transactions for {wallet}")
        except Exception as e:
            logging.error(f"Error fetching total transactions: {e}")

        await asyncio.sleep(0.5)  # Delay to avoid rate limits

        # Get first transaction date
        try:
            first_tx_date = await get_first_tx_date(wallet, max_pages=100)
            if first_tx_date:
                logging.info(
                    f"First transaction for {wallet} was made on: {first_tx_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            else:
                logging.error(f"No transactions found for {wallet} or failed to fetch first transaction date")
        except Exception as e:
            logging.error(f"Error fetching first transaction date: {e}")

        await asyncio.sleep(0.5)

        # Get latest transaction date
        try:
            latest_tx_date = await get_last_tx_date(wallet)
            if latest_tx_date:
                logging.info(
                    f"Last transaction for {wallet} was made on: {latest_tx_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            else:
                logging.error(f"No transactions found for {wallet} or failed to fetch latest transaction date")
        except Exception as e:
            logging.error(f"Error fetching latest transaction date: {e}")

        await asyncio.sleep(0.5)

        # Get unique tokens traded
        try:
            unique_tokens = await get_unique_tokens_traded(wallet, max_pages=5)
            if unique_tokens is not None:
                logging.info(f"Unique tokens traded by {wallet}: {unique_tokens}")
            else:
                logging.error(f"Failed to fetch unique tokens traded for {wallet}")
        except Exception as e:
            logging.error(f"Error fetching unique tokens traded: {e}")


if __name__ == "__main__":
    asyncio.run(main())