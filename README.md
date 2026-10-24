# MedExplain AI 🩺

Purwarupa aplikasi Streamlit untuk penjelasan citra medis berbahasa pasien.

## Cara Menjalankan

```bash
# 1. Masuk ke folder
cd medical_explainer

# 2. Install dependensi
pip install -r requirements.txt

# 3. (Opsional) Tambah API key di environment
# Windows PowerShell:
$env:OPENAI_API_KEY="sk-..."
# atau
$env:GOOGLE_API_KEY="AIza..."

# 4. Jalankan
streamlit run app.py
```

## Fitur

| Fitur | Status |
|---|---|
| Upload JPG / PNG / DICOM | ✅ |
| Input catatan dokter | ✅ |
| Analisis AI (GPT-4o / Gemini) | ✅ (butuh API key) |
| Mode demo offline (tanpa API key) | ✅ |
| Chat Q&A lanjutan | ✅ |

## Menambahkan API Key

Aplikasi secara otomatis mendeteksi environment variable:
- **OpenAI** → `OPENAI_API_KEY` (model: `gpt-4o`)
- **Google Gemini** → `GOOGLE_API_KEY` (model: `gemini-1.5-flash`)

Jika tidak ada key, aplikasi berjalan dalam **mode demo** dengan respons placeholder.

## Deploy ke Streamlit Cloud

1. Push folder ini ke GitHub
2. Buka [share.streamlit.io](https://share.streamlit.io)
3. Pilih repo → `medical_explainer/app.py`
4. Tambahkan secret di **Settings → Secrets**:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```
