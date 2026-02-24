from bitcoin import SelectParams
from bitcoin.wallet import P2WPKHBitcoinAddress
from bitcoin.core import Hash160
from bip32utils import BIP32Key
import base58

SelectParams('mainnet')

def zpub_to_xpub(zpub):
    data = base58.b58decode_check(zpub)
    # zpub (BIP84) → xpub version bytes
    return base58.b58encode_check(b'\x04\x88\xb2\x1e' + data[4:]).decode()

zpub = "zpub6r3uNKcg5jZrdCBFFHXFsVvq9eu2oGb5g9mRgPBwhhPfS84vztPN2V4XhEkPeAPCX4ehR9574ARn9yr9nE2NjbLWfsR44eVRMF4iessmzHv"

xpub = zpub_to_xpub(zpub)
root = BIP32Key.fromExtendedKey(xpub)

# External (receive) chain: m/84'/0'/0'/0/i
external = root.ChildKey(0)

for i in range(10):
    child = external.ChildKey(i)
    pubkey = child.PublicKey()
    h160 = Hash160(pubkey)
    addr = P2WPKHBitcoinAddress.from_bytes(0, h160)
    print(f"m/84'/0'/0'/0/{i} -> {addr}")
