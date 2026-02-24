import base64
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# ---- LOAD FILES ----
with open("salt.bin", "rb") as f:
    salt = f.read()

with open("cipher.bin", "rb") as f:
    blob = f.read()

# ---- PARAMETERS EXTRACTED FROM YOUR WALLET ----
m_cost = 16384  # memory KiB
t_cost = 8      # iterations
p_cost = 1      # parallelism

# Exodus uses AES-256-GCM:
iv = blob[:12]          # 12 byte nonce
ciphertext = blob[12:-16]
gcm_tag = blob[-16:]    # 16 byte tag

print("Salt:", salt.hex())
print("IV:", iv.hex())
print("Ciphertext length:", len(ciphertext))

# ---- TRY PASSWORDS ----
with open("password.txt", "r", encoding="utf-8") as wordlist:
    for pwd in wordlist:
        pwd = pwd.strip()

        print("Trying:", pwd)

        # Derive key using Argon2id
        key = hash_secret_raw(
            secret=pwd.encode(),
            salt=salt,
            time_cost=t_cost,
            memory_cost=m_cost,
            parallelism=p_cost,
            hash_len=32,
            type=Type.ID,
        )

        # Try decrypting
        try:
            decryptor = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, gcm_tag)
            ).decryptor()

            plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            print("\n\n===============================")
            print("PASSWORD FOUND:", pwd)
            print("===============================\n\n")

            with open("decrypted_wallet.bin", "wb") as out:
                out.write(plaintext)

            exit(0)

        except Exception:
            continue

print("No password matched.")
