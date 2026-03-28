#!/usr/bin/env python3
"""
download_apk.py
Download base YouTube APK (universal) dari APKMirror.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

TOOLS_DIR = Path("tools")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Mobile Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

YT_PACKAGE = "com.google.android.youtube"
APKMIRROR_BASE = "https://www.apkmirror.com"


# ── Deteksi versi kompatibel ──────────────────────────────────────────────────

def get_compatible_version() -> str:
    import subprocess

    cli = TOOLS_DIR / "morphe-cli.jar"
    patches = TOOLS_DIR / "morphe-patches.rvp"

    if not cli.exists() or not patches.exists():
        print("  ⚠ Tools belum tersedia, skip deteksi versi otomatis.")
        return ""

    cmd = [
        "java", "-jar", str(cli),
        "list-patches",
        "--patch-bundle", str(patches),
        "--filter-package-name", YT_PACKAGE,
        "--with-versions",
        "--json",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        data = json.loads(result.stdout)
        versions = set()
        for patch in data:
            for compat in patch.get("compatiblePackages", []):
                if compat.get("name") == YT_PACKAGE:
                    for v in compat.get("versions", []):
                        versions.add(v)
        if versions:
            latest = sorted(versions, key=lambda v: [int(x) for x in v.split(".")])[-1]
            print(f"  ✅ Versi YouTube kompatibel: {latest}")
            return latest
    except Exception as e:
        print(f"  ⚠ Gagal deteksi versi: {e}")
    return ""


# ── APKMirror scraper ─────────────────────────────────────────────────────────

def apkmirror_release_page_url(version: str) -> str:
    slug = version.replace(".", "-")
    return f"{APKMIRROR_BASE}/apk/google-inc/youtube/youtube-{slug}-release/"


def apkmirror_find_universal_apk_page(version: str) -> str | None:
    """Cari link halaman APK universal (nodpi) dari halaman release."""
    url = apkmirror_release_page_url(version)
    print(f"  📄 Release page: {url}")

    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"  ❌ Gagal akses halaman release: {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # Cari baris yang mengandung "nodpi" dan bukan bundle
    for row in soup.select("div.apkm-card, div.table-row, div.widget_appmanager_apkrow"):
        text = row.get_text(" ", strip=True).lower()
        if "nodpi" in text and "apk" in text and "bundle" not in text:
            link = row.find("a", href=re.compile(r"/apk/google-inc/youtube/.*-nodpi"))
            if link:
                return APKMIRROR_BASE + link["href"]

    # Fallback: href pattern
    for a in soup.find_all("a", href=re.compile(r"/apk/google-inc/youtube/youtube.*-nodpi.*/")):
        return APKMIRROR_BASE + a["href"]

    print("  ⚠ APK universal/nodpi tidak ditemukan di halaman release.")
    return None


def apkmirror_get_download_confirm_url(apk_detail_url: str) -> str | None:
    """Dari halaman detail APK, ambil URL halaman konfirmasi download."""
    print(f"  📄 APK detail: {apk_detail_url}")
    try:
        r = requests.get(apk_detail_url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        btn = (
            soup.find("a", class_=re.compile(r"downloadButton"))
            or soup.find("a", string=re.compile(r"Download APK", re.I))
        )
        if btn and btn.get("href"):
            href = btn["href"]
            return (APKMIRROR_BASE + href) if href.startswith("/") else href
    except Exception as e:
        print(f"  ❌ Error saat parsing APK detail: {e}")
    return None


def apkmirror_get_direct_url(confirm_url: str) -> str | None:
    """Dari halaman konfirmasi, ambil URL download final."""
    print(f"  📄 Confirm page: {confirm_url}")
    try:
        r = requests.get(confirm_url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        link = soup.find("a", href=re.compile(r"download\.php|/wp-content/uploads"))
        if link:
            href = link["href"]
            return (APKMIRROR_BASE + href) if href.startswith("/") else href
    except Exception as e:
        print(f"  ❌ Error saat parsing confirm page: {e}")
    return None


# ── Downloader ────────────────────────────────────────────────────────────────

def download_file(url: str, dest: Path):
    print(f"\n  ⬇ Mengunduh:\n    {url}")
    with requests.get(url, headers=HEADERS, stream=True, timeout=300) as r:
        r.raise_for_status()
        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
                downloaded += len(chunk)
    size_mb = dest.stat().st_size / 1024 / 1024
    print(f"  ✅ Selesai: {dest.name} ({size_mb:.1f} MB)")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", default="youtube")
    parser.add_argument("--arch", default="universal")
    parser.add_argument("--version", default="")
    args = parser.parse_args()

    version = args.version.strip()

    if not version:
        print("🔍 Mendeteksi versi YouTube kompatibel dari Morphe patches...")
        version = get_compatible_version()
        if not version:
            version = "19.16.39"
            print(f"  ⚠ Fallback ke versi: {version}")

    print(f"\n🎯 Target: YouTube {version} [universal]")

    out_file = OUTPUT_DIR / f"youtube-{version}-universal-base.apk"
    if out_file.exists():
        print(f"✅ APK sudah ada, skip download.")
        _save_version(version)
        return

    print(f"\n📡 Scraping APKMirror...")

    # Step 1: halaman APK detail
    apk_detail = apkmirror_find_universal_apk_page(version)
    if not apk_detail:
        print("\n❌ APK universal tidak ditemukan di APKMirror.")
        print("💡 Coba versi lain atau cek manual di: https://www.apkmirror.com/apk/google-inc/youtube/")
        sys.exit(1)

    # Step 2: halaman konfirmasi download
    confirm_url = apkmirror_get_download_confirm_url(apk_detail)
    if not confirm_url:
        print("\n❌ Tombol download tidak ditemukan.")
        sys.exit(1)

    # Step 3: URL download final
    direct_url = apkmirror_get_direct_url(confirm_url)
    if not direct_url:
        print("\n❌ Link download final tidak ditemukan.")
        sys.exit(1)

    # Step 4: unduh file
    download_file(direct_url, out_file)
    _save_version(version)

    print(f"\n✅ Base APK siap: {out_file}")


def _save_version(version: str):
    (OUTPUT_DIR / ".version").write_text(version)


if __name__ == "__main__":
    main()
