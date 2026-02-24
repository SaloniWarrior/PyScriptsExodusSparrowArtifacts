import hashlib

# Load BIP39 wordlist
with open("/home/kali/wordlist.txt", "r", encoding="utf-8") as f:
    WORDLIST = [w.strip() for w in f.readlines()]

def mnemonic_to_entropy(words):
    """Convert mnemonic to entropy and checksum; return (entropy_hex, is_valid)."""
    if len(words) != 12:
        return (None, False)

    # Convert words to 132-bit binary string
    bits = ""
    for w in words:
        if w not in WORDLIST:
            return (None, False)
        idx = WORDLIST.index(w)
        bits += bin(idx)[2:].zfill(11)

    # 128 bits entropy + 4 bits checksum
    entropy_bits = bits[:128]
    checksum_bits = bits[128:]

    entropy_bytes = int(entropy_bits, 2).to_bytes(16, byteorder="big")
    hash_bytes = hashlib.sha256(entropy_bytes).digest()
    hash_bits = bin(hash_bytes[0])[2:].zfill(8)

    # Compare checksum
    if checksum_bits == hash_bits[:4]:
        return (entropy_bytes.hex(), True)
    else:
        return (entropy_bytes.hex(), False)

input_file = "/home/kali/Exodus/next/seednext"     # your extracted seeds
output_file = "valid_seeds.txt"  # only valid seeds

valid = []

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip().lower()
        words = line.split()

        if len(words) == 12:
            ent, ok = mnemonic_to_entropy(words)
            if ok:
                print("[VALID]  ", line)
                valid.append(line)
            else:
                pass  # ignore invalid
        else:
            pass  # ignore lines not containing 12 words

# Save all valid results
with open(output_file, "w", encoding="utf-8") as f:
    for v in valid:
        f.write(v + "\n")

print("\nDONE!")
print(f"Valid seeds found: {len(valid)}")
print(f"Saved to: {output_file}")
