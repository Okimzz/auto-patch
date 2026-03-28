#!/usr/bin/env python3
"""
patch.py
Menjalankan Morphe CLI untuk patch APK YouTube, lalu sign hasilnya.
"""

import argparse
import glob
import os
import subprocess
import sys
from pathlib import Path

TOOLS_DIR = Path("tools")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def parse_patch_config(config_file: str) -> tuple[list[str], list[str]]:
    """
    Baca file patches/youtube-morphe.txt
    Baris dengan '+' = include, '-' = exclude, '#' = komentar.
    """
    includes = []
    excludes = []
    path = Path(config_file)
    if not path.exists():
        print(f"⚠ Patch config tidak ditemukan: {config_file}")
        return [], []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("+"):
            includes.append(line[1:].strip())
        elif line.startswith("-"):
            excludes.append(line[1:].strip())
    return includes, excludes


def find_base_apk(arch: str) -> Path | None:
    pattern = str(OUTPUT_DIR / f"youtube-*-{arch}-base.apk")
    files = glob.glob(pattern)
    if files:
        return Path(sorted(files)[-1])  # versi terbaru
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", default="youtube")
    parser.add_argument("--arch", default="arm64-v8a")
    parser.add_argument("--patches-config", default="patches/youtube-morphe.txt")
    parser.add_argument("--keystore", default="keystore/morphe.keystore")
    parser.add_argument("--keystore-pass", default="morphe123")
    parser.add_argument("--key-alias", default="morphe")
    args = parser.parse_args()

    arch = args.arch
    cli_jar = TOOLS_DIR / "morphe-cli.jar"
    patches_rvp = TOOLS_DIR / "morphe-patches.rvp"
    integrations_apk = TOOLS_DIR / "morphe-integrations.apk"

    # Validasi tools
    for f in [cli_jar, patches_rvp]:
        if not f.exists():
            print(f"❌ Tools tidak ditemukan: {f}")
            print("   Jalankan scripts/download_tools.py terlebih dahulu.")
            sys.exit(1)

    # Cari base APK
    base_apk = find_base_apk(arch)
    if not base_apk:
        print(f"❌ Base APK [{arch}] tidak ditemukan di {OUTPUT_DIR}/")
        print("   Jalankan scripts/download_apk.py terlebih dahulu.")
        sys.exit(1)

    print(f"📦 Base APK: {base_apk}")

    # Baca versi dari nama file: youtube-{version}-{arch}-base.apk
    parts = base_apk.stem.split("-")
    yt_version = parts[1] if len(parts) >= 3 else "unknown"

    # Output path
    out_apk = OUTPUT_DIR / f"youtube-morphe-{yt_version}-{arch}.apk"

    # Parse patch config
    includes, excludes = parse_patch_config(args.patches_config)
    print(f"✅ Include patches ({len(includes)}): {includes or 'semua'}")
    print(f"❌ Exclude patches ({len(excludes)}): {excludes or 'tidak ada'}")

    # Bangun perintah morphe-cli
    cmd = [
        "java", "-jar", str(cli_jar),
        "patch",
        str(base_apk),
        "--patch-bundle", str(patches_rvp),
        "--out", str(out_apk),
        "--keystore", args.keystore,
        "--keystore-password", args.keystore_pass,
        "--alias", args.key_alias,
        "--alias-password", args.keystore_pass,
    ]

    # Tambah integrations jika ada
    if integrations_apk.exists():
        cmd += ["--merge", str(integrations_apk)]

    # Universal tidak perlu strip native lib

    # Tambah patch include/exclude
    for p in includes:
        cmd += ["--include", p]
    for p in excludes:
        cmd += ["--exclude", p]

    print(f"\n🔧 Menjalankan Morphe CLI...")
    print("   " + " ".join(cmd))
    print()

    result = subprocess.run(cmd, text=True)

    if result.returncode != 0:
        print(f"\n❌ Patching gagal! Exit code: {result.returncode}")
        sys.exit(result.returncode)

    if not out_apk.exists():
        print(f"\n❌ Output APK tidak ditemukan: {out_apk}")
        sys.exit(1)

    size_mb = out_apk.stat().st_size / 1024 / 1024
    print(f"\n✅ Patching sukses!")
    print(f"   Output: {out_apk} ({size_mb:.1f} MB)")


def _opposite_arch(arch: str) -> str:
    """Kembalikan arsitektur yang TIDAK dipakai (untuk di-strip)."""
    mapping = {
        "arm64-v8a": "armeabi-v7a",
        "armeabi-v7a": "arm64-v8a",
    }
    return mapping.get(arch, "")


if __name__ == "__main__":
    main()
