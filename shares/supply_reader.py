from web3 import Web3
from decimal import Decimal
import os
from dotenv import load_dotenv
from pathlib import Path
import sys
import logging
from utils.retry import Web3Retry

"""
dtEURC token supply reader.
Minimal implementation to read total supply of DeTrade EURC tokens.
"""

# Configure logging
class CustomFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.INFO:
            self._style._fmt = '%(message)s'
        return super().format(record)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Add parent directory to PYTHONPATH
root_path = str(Path(__file__).parent.parent)
sys.path.append(root_path)

from config.networks import RPC_URLS

# Contract configuration
CONTRACT_ADDRESS = "0xd4401d8bea82e4e6c40bb26ae3a04d2fb7ca4550"
CONTRACT_NAME = "dtEURC"

class SupplyReader:
    """
    Simple reader for dtEURC token total supply on Base network.
    """
    
    def __init__(self, address: str = None, rpc_url: str = None):
        logger.info("\n=== Supply Reader Initialization ===")
        
        # Use provided address or default to production address
        self.user_address = address or '0x66DbceE7feA3287B3356227d6F3DfF3CeFbC6F3C'
        logger.info(f"User Address: {self.user_address}")
        
        # Use contract configuration
        self.contract_address = CONTRACT_ADDRESS
        self.contract_name = CONTRACT_NAME
        logger.info(f"Contract: {self.contract_name} ({self.contract_address})")
        
        # Initialize Web3 connection
        rpc_url = rpc_url or RPC_URLS['base']
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to RPC endpoint")
        
        # Setup contract
        self.abi = [{
            "name": "totalSupply",
            "inputs": [],
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        }]
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.contract_address),
            abi=self.abi
        )
        logger.info("✓ Connection established\n")
    
    def get_total_supply(self) -> str:
        """Returns raw total supply in wei as string"""
        total_supply = Web3Retry.call_contract_function(
            self.contract.functions.totalSupply().call
        )
        logger.info(f"Raw Supply: {total_supply} wei")
        return str(total_supply)

    def format_total_supply(self) -> str:
        """Returns formatted total supply with 18 decimals"""
        total_supply = self.get_total_supply()
        formatted_supply = f"{Decimal(total_supply) / Decimal('1000000000000000000'):.18f}"
        logger.info(f"Formatted Supply: {formatted_supply} {self.contract_name}\n")
        return formatted_supply

def main():
    """CLI utility to check dtEURC total supply"""
    try:
        logger.info("\n=== dtEURC Supply Reader ===")
        reader = SupplyReader()
        reader.format_total_supply()
    except Exception as e:
        logger.error(f"\n❌ Error: {str(e)}\n")
        raise

if __name__ == "__main__":
    main() 