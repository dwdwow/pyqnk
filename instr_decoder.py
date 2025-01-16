from solders.pubkey import Pubkey
from solana.constants import SYSTEM_PROGRAM_ID, CONFIG_PROGRAM_ID, STAKE_PROGRAM_ID, VOTE_PROGRAM_ID, ADDRESS_LOOKUP_TABLE_PROGRAM_ID, BPF_LOADER_PROGRAM_ID, ED25519_PROGRAM_ID, SECP256K1_PROGRAM_ID


TOKEN_PROGRAM_ID: Pubkey = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
TOKEN_2022_PROGRAM_ID: Pubkey = Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb")
RAYDIUM_CPMM_PROGRAM_ID: Pubkey = Pubkey.from_string("CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C")
ORCA_WHIRLPOOLS_PROGRAM_ID: Pubkey = Pubkey.from_string("whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc")


def system_instruction_decoder(data: bytes) -> dict:
    pass