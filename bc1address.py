import requests
import time

INPUT_FILE = "bc1sending_clean.txt"
OUTPUT_FILE = "bc1_results.csv"
API_URL = "https://blockstream.info/api/address/{}"

with open(INPUT_FILE, "r") as f:
    addresses = [line.strip() for line in f if line.strip()]

print(f"[+] Loaded {len(addresses)} addresses")

with open(OUTPUT_FILE, "w") as out:
    out.write("Address,Status,TxCount\n")

    for addr in addresses:
        try:
            r = requests.get(API_URL.format(addr), timeout=10)

            if r.status_code != 200:
                out.write(f"{addr},INVALID_OR_UNKNOWN,0\n")
                print(f"INVALID_OR_UNKNOWN : {addr}")
                continue

            data = r.json()
            txs = data.get("chain_stats", {}).get("tx_count", 0)

            if txs > 0:
                status = "VALID_ACTIVE"
            else:
                status = "VALID_UNUSED"

            out.write(f"{addr},{status},{txs}\n")
            print(f"{status} : {addr} ({txs})")

            time.sleep(1)

        except Exception as e:
            print(f"ERROR : {addr} : {e}")
            time.sleep(2)

print("[+] Done.")
