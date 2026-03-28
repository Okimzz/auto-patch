# 🔧 Morphe YouTube AutoBuild

Autobuild APK YouTube menggunakan [Morphe](https://github.com/MorpheApp) — otomatis setiap hari via GitHub Actions.

## 📦 Download APK

> Cek [Releases](../../releases/latest) untuk APK terbaru.

| File | Untuk |
|------|-------|
| `*-universal.apk` | Semua HP Android (arm64 & arm32) |

**Syarat:** Install [MicroG-RE dari Morphe](https://github.com/MorpheApp/mite) agar bisa login Google.

---

## ⚙️ Setup (Fork & Jalankan Sendiri)

### 1. Fork repo ini

Klik tombol **Fork** di GitHub.

### 2. Buat Keystore untuk signing

Di komputer lokal kamu:

```bash
git clone https://github.com/USERNAMEMU/morphe-youtube-autobuild
cd morphe-youtube-autobuild
pip install -r requirements.txt
python scripts/generate_keystore.py
```

Ikuti instruksi — simpan **password** dan **alias** yang kamu masukkan.

### 3. Commit keystore

```bash
git add keystore/morphe.keystore
git commit -m "Add keystore"
git push
```

### 4. Tambahkan GitHub Secrets

Di repo GitHub kamu → **Settings → Secrets and variables → Actions → New secret**:

| Nama Secret | Nilai |
|-------------|-------|
| `KEYSTORE_PASSWORD` | Password yang kamu buat tadi |
| `KEY_ALIAS` | Alias yang kamu masukkan (default: `morphe`) |

### 5. Aktifkan GitHub Actions

Buka tab **Actions** → klik **"I understand my workflows, go ahead and enable them"**.

Build akan otomatis berjalan setiap hari jam **13:00 WIB** (06:00 UTC).

---

## 🛠️ Konfigurasi

### Pilih patch (`patches/youtube-morphe.txt`)

```
# Tambah patch
+ nama-patch

# Hapus/skip patch
- nama-patch
```

### Build manual

Buka **Actions → 🔧 Build Morphe YouTube → Run workflow**.

Bisa pilih arsitektur spesifik atau paksa versi YouTube tertentu.

---

## 📁 Struktur Repo

```
.github/workflows/
  build.yml            ← Workflow GitHub Actions
patches/
  youtube-morphe.txt   ← Daftar patch include/exclude
scripts/
  download_tools.py    ← Unduh Morphe CLI, patches, integrations
  download_apk.py      ← Unduh base YouTube APK (APKMirror/APKPure/Uptodown)
  patch.py             ← Patch + sign APK
  generate_keystore.py ← Buat keystore (jalankan sekali lokal)
keystore/
  morphe.keystore      ← Keystore signing (commit ke repo)
requirements.txt
```

---

## ⚠️ Disclaimer

- Bukan build resmi dari tim Morphe.
- Digunakan untuk keperluan edukasi dan kemudahan personal.
- Butuh MicroG-RE agar fitur Google berjalan di non-root.
- Gunakan dengan risiko sendiri.

---

Made with ❤️ — mengacu pada [RookieEnough/Morphe-AutoBuilds](https://github.com/RookieEnough/Morphe-AutoBuilds)
