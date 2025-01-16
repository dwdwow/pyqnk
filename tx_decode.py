import os
import base58
from solders.transaction import Transaction, VersionedTransaction
from solders.message import Message, MessageV0
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction_status import UiTransactionStatusMeta, UiTransaction, UiRawMessage, UiParsedMessage
from base58 import b58decode
from solana.rpc.api import Client

# Common Solana Program IDs
SYSTEM_PROGRAM_ID = "11111111111111111111111111111111"
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
TOKEN_2022_PROGRAM_ID = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
ASSOCIATED_TOKEN_PROGRAM_ID = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
RAYDIUM_AMM_V4_PROGRAM_ID = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"  # AMM v4
RAYDIUM_CLMM_PROGRAM_ID = "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK"    # Concentrated Liquidity
RAYDIUM_CPMM_PROGRAM_ID = "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C"    # CPMM (Constant Product)


def decode_system_instruction(data: bytes) -> dict:
    """
    Decode System Program instruction data
    """
    if len(data) < 4:
        return {"error": "Invalid data length"}
        
    instruction_type = int.from_bytes(data[:4], 'little')
    
    # System Program instruction types
    SYSTEM_INSTRUCTIONS = {
        2: "Transfer",
        3: "CreateAccount",
        8: "CreateAccountWithSeed",
    }
    
    instruction_name = SYSTEM_INSTRUCTIONS.get(instruction_type, f"Unknown({instruction_type})")
    
    if instruction_type == 2:  # Transfer
        lamports = int.from_bytes(data[4:12], 'little')
        return {
            "type": instruction_name,
            "lamports": lamports,
            "sol": lamports / 1_000_000_000  # Convert lamports to SOL
        }
    
    return {
        "type": instruction_name,
        "raw_data": data.hex()
    }

def decode_token_instruction(data: bytes) -> dict:
    """
    Decode Token Program instruction data
    """
    if len(data) < 1:
        return {"error": "Invalid data length"}
        
    instruction_type = data[0]
    
    # Token Program instruction types
    TOKEN_INSTRUCTIONS = {
        1: "InitializeAccount",
        3: "Transfer",
        7: "MintTo",
        8: "Burn",
        9: "CloseAccount",
    }
    
    instruction_name = TOKEN_INSTRUCTIONS.get(instruction_type, f"Unknown({instruction_type})")
    
    if instruction_type == 1:  # InitializeAccount
        return {
            "type": instruction_name,
            "owner": data[1:33].hex() if len(data) >= 33 else None
        }
    elif instruction_type == 3:  # Transfer
        amount = int.from_bytes(data[1:9], 'little')
        return {
            "type": instruction_name,
            "amount": amount
        }
    
    return {
        "type": instruction_name,
        "raw_data": data.hex()
    }

def decode_token_2022_instruction(data: bytes) -> dict:
    """
    Decode Token Program instruction data
    """
    if len(data) < 1:
        return {"error": "Invalid data length"}
        
    instruction_type = data[0]
    
    # Token Program instruction types
    TOKEN_INSTRUCTIONS = {
        1: "InitializeAccount",
        3: "Transfer",
        7: "MintTo",
        8: "Burn",
        9: "CloseAccount",
    }
    
    instruction_name = TOKEN_INSTRUCTIONS.get(instruction_type, f"Unknown({instruction_type})")
    
    if instruction_type == 1:  # InitializeAccount
        return {
            "type": instruction_name,
            "owner": data[1:33].hex() if len(data) >= 33 else None
        }
    elif instruction_type == 3:  # Transfer
        amount = int.from_bytes(data[1:9], 'little')
        return {
            "type": instruction_name,
            "amount": amount
        }
    
    return {
        "type": instruction_name,
        "raw_data": data.hex()
    }

def decode_raydium_amm_instruction(data: bytes) -> dict:
    """
    Decode Raydium AMM v4 instruction data
    """
    if len(data) < 1:
        return {"error": "Invalid data length"}
        
    instruction_type = data[0]
    
    # Raydium AMM instruction types
    RAYDIUM_AMM_INSTRUCTIONS = {
        1: "Initialize",
        2: "Swap",
        3: "DepositAllTokenTypes",
        4: "WithdrawAllTokenTypes",
        5: "DepositSingleTokenTypeExactAmountIn",
        6: "WithdrawSingleTokenTypeExactAmountOut",
    }
    
    instruction_name = RAYDIUM_AMM_INSTRUCTIONS.get(instruction_type, f"Unknown({instruction_type})")
    
    if instruction_type == 2:  # Swap
        try:
            amount_in = int.from_bytes(data[1:9], 'little')
            minimum_amount_out = int.from_bytes(data[9:17], 'little')
            return {
                "type": instruction_name,
                "amount_in": amount_in,
                "minimum_amount_out": minimum_amount_out
            }
        except:
            pass
            
    elif instruction_type in (3, 4):  # Deposit/Withdraw All Token Types
        try:
            max_coin_amount = int.from_bytes(data[1:9], 'little')
            max_pc_amount = int.from_bytes(data[9:17], 'little')
            return {
                "type": instruction_name,
                "max_coin_amount": max_coin_amount,
                "max_pc_amount": max_pc_amount
            }
        except:
            pass
    
    return {
        "type": instruction_name,
        "raw_data": data.hex()
    }

def decode_raydium_clmm_instruction(data: bytes) -> dict:
    """
    Decode Raydium Concentrated Liquidity instruction data
    """
    if len(data) < 1:
        return {"error": "Invalid data length"}
        
    instruction_type = data[0]
    
    # Raydium CLMM instruction types
    RAYDIUM_CLMM_INSTRUCTIONS = {
        0: "CreatePool",
        1: "OpenPosition",
        2: "ClosePosition",
        3: "Swap",
        4: "IncreasePosition",
        5: "DecreasePosition",
    }
    
    instruction_name = RAYDIUM_CLMM_INSTRUCTIONS.get(instruction_type, f"Unknown({instruction_type})")
    
    if instruction_type == 3:  # Swap
        try:
            amount_in = int.from_bytes(data[1:9], 'little')
            amount_out_minimum = int.from_bytes(data[9:17], 'little')
            sqrt_price_limit = int.from_bytes(data[17:25], 'little')
            return {
                "type": instruction_name,
                "amount_in": amount_in,
                "amount_out_minimum": amount_out_minimum,
                "sqrt_price_limit": sqrt_price_limit
            }
        except:
            pass
    
    return {
        "type": instruction_name,
        "raw_data": data.hex()
    }

def decode_raydium_cpmm_instruction(data: bytes) -> dict:
    """
    Decode Raydium Constant Product Market Maker (CPMM) instruction data
    """
    if len(data) < 1:
        return {"error": "Invalid data length"}
        
    instruction_type = data[8]
    
    # Raydium CPMM instruction types
    RAYDIUM_CPMM_INSTRUCTIONS = {
        0: "CreateAmmConfig",
        1: "UpdateAmmConfig",
        2: "UpdatePoolStatus",
        3: "CollectProtocolFee",
        4: "CollectFundFee",
        5: "Initialize",
        6: "Deposit",
        7: "Withdraw",
        8: "SwapBaseInput",
        9: "SwapBaseOutput"
    }
    
    instruction_name = RAYDIUM_CPMM_INSTRUCTIONS.get(instruction_type, f"Unknown({instruction_type})")
    
    try:
        if instruction_type == 5:  # Initialize
            init_amount_0 = int.from_bytes(data[1:9], 'little')
            init_amount_1 = int.from_bytes(data[9:17], 'little')
            open_time = int.from_bytes(data[17:25], 'little')
            return {
                "type": instruction_name,
                "init_amount_0": init_amount_0,
                "init_amount_1": init_amount_1,
                "open_time": open_time
            }
            
        elif instruction_type == 6:  # Deposit
            lp_token_amount = int.from_bytes(data[1:9], 'little')
            maximum_token_0_amount = int.from_bytes(data[9:17], 'little')
            maximum_token_1_amount = int.from_bytes(data[17:25], 'little')
            return {
                "type": instruction_name,
                "lp_token_amount": lp_token_amount,
                "maximum_token_0_amount": maximum_token_0_amount,
                "maximum_token_1_amount": maximum_token_1_amount
            }
            
        elif instruction_type == 7:  # Withdraw
            lp_token_amount = int.from_bytes(data[1:9], 'little')
            minimum_token_0_amount = int.from_bytes(data[9:17], 'little')
            minimum_token_1_amount = int.from_bytes(data[17:25], 'little')
            return {
                "type": instruction_name,
                "lp_token_amount": lp_token_amount,
                "minimum_token_0_amount": minimum_token_0_amount,
                "minimum_token_1_amount": minimum_token_1_amount
            }
            
        elif instruction_type == 8:  # SwapBaseInput
            amount_in = int.from_bytes(data[1:9], 'little')
            minimum_amount_out = int.from_bytes(data[9:17], 'little')
            return {
                "type": instruction_name,
                "amount_in": amount_in,
                "minimum_amount_out": minimum_amount_out
            }
            
        elif instruction_type == 9:  # SwapBaseOutput
            max_amount_in = int.from_bytes(data[1:9], 'little')
            amount_out = int.from_bytes(data[9:17], 'little')
            return {
                "type": instruction_name,
                "max_amount_in": max_amount_in,
                "amount_out": amount_out
            }
            
    except:
        pass
    
    return {
        "type": instruction_name,
        "raw_data": data.hex()
    }

def decode_instruction_data(program_id: Pubkey, data: bytes) -> dict:
    """
    Decode instruction data based on program ID
    """
    program_id_str = str(program_id)
    
    if program_id_str == SYSTEM_PROGRAM_ID:
        return decode_system_instruction(data)
    elif program_id_str == TOKEN_PROGRAM_ID:
        return decode_token_instruction(data)
    elif program_id_str == TOKEN_2022_PROGRAM_ID:
        return decode_token_2022_instruction(data)
    elif program_id_str == RAYDIUM_AMM_V4_PROGRAM_ID:
        return decode_raydium_amm_instruction(data)
    elif program_id_str == RAYDIUM_CPMM_PROGRAM_ID:
        return decode_raydium_cpmm_instruction(data)
    elif program_id_str == RAYDIUM_CLMM_PROGRAM_ID:
        return decode_raydium_clmm_instruction(data)
    
    return {
        "program": program_id_str,
        "raw_data": data.hex()
    }

def decode_transaction(tx_string: str) -> Transaction:
    """
    Decode a Solana transaction from either a base58 or base64 encoded string
    
    Args:
        tx_string (str): The encoded transaction string
        
    Returns:
        Transaction: Decoded Solana transaction object from solders
    """
    try:
        # Try base58 first
        decoded_data = b58decode(tx_string)
        return Transaction.from_bytes(decoded_data)
        # try:
        # except:
        #     # If base58 fails, try base64
        #     print("use base64 to decode tx raw string")
        #     decoded_data = base64.b64decode(tx_string)
        #     return Transaction.from_bytes(decoded_data)
            
    except Exception as e:
        raise ValueError(f"Failed to decode transaction: {str(e)}")

def print_transaction_details(transaction: VersionedTransaction, meta: UiTransactionStatusMeta=None):
    """
    Print readable details of a decoded transaction
    
    Args:
        transaction (Transaction): Decoded Solana transaction object
        meta: Transaction metadata containing inner instructions
    """
    print("\nTransaction Details:")
    print("-" * 50)
    
    # Print signatures
    print("Signatures:")
    for sig in transaction.signatures:
        print(sig)
    
    # Print message (contains instructions)
    message = transaction.message
    accounts = [*message.account_keys]
    if meta:
        accounts.extend(meta.loaded_addresses.writable)
        accounts.extend(meta.loaded_addresses.readonly)
    print("\nAccounts:")
    for account in accounts:
        print(account)
    print("\nInstructions:")
    for idx, instruction in enumerate(message.instructions):
        print(f"\nInstruction {idx + 1}:")
        program_id = accounts[instruction.program_id_index]
        print(f"  Program ID: {program_id}")
        
        # Decode and print instruction data
        decoded_data = decode_instruction_data(program_id, instruction.data)
        print(f"  Decoded Data: {decoded_data}")
        
        # Print inner instructions if available
        if meta and meta.inner_instructions:
            inner_instructions = [x for x in meta.inner_instructions if x.index == idx]
            if inner_instructions:
                print("\n  Inner Instructions:")
                for inner_ix_group in inner_instructions:
                    for inner_ix in inner_ix_group.instructions:
                        inner_decoded = decode_instruction_data(accounts[inner_ix.program_id_index], base58.b58decode(inner_ix.data))
                        print(f"      Decoded Data: {inner_decoded}")
                    # for inner_idx, inner_ix in enumerate(inner_ix_group.instructions):
                    #     inner_program_id = message.account_keys[inner_ix.program_id_index]
                    #     print(f"\n    Inner Instruction {inner_idx + 1}:")
                    #     print(f"      Program ID: {inner_program_id}")
                    #     print(inner_ix.data)
                    #     inner_decoded = decode_instruction_data(inner_program_id, base58.b58decode(inner_ix.data))
                    #     print(f"      Decoded Data: {inner_decoded}")

def get_transaction_by_hash(tx_hash: str, rpc_url: str = "https://api.mainnet-beta.solana.com") -> tuple[VersionedTransaction | UiTransaction, any]:
    """
    Fetch transaction data and metadata from Solana network using transaction hash
    
    Args:
        tx_hash (str): Transaction hash/signature
        rpc_url (str): Solana RPC endpoint URL
        
    Returns:
        tuple: (VersionedTransaction, metadata)
    """
    client = Client(rpc_url)
    sig = Signature.from_string(tx_hash)
    response = client.get_transaction(
        sig,
        encoding='jsonParsed',
        max_supported_transaction_version=0
    )
    
    if not response.value:
        raise ValueError(f"Transaction {tx_hash} not found")
    
    tx = response.value.transaction.transaction
    
    if isinstance(tx, UiTransaction):
        print(len(tx.message.account_keys))
        print("is a ui transaction")
    elif isinstance(tx, VersionedTransaction):
        print(len(tx.message.account_keys))
        print("is a versioned transaction")
    else:
        raise ValueError("Not a typed tx")
    
    tx_msg = tx.message
    
    if isinstance(tx_msg, UiRawMessage):
        print("is a ui raw message")
    elif isinstance(tx_msg, MessageV0):
        print("is a message v0")
    elif isinstance(tx_msg, Message):
        print("is a message")
    elif isinstance(tx_msg, UiParsedMessage):
        print("is a ui parsed message")
    else:
        raise ValueError("Not a typed tx message")


    meta = response.value.transaction.meta
    
    if meta.inner_instructions:
        print(type(meta.inner_instructions[0].instructions[0]))
    

    # print(meta.pre_balances)
    # print(meta.post_balances)
    # print(meta.pre_token_balances)
    # print(meta.post_token_balances)

    return tx, meta
        

def main():
    # Read RPC URL from file
    # with open(os.path.expanduser('~/test_tokens/quick_node_http'), 'r') as f:
    #     rpc_url = f.read().strip('\n\t\r ')
# Example transaction hash
    tx_hash = "mCN8EsjzE4HELqF8CBC845wvL39mGDSGoVq6ex8yAGqjxGN59U5MNt7H7rkA4NLgQiJ6bjXefEy45oqN41KmUm4"
    
    tx, meta = get_transaction_by_hash(tx_hash)
    # print_transaction_details(tx, meta)
        

if __name__ == "__main__":
    main()