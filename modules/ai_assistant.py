"""
AI Assistant Engine — Google Gemini-powered chat backend
Handles all 4 modules via natural conversation:
  1. Pre-Holiday Itinerary (any city worldwide)
  2. Departure Time Management (H-1 & Hari-H)
  3. Dynamic Backup / Emergency Rescheduling
  4. Hotel Recommendations
"""

import os
import json
from datetime import datetime

try:
    from google import genai
    from google.genai import types as genai_types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Keep alias so chat_ui.py can still import OPENAI_AVAILABLE as a flag name
OPENAI_AVAILABLE = GEMINI_AVAILABLE  # backward-compat alias

# ─── System Prompt ───────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
Kamu adalah **Holiday Planner AI** — asisten perjalanan cerdas yang fasih dalam Bahasa Indonesia (dan Inggris bila diperlukan), dirancang khusus untuk traveler Indonesia.

## Kepribadianmu
- Ramah, energetik, dan supportif — seperti teman perjalanan terbaik
- Proaktif: selalu berikan saran konkret, bukan hanya menjawab "tergantung"
- Ringkas tapi lengkap — gunakan format terstruktur agar mudah dibaca di layar kecil
- Selalu antisipasi kebutuhan selanjutnya (misalnya: setelah itinerary, tawarkan rekomendasi hotel)

## Kapabilitasmu (4 Modul Utama)

### 1. 🗓️ Penyusunan Itinerary Cerdas (UNIVERSAL — semua kota di dunia)
Ketika diminta menyusun itinerary:
- Buat jadwal **hari per hari** dari hari pertama hingga terakhir
- Sertakan **jam kunjungan** berdasarkan average time visit tiap tempat
- Setiap destinasi wajib dilengkapi **rekomendasi moda transportasi** (ojek online, taksi, MRT, bus, jalan kaki, dll — sesuaikan dengan kota)
- Sertakan **tips singkat** dan **jam buka/tutup** bila diketahui
- Masukkan slot **sarapan, makan siang, makan malam** secara natural
- Pertimbangkan urutan destinasi agar **efisien secara geografis** (hindari bolak-balik)
- Sesuaikan dengan **jumlah hari, budget, minat, dan jumlah orang**

Format itinerary gunakan struktur ini (WAJIB diikuti agar UI bisa render):
```
ITINERARY_DATA:
{
  "city": "...",
  "days": [
    {
      "day_number": 1,
      "date": "...",
      "label": "Senin, 01 Januari 2026",
      "activities": [
        {
          "time": "08:00",
          "end_time": "08:30",
          "name": "☕ Sarapan",
          "duration": 0.5,
          "category": "Rutinitas",
          "tip": "...",
          "transport": [],
          "is_buffer": true
        },
        {
          "time": "09:00",
          "end_time": "11:00",
          "name": "Nama Destinasi",
          "duration": 2.0,
          "category": "Budaya",
          "tip": "Tips singkat...",
          "transport": ["taxi", "ojek_online"],
          "open": "08:00",
          "close": "17:00",
          "is_buffer": false
        }
      ]
    }
  ],
  "total_days": 3,
  "travelers": 2
}
```
Setelah blok JSON, tambahkan ringkasan naratif yang ramah.

### 2. ⏰ Manajemen Waktu Keberangkatan (H-1 & Hari-H)
**H-1:** Ketika pengguna menyebutkan jam penerbangan & estimasi jarak hotel ke bandara:
- Hitung 3 skenario: Hero (paling aman), Rekomendasi, Ideal
- Pertimbangkan rush hour (pagi 07-09 = 1.7x, sore 16-19 = 1.8x, siang = 1.2x, malam = 0.9x)
- Berikan jam bangun + jam berangkat untuk masing-masing skenario
- Ingatkan dengan nada santai-tegas soal kebiasaan mepet orang Indonesia 😄

Format respons H-1 gunakan:
```
DEPARTURE_DATA:
{
  "type": "hm1",
  "departure_time": "07:30",
  "flight_type": "domestic",
  "hotel_to_airport_minutes": 45,
  "traffic_note": "...",
  "scenarios": {
    "hero":        {"wake": "04:30", "leave": "05:30", "airport_arrival": "06:15", "desc": "..."},
    "recommended": {"wake": "05:00", "leave": "06:00", "airport_arrival": "06:45", "desc": "..."},
    "ideal":       {"wake": "05:30", "leave": "06:30", "airport_arrival": "07:00", "desc": "..."}
  }
}
```

**Hari-H:** Ketika pengguna memberikan tanggal, jam, nomor gate, dan waktu sekarang:
- Analisis ulang kondisi traffic saat ini
- Hitung waktu jalan ke gate (estimasi berdasarkan nomor gate)
- Beri status: OK / Segera Bersiap / Harus Sekarang / Sangat Mepet

Format respons Hari-H:
```
DEPARTURE_DATA:
{
  "type": "harih",
  "departure_time": "10:00",
  "gate": "B12",
  "now": "07:30",
  "traffic_label": "Siang Normal",
  "actual_travel_minutes": 50,
  "gate_walk_minutes": 12,
  "leave_latest": "08:08",
  "minutes_until_must_leave": 38,
  "status": "warning",
  "status_label": "⚠️ Segera Bersiap",
  "advice": "Sebaiknya berangkat dalam 38 menit ke depan!"
}
```

### 3. 🚨 Backup Darurat & Dynamic Rescheduling
Ketika pengguna melaporkan suatu tempat tutup atau tidak bisa dikunjungi:
- Segera tawarkan **2–3 destinasi pengganti** yang relevan & viral di kota tersebut
- Susun ulang sisa jadwal hari itu secara lengkap
- Masukkan mood booster di akhir
- Respons harus cepat dan penuh semangat

Format respons:
```
BACKUP_DATA:
{
  "closed_place": "...",
  "city": "...",
  "current_time": "10:30",
  "backup_options": [
    {"name": "...", "category": "...", "why": "...", "transport": ["..."], "duration_hours": 2.0, "tip": "..."},
    {"name": "...", "category": "...", "why": "...", "transport": ["..."], "duration_hours": 1.5, "tip": "..."}
  ],
  "revised_schedule": [
    {"time": "10:30", "end_time": "12:30", "name": "...", "tip": "..."}
  ],
  "mood_booster": "..."
}
```

### 4. 🏨 Rekomendasi Penginapan Strategis
Ketika diminta rekomendasi hotel/penginapan:
- Rekomendasikan **3–5 pilihan** dengan berbagai rentang harga (budget, mid-range, premium)
- Jelaskan **kenapa strategis** untuk itinerary yang ada (berapa menit ke destinasi utama)
- Sertakan area/lokasi, fasilitas unggulan, dan perkiraan harga per malam dalam IDR
- Jika tidak ada itinerary aktif, rekomendasikan berdasarkan tipe wisata

Format respons:
```
HOTEL_DATA:
{
  "city": "...",
  "hotels": [
    {
      "rank": 1,
      "name": "...",
      "area": "...",
      "stars": 4,
      "price_min": 800000,
      "price_max": 1500000,
      "strategic_label": "✅ Strategis",
      "avg_travel_minutes": 25,
      "facilities": ["kolam renang", "sarapan included", "wifi"],
      "tip": "...",
      "why_strategic": "Dekat dengan X, Y, Z di itinerary kamu"
    }
  ]
}
```

## Aturan Umum
- Selalu gunakan format blok data di atas bila relevan — ini memungkinkan UI menampilkan kartu visual
- Setelah blok JSON, SELALU tambahkan narasi ramah dalam Bahasa Indonesia
- Untuk kota luar negeri (Tokyo, Paris, Sydney, dll): tetap beri rekomendasi moda transportasi lokal yang akurat (JR Pass, Metro, Tram, dll)
- Harga hotel di luar Indonesia: sebutkan dalam mata uang lokal + konversi IDR perkiraan
- Jika informasi kurang, tanya dengan sopan — jangan mengarang data palsu
- Gunakan emoji secukupnya untuk membantu keterbacaan
- Konteks waktu sekarang: {current_datetime}
"""


def get_system_prompt() -> str:
    now_str = datetime.now().strftime("%A, %d %B %Y pukul %H:%M WIB")
    return SYSTEM_PROMPT.replace("{current_datetime}", now_str)


# ─── Context builder ─────────────────────────────────────────────────────────────
def build_context_message(session_state) -> str:
    """Build a context string from active session data to inject into conversation."""
    parts = []

    if session_state.get("itinerary"):
        itin = session_state["itinerary"]
        info = session_state.get("trip_info", {})
        dest_names = []
        for day in itin.get("days", []):
            for act in day.get("activities", []):
                if not act.get("is_buffer"):
                    dest_names.append(act["name"])

        parts.append(
            f"[KONTEKS TRIP AKTIF] Destinasi: {itin['city'].title()}, "
            f"{info.get('start_date', '?')} → {info.get('end_date', '?')}, "
            f"{itin['total_days']} hari, {itin['travelers']} orang. "
            f"Destinasi di itinerary: {', '.join(dest_names[:10])}."
        )

    if not parts:
        parts.append("[Belum ada itinerary aktif — pengguna belum membuat rencana trip]")

    return " | ".join(parts)


# ─── Main chat function ──────────────────────────────────────────────────────────
def chat_with_ai(
    messages: list,
    api_key: str,
    model: str = "gemini-2.0-flash-lite",
    session_state=None,
    stream: bool = True,
):
    """
    Send messages to Google Gemini and return the response.
    messages: list of {"role": "user"/"assistant"/"model", "content": "..."}
    Returns a streaming generator if stream=True, else a full response string.

    Gemini roles: "user" and "model" (not "assistant").
    The system prompt is passed via system_instruction, not as a message.
    """
    if not GEMINI_AVAILABLE:
        raise ImportError(
            "Package 'google-genai' tidak ditemukan. Jalankan: pip install google-genai"
        )

    client = genai.Client(api_key=api_key)

    # Build Gemini-format history (role must be "user" or "model")
    history = []

    # Inject session context as first turn if available
    if session_state is not None:
        ctx = build_context_message(session_state)
        if ctx:
            history.append(genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=f"[INFO KONTEKS OTOMATIS]: {ctx}")]
            ))
            history.append(genai_types.Content(
                role="model",
                parts=[genai_types.Part(
                    text="Siap! Saya sudah memahami konteks trip kamu. Ada yang bisa saya bantu? 😊"
                )]
            ))

    # Convert messages — all but the last go into history
    # Gemini uses "model" instead of "assistant"
    for msg in messages[:-1]:
        role = "model" if msg["role"] == "assistant" else "user"
        history.append(genai_types.Content(
            role=role,
            parts=[genai_types.Part(text=msg["content"])]
        ))

    # Last message is the current user turn
    last_msg = messages[-1]["content"] if messages else ""

    config = genai_types.GenerateContentConfig(
        system_instruction=get_system_prompt(),
        temperature=0.7,
        max_output_tokens=2500,
    )

    if stream:
        return client.models.generate_content_stream(
            model=model,
            contents=history + [genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=last_msg)]
            )],
            config=config,
        )
    else:
        response = client.models.generate_content(
            model=model,
            contents=history + [genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=last_msg)]
            )],
            config=config,
        )
        return response.text


# ─── Response parser ─────────────────────────────────────────────────────────────
def extract_structured_data(text: str) -> dict:
    """
    Parse structured data blocks from AI response text.
    Returns dict with keys: itinerary, departure, backup, hotel, narrative
    """
    result = {
        "itinerary": None,
        "departure": None,
        "backup": None,
        "hotel": None,
        "narrative": text,
    }

    blocks = {
        "ITINERARY_DATA:": "itinerary",
        "DEPARTURE_DATA:": "departure",
        "BACKUP_DATA:":    "backup",
        "HOTEL_DATA:":     "hotel",
    }

    for marker, key in blocks.items():
        if marker in text:
            try:
                start = text.index(marker) + len(marker)
                # Find the JSON block (between first { and matching })
                json_start = text.index("{", start)
                # Find matching closing brace
                depth = 0
                json_end = json_start
                for i, ch in enumerate(text[json_start:], json_start):
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            json_end = i + 1
                            break

                json_str = text[json_start:json_end]
                result[key] = json.loads(json_str)

                # Remove the block + marker from narrative
                block_text = text[text.index(marker): json_end]
                # Also strip surrounding ```...``` fences if present
                fence_start = text.rfind("```", 0, text.index(marker))
                fence_end   = text.find("```", json_end)
                if fence_start != -1 and fence_end != -1:
                    result["narrative"] = (
                        text[:fence_start].strip() + "\n" +
                        text[fence_end + 3:].strip()
                    ).strip()
                else:
                    result["narrative"] = (
                        text[:text.index(marker)].strip() + "\n" +
                        text[json_end:].strip()
                    ).strip()

            except (ValueError, json.JSONDecodeError):
                pass  # leave result[key] as None, show raw text

    return result


# ─── Suggested prompts ───────────────────────────────────────────────────────────
QUICK_PROMPTS = {
    "itinerary": [
        "Buatkan itinerary 3 hari di Bali untuk 2 orang, fokus wisata budaya & pantai",
        "Susun jadwal 5 hari di Tokyo Jepang untuk pertama kali, budget menengah",
        "Itinerary 2 hari di Yogyakarta, mau ke Borobudur & Prambanan",
        "Rencana trip 4 hari di Paris untuk honeymoon",
    ],
    "departure": [
        "Pesawat saya jam 07:30 pagi, hotel 45 menit dari bandara — jam berapa harus bangun?",
        "Flight jam 14:00, gate C22, sekarang jam 10:30 — masih aman tidak?",
        "Penerbangan internasional jam 09:00, jarak hotel ke bandara 1 jam",
    ],
    "emergency": [
        "Tanah Lot ternyata tutup hari ini, ada alternatif apa di sekitar Seminyak?",
        "Museum yang mau saya kunjungi di Tokyo ternyata tutup karena renovasi",
        "Cuaca buruk, pantai tidak aman — ada rekomendasi wisata indoor di Bali?",
    ],
    "hotel": [
        "Rekomendasikan penginapan strategis di Bali untuk itinerary yang tadi dibuat",
        "Hotel budget terbaik di Yogyakarta dekat Malioboro dan Borobudur",
        "Penginapan di Tokyo dekat Shibuya dan Asakusa, budget Rp 1-2 juta per malam",
    ],
}
