# ✈️ Holiday Planner & Smart Assistant

Purwarupa aplikasi **Holiday Planner & Smart Assistant** berbasis Python + Streamlit — asisten perjalanan cerdas yang menemanimu dari pra-keberangkatan hingga di destinasi, lengkap dengan dukungan suara.

---

## 🗂️ Struktur Proyek

```
holiday_planner/
├── app.py                   # Entry point — Streamlit main app
├── requirements.txt
└── modules/
    ├── __init__.py
    ├── utils.py             # Shared helpers, data, CSS
    ├── itinerary.py         # Modul 1: Pre-Holiday Itinerary
    ├── departure.py         # Modul 2: H-1 & Hari-H Departure
    ├── emergency.py         # Modul 3: Dynamic Backup Plan
    └── voice.py             # Modul 4: Voice Assistant
```

---

## 🚀 Cara Menjalankan

### 1. Install dependencies

```bash
cd holiday_planner
pip install -r requirements.txt
```

### 2. Jalankan aplikasi

```bash
streamlit run app.py
```

Buka browser di `http://localhost:8501`

---

## 📦 Fitur Lengkap

### 🗓️ Modul 1 — Pre-Holiday Itinerary Cerdas
- Pilih kota tujuan (Bali, Yogyakarta, Jakarta, Lombok)
- Input tanggal, jumlah wisatawan, minat, jam mulai/selesai harian
- Auto-generate jadwal hari per hari dengan:
  - Rata-rata durasi kunjungan (average time visit) per destinasi
  - Slot sarapan, makan siang, makan malam otomatis
  - Waktu tempuh antar destinasi (25 menit rata-rata)
  - Rekomendasi moda transportasi per destinasi (Taxi, Ojek Online, MRT, dll)
  - Jam buka/tutup setiap tempat wisata
  - Tips kunjungan

### ⏰ Modul 2 — Manajemen Waktu Keberangkatan

**Tab H-1:**
- Input jam keberangkatan & jarak hotel → bandara
- Output 3 tier rekomendasi: **Hero**, **Recommended**, **Ideal**
- Kalkulasi otomatis memperhitungkan kondisi lalu lintas:
  - 🔴 Pagi Rush Hour (07:00–09:00) → multiplier 1.7x
  - 🟡 Siang Normal (09:00–16:00) → multiplier 1.2x
  - 🔴 Sore Rush Hour (16:00–19:00) → multiplier 1.8x
  - 🟢 Malam Lancar (19:00–06:00) → multiplier 0.9x

**Tab Hari-H:**
- Input tanggal, jam keberangkatan, nomor gate, waktu saat ini
- Analisis real-time membandingkan kondisi traffic saat ini
- Estimasi waktu jalan kaki ke gate (heuristik berdasarkan nomor gate)
- Status: ✅ Aman / ⚠️ Segera Bersiap / 🚨 Harus Berangkat SEKARANG / ❌ Sangat Mepet
- Countdown timer hingga batas waktu harus berangkat

### 🚨 Modul 3 — Dynamic Backup Plan
- Pilih hari & destinasi yang tutup
- Sistem otomatis hapus destinasi tutup dari jadwal
- Cari pengganti dari database destinasi kota + viral backup destinations
- Sisipkan destinasi baru di slot waktu yang sama
- Re-sort jadwal agar tetap kronologis
- Motivasi mood booster messages
- Demo mode tersedia tanpa perlu buat itinerary dulu

### 🎤 Modul 4 — Voice Assistant
- **Speech-to-Text**: Web Speech API (Chrome/Edge)
  - Dukungan Bahasa Indonesia & Inggris
  - Real-time interim results
  - Tombol "Gunakan Teks Ini" untuk konfirmasi
- **Text-to-Speech**: Speech Synthesis API
  - Auto-read rekomendasi asisten
  - Kontrol rate, pitch, volume
  - Pilihan voice berdasarkan locale
- Tersedia di semua modul via expandable panel
- Toggle on/off dari sidebar & halaman pengaturan

---

## 🗺️ Database Destinasi

| Kota | Jumlah Destinasi | Highlight |
|------|-----------------|-----------|
| Bali | 10 | Tanah Lot, Ubud, Kuta, Uluwatu, Waterbom |
| Yogyakarta | 6 | Borobudur, Prambanan, Kraton, Malioboro |
| Jakarta | 4 | Kota Tua, Ancol, Grand Indonesia, TMII |
| Lombok | 3 | Gili Trawangan, Kuta Lombok, Rinjani |

Dilengkapi 4 viral backup destinations generik yang selalu tersedia.

---

## 🔧 Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| UI Framework | Streamlit 1.32+ |
| Voice Input | Web Speech API (browser native) |
| Voice Output | Speech Synthesis API (browser native) |
| Styling | Custom HTML/CSS via `st.markdown` |
| Data | Static Python dict (dapat diganti API) |
| State | `st.session_state` |

---

## 📌 Catatan Pengembangan Lanjutan

Untuk produksi, fitur-fitur berikut dapat ditambahkan:
- **Google Places API** untuk data destinasi real-time
- **Google Maps Directions API** untuk estimasi lalu lintas akurat
- **FlightAware / AviationStack API** untuk status penerbangan
- **OpenAI / Gemini API** untuk chatbot natural language
- **Firebase / Supabase** untuk simpan itinerary pengguna
- **Notifikasi push** untuk alarm keberangkatan
