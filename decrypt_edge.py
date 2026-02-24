# decrypt_edge.py (debug-friendly, supports v10/v11/v20/v21/v22/v23 short-tag)
import sqlite3, json, base64, traceback
import win32crypt
from Cryptodome.Cipher import AES

try:
    # Load Local State and DPAPI decrypt key
    with open(r"C:\chrome_forensic\Local State","r",encoding="utf-8") as f:
        ls = json.load(f)
    enc_key = base64.b64decode(ls["os_crypt"]["encrypted_key"])[5:]
    key = win32crypt.CryptUnprotectData(enc_key, None, None, None, 0)[1]
    print("Decrypted AES Key:", key.hex())
except Exception as e:
    print("FAILED to load Local State or decrypt enc_key:", e)
    traceback.print_exc()
    raise SystemExit(1)

def decrypt_password(blob):
    blob = bytes(blob)

    # v10 / v11 (old)
    if blob.startswith(b"v10") or blob.startswith(b"v11"):
        iv = blob[3:15]
        ciphertext = blob[15:-16]
        tag = blob[-16:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()

    # v20+ (new)
    if blob.startswith(b"v20"):
        version = blob[3]

        # Chrome v23+ style: short 8-byte tag (we detect version byte >= 0xE5 from your blob)
        if version >= 0xE5:
            iv = blob[4:16]           # 12-byte IV
            tag = blob[-8:]           # 8-byte short tag
            ciphertext = blob[16:-8]
        # v21/v22 variants (examples): use 16-byte IV and 32-byte tag
        elif version >= 0xE0:
            iv = blob[4:20]           # 16-byte IV
            tag = blob[-32:]          # 32-byte tag (v22)
            ciphertext = blob[20:-32]
        else:
            # v20 legacy (12 byte IV + 16 tag)
            iv = blob[4:16]
            tag = blob[-16:]
            ciphertext = blob[16:-16]

        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()

    raise ValueError("Unknown blob format")

# Load DB and attempt decrypt
try:
    conn = sqlite3.connect(r"C:\chrome_forensic\Login Data")
    cur = conn.cursor()
    cur.execute("SELECT origin_url, username_value, password_value FROM logins")
    rows = cur.fetchall()
    print("Entries:", len(rows))
except Exception as e:
    print("FAILED to read Login Data:", e)
    traceback.print_exc()
    raise SystemExit(1)

if not rows:
    print("No rows found in Login Data.")
for idx, (url, user, enc) in enumerate(rows, start=1):
    try:
        print(f"\n--- Entry {idx} ---")
        print("url:", url)
        print("user:", user)
        if not enc:
            print("password blob is empty")
            continue
        print("blob length:", len(enc))
        print("blob hex:", bytes(enc).hex())
        password = decrypt_password(enc)
        print("DECRYPTED PASSWORD:", password)
    except Exception as e:
        print("DECRYPT ERROR:", e)
        traceback.print_exc()
                                  
