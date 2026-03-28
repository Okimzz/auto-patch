#!/usr/bin/env python3
"""
download_tools.py
Mengambil rilis terbaru Morphe CLI, Patches, dan Integrations dari GitHub.
"""

import os
import sys
import json
import requests
from pathlib import Path

TOOLS_DIR = Path("tools")
TOOLS_DIR.mkdir(exist_ok=True)

MORPHE_REPOS = {
    "cli": "MorpheApp/morphe-cli",
    "patches": "MorpheApp/morphe-patches",
    "integrations": "MorpheApp/morphe-integrations",
}

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}


def get_latest_release(repo: str) -> dict:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def download_asset(url: str, dest: Path):
    print(f"  ⬇ Downloading {dest.name}...")
    with requests.get(url, headers=HEADERS, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"  ✅ Saved to {dest}")


def main():
    versions = {}

    for name, repo in MORPHE_REPOS.items():
        print(f"\n🔍 Fetching latest {name} from {repo}...")
        release = get_latest_release(repo)
        tag = release["tag_name"]
        print(f"   Tag: {tag}")
        versions[name] = tag

        for asset in release["assets"]:
            aname = asset["name"]
            # Ambil .jar untuk cli dan patches, .apk untuk integrations
            if name == "cli" and aname.endswith(".jar"):
                download_asset(asset["browser_download_url"], TOOLS_DIR / "morphe-cli.jar")
            elif name == "patches" and aname.endswith(".rvp"):
                download_asset(asset["browser_download_url"], TOOLS_DIR / "morphe-patches.rvp")
            elif name == "integrations" and aname.endswith(".apk"):
                download_asset(asset["browser_download_url"], TOOLS_DIR / "morphe-integrations.apk")

    # Simpan versi untuk dipakai script lain
    with open(TOOLS_DIR / "versions.json", "w") as f:
        json.dump(versions, f, indent=2)

    print("\n✅ Semua Morphe tools berhasil diunduh!")
    print(json.dumps(versions, indent=2))


if __name__ == "__main__":
    main()
