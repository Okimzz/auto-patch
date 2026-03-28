#!/usr/bin/env python3
"""
generate_keystore.py
Buat keystore baru untuk signing APK.
Jalankan SEKALI secara lokal, lalu simpan keystore/morphe.keystore ke repo.
Password dan alias disimpan sebagai GitHub Actions Secret.
"""

import subprocess
import sys
from pathlib import Path

KEYSTORE_DIR = Path("keystore")
KEYSTORE_DIR.mkdir(exist_ok=True)
KEYSTORE_FILE = KEYSTORE_DIR / "morphe.keystore"


def main():
    if KEYSTORE_FILE.exists():
        print(f"⚠ Keystore sudah ada: {KEYSTORE_FILE}")
        print("   Hapus dulu jika mau buat baru.")
        return

    password = input("Masukkan password keystore (min 6 karakter): ").strip()
    alias = input("Masukkan alias key (default: morphe): ").strip() or "morphe"
    name = input("Nama (CN, misal: Morphe Builder): ").strip() or "Morphe Builder"

    cmd = [
        "keytool",
        "-genkey",
        "-v",
        "-keystore", str(KEYSTORE_FILE),
        "-alias", alias,
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", "10000",
        "-storepass", password,
        "-keypass", password,
        "-dname", f"CN={name}, OU=AutoBuild, O=Morphe, L=ID, S=ID, C=ID",
    ]

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("❌ Gagal generate keystore!")
        sys.exit(1)

    print(f"\n✅ Keystore dibuat: {KEYSTORE_FILE}")
    print("\n🔐 Simpan info ini sebagai GitHub Actions Secret:")
    print(f"   KEYSTORE_PASSWORD = {password}")
    print(f"   KEY_ALIAS         = {alias}")
    print("\n📌 Commit file keystore/morphe.keystore ke repo (aman karena dilindungi password).")


if __name__ == "__main__":
    main()
