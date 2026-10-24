import streamlit as st
import base64
from PIL import Image
import io
import os
import time

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MedExplain AI",
    page_icon="🩺",
    layout="centered",
)

# ── Minimal CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 2rem; max-width: 780px; }
    .chat-bubble-user {
        background: #e8f0fe; border-radius: 12px;
        padding: 10px 14px; margin: 6px 0; text-align: right;
    }
    .chat-bubble-ai {
        background: #f1f3f4; border-radius: 12px;
        padding: 10px 14px; margin: 6px 0;
    }
    .section-title { font-size: 0.85rem; color: #5f6368;
                     text-transform: uppercase; letter-spacing: .05em;
                     margin-bottom: 4px; }
    hr { border: none; border-top: 1px solid #e0e0e0; margin: 1.2rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "analysis_text" not in st.session_state:
    st.session_state.analysis_text = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None
if "doctor_note" not in st.session_state:
    st.session_state.doctor_note = ""

# ── AI helper functions ───────────────────────────────────────────────────────

def encode_image_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def analyze_image_with_ai(image_bytes: bytes, doctor_note: str) -> str:
    """
    Kirim gambar + catatan dokter ke LLM multimodal.
    Mendukung: OpenAI GPT-4o · Google Gemini · placeholder offline.
    Atur environment variable OPENAI_API_KEY atau GOOGLE_API_KEY.
    """
    openai_key = os.getenv("OPENAI_API_KEY", "")
    google_key = os.getenv("GOOGLE_API_KEY", "")

    system_prompt = (
        "Kamu adalah asisten medis edukatif yang bertugas menjelaskan citra medis "
        "kepada pasien awam dengan bahasa yang mudah dipahami namun tetap akurat secara medis. "
        "Gunakan poin-poin singkat. Selalu ingatkan pengguna untuk berkonsultasi langsung "
        "dengan dokter untuk diagnosis dan pengobatan."
    )

    user_prompt = (
        "Jelaskan apa yang terlihat pada citra medis ini dengan bahasa sederhana. "
        "Sebutkan: (1) Jenis citra / bagian tubuh yang tampak, "
        "(2) Temuan utama yang terlihat, "
        "(3) Kemungkinan kondisi medis yang terkait (jika ada), "
        "(4) Saran umum bagi pasien."
    )
    if doctor_note.strip():
        user_prompt += (
            f"\n\nCatatan tambahan dari dokter yang perlu dirangkum ulang:\n\"{doctor_note.strip()}\""
        )

    # ── OpenAI GPT-4o ─────────────────────────────────────────────────────────
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            b64 = encode_image_base64(image_bytes)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                            },
                        ],
                    },
                ],
                max_tokens=700,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ OpenAI error: {e}"

    # ── Google Gemini ─────────────────────────────────────────────────────────
    if google_key:
        try:
            import google.generativeai as genai
            from google.generativeai.types import HarmCategory, HarmBlockThreshold

            genai.configure(api_key=google_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            img = Image.open(io.BytesIO(image_bytes))
            full_prompt = system_prompt + "\n\n" + user_prompt
            response = model.generate_content(
                [full_prompt, img],
                safety_settings={
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
                },
            )
            return response.text
        except Exception as e:
            return f"⚠️ Gemini error: {e}"

    # ── Placeholder (offline) ─────────────────────────────────────────────────
    note_section = ""
    if doctor_note.strip():
        note_section = (
            f"\n\n**📋 Ringkasan Catatan Dokter:**\n"
            f"> {doctor_note.strip()}\n\n"
            "Dokter Anda telah memberikan penjelasan di atas. Pastikan Anda memahaminya "
            "dan tanyakan kembali jika ada yang kurang jelas pada kunjungan berikutnya."
        )

    return (
        "**🔍 Analisis Citra Medis (Demo — Tanpa Koneksi AI)**\n\n"
        "**1. Jenis Citra**\n"
        "Gambar yang diunggah tampak merupakan citra medis (X-Ray / CT / MRI / USG — "
        "terdeteksi dari konteks visual).\n\n"
        "**2. Temuan Utama**\n"
        "- Struktur anatomi terlihat dalam batas normal secara umum.\n"
        "- Tidak ada kelainan mencolok yang dapat didentifikasi pada demonstrasi ini.\n\n"
        "**3. Kemungkinan Kondisi**\n"
        "- Diperlukan analisis AI nyata untuk interpretasi klinis yang akurat.\n\n"
        "**4. Saran untuk Pasien**\n"
        "- Selalu diskusikan hasil citra ini langsung dengan dokter Anda.\n"
        "- Jangan membuat keputusan medis hanya berdasarkan penjelasan AI.\n"
        + note_section
        + "\n\n> ⚙️ *Untuk analisis nyata, tambahkan `OPENAI_API_KEY` atau `GOOGLE_API_KEY` "
        "ke environment variable atau file `.env`.*"
    )


def chat_with_ai(question: str, analysis_context: str, history: list, image_bytes: bytes) -> str:
    """Lanjutan Q&A berdasarkan konteks analisis."""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    google_key = os.getenv("GOOGLE_API_KEY", "")

    system_prompt = (
        "Kamu adalah asisten medis edukatif. Kamu sudah menganalisis sebuah citra medis "
        "dan pengguna ingin bertanya lebih lanjut. Jawab dengan jelas, empati, dan ingatkan "
        "bahwa diagnosis final tetap harus dari dokter.\n\n"
        f"Konteks analisis sebelumnya:\n{analysis_context}"
    )

    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            messages = [{"role": "system", "content": system_prompt}]
            for h in history[-6:]:  # batasi konteks 6 pesan terakhir
                messages.append({"role": h["role"], "content": h["content"]})
            messages.append({"role": "user", "content": question})
            response = client.chat.completions.create(
                model="gpt-4o", messages=messages, max_tokens=400
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ Error: {e}"

    if google_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=google_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            history_text = "\n".join(
                f"{'Pasien' if h['role']=='user' else 'AI'}: {h['content']}"
                for h in history[-6:]
            )
            full = f"{system_prompt}\n\nRiwayat percakapan:\n{history_text}\n\nPasien: {question}"
            response = model.generate_content(full)
            return response.text
        except Exception as e:
            return f"⚠️ Error: {e}"

    # Placeholder Q&A
    answers = {
        "apakah": "Berdasarkan analisis demo, kondisi yang terlihat masih dalam parameter umum. Namun untuk jawaban definitif, silakan konsultasikan dengan dokter Anda.",
        "apa": "Pertanyaan bagus! Pada citra ini secara umum terlihat struktur anatomi yang perlu dievaluasi lebih lanjut oleh dokter spesialis.",
        "bagaimana": "Dokter Anda adalah yang paling tepat menjelaskan prosedur selanjutnya. Citra ini bisa menjadi bahan diskusi yang baik.",
        "berbahaya": "Demo AI tidak dapat menentukan tingkat bahaya. Selalu konsultasikan dengan dokter untuk penilaian risiko yang tepat.",
        "pengobatan": "Pengobatan harus ditentukan oleh dokter berdasarkan evaluasi menyeluruh, bukan hanya dari citra medis.",
    }
    question_lower = question.lower()
    for kw, ans in answers.items():
        if kw in question_lower:
            return ans
    return (
        "Terima kasih atas pertanyaannya. Dalam mode demo ini saya tidak dapat memberikan "
        "analisis mendalam. Namun yang terpenting: selalu diskusikan pertanyaan medis Anda "
        "langsung dengan dokter atau tenaga kesehatan yang menangani Anda. "
        "Untuk jawaban AI nyata, hubungkan aplikasi dengan API key."
    )


# ── UI ────────────────────────────────────────────────────────────────────────

st.title("🩺 MedExplain AI")
st.caption("Asisten penjelasan citra medis berbahasa pasien · Prototype")
st.markdown("<hr>", unsafe_allow_html=True)

# ── Step 1: Upload ────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">1 · Upload Citra Medis</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Pilih file gambar", type=["jpg", "jpeg", "png", "dcm"], label_visibility="collapsed"
)

if uploaded_file:
    # Baca bytes
    image_bytes = uploaded_file.read()
    st.session_state.image_bytes = image_bytes

    # Tampilkan preview (DICOM ditampilkan sebagai placeholder teks)
    if uploaded_file.name.endswith(".dcm"):
        st.info("📄 File DICOM terdeteksi. Preview tidak tersedia — analisis tetap akan berjalan.")
    else:
        img = Image.open(io.BytesIO(image_bytes))
        st.image(img, use_container_width=True, caption=uploaded_file.name)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Step 2: Doctor note ───────────────────────────────────────────────────────
st.markdown('<p class="section-title">2 · Catatan Dokter (Opsional)</p>', unsafe_allow_html=True)
doctor_note = st.text_area(
    "Tempel atau ketik penjelasan/catatan dokter yang ingin dirangkum ulang",
    placeholder="Contoh: Dokter bilang ada infiltrat di lobus kanan bawah, kemungkinan pneumonia...",
    height=100,
    label_visibility="collapsed",
)
st.session_state.doctor_note = doctor_note

st.markdown("<hr>", unsafe_allow_html=True)

# ── Step 3: Analyze ───────────────────────────────────────────────────────────
st.markdown('<p class="section-title">3 · Analisis AI</p>', unsafe_allow_html=True)

if st.button("🔬 Analisis Sekarang", use_container_width=True, type="primary"):
    if not st.session_state.image_bytes:
        st.warning("Silakan upload citra medis terlebih dahulu.")
    else:
        with st.spinner("Menganalisis citra..."):
            result = analyze_image_with_ai(
                st.session_state.image_bytes, st.session_state.doctor_note
            )
        st.session_state.analysis_text = result
        st.session_state.analysis_done = True
        st.session_state.chat_history = []  # reset chat saat analisis baru

if st.session_state.analysis_done:
    st.markdown(st.session_state.analysis_text)
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Step 4: Q&A Chat ──────────────────────────────────────────────────────
    st.markdown('<p class="section-title">4 · Tanya Jawab Lanjutan</p>', unsafe_allow_html=True)

    # Tampilkan riwayat chat
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-bubble-user">🧑 {msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-bubble-ai">🤖 {msg["content"]}</div>',
                unsafe_allow_html=True,
            )

    with st.form("chat_form", clear_on_submit=True):
        user_q = st.text_input(
            "Tulis pertanyaan Anda",
            placeholder="Contoh: Apakah kondisi ini berbahaya?",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Kirim →", use_container_width=True)

    if submitted and user_q.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_q.strip()})
        with st.spinner("Menjawab..."):
            answer = chat_with_ai(
                user_q.strip(),
                st.session_state.analysis_text,
                st.session_state.chat_history,
                st.session_state.image_bytes,
            )
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.caption(
    "⚠️ MedExplain AI hanyalah alat bantu edukatif. "
    "Bukan pengganti diagnosis atau saran medis profesional. "
    "Selalu konsultasikan kondisi kesehatan Anda dengan dokter."
)
