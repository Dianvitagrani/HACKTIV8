import streamlit as st
from PIL import Image
import io
import os
import json
import re

# ── Page config ───────────────────────────────────────────────────────────────
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
    .bone-card {
        background: #f8f9fa; border: 1px solid #e0e0e0;
        border-radius: 12px; padding: 16px 20px; margin: 10px 0;
    }
    .status-normal   { color: #1e7e34; font-weight: 600; }
    .status-delayed  { color: #c0392b; font-weight: 600; }
    .status-advanced { color: #d35400; font-weight: 600; }
    hr { border: none; border-top: 1px solid #e0e0e0; margin: 1.4rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for _k, _v in {
    "analysis_done": False, "analysis_text": "", "chat_history": [], "image_bytes": None,
    "bone_done": False, "bone_result": {}, "bone_chat_history": [], "bone_image_bytes": None,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_api_key() -> str:
    key = os.getenv("GOOGLE_API_KEY", "")
    if not key:
        try:
            key = st.secrets["GOOGLE_API_KEY"]
        except (KeyError, FileNotFoundError):
            key = ""
    return key


def _gemini(parts: list = None, text: str = "") -> str:
    """Panggil Gemini. `parts` = list[str | PIL.Image], `text` = prompt teks saja."""
    key = get_api_key()
    if not key:
        return ""
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=key)
        contents = []
        for p in (parts or []):
            contents.append(types.Part.from_text(text=p) if isinstance(p, str) else p)
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite-preview-06-17",
            contents=contents or text,
        )
        return response.text
    except ImportError:
        pass
    except Exception as e:
        return f"⚠️ Gemini error: {e}"
    try:
        import google.generativeai as g
        g.configure(api_key=key)
        m = g.GenerativeModel("gemini-1.5-flash")
        response = m.generate_content(parts if parts else text)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini error: {e}"


# ── AI: analisis citra umum ───────────────────────────────────────────────────

def analyze_image(image_bytes: bytes, doctor_note: str) -> str:
    sys_p = (
        "Kamu adalah asisten medis edukatif yang menjelaskan citra medis kepada pasien awam "
        "dengan bahasa mudah dipahami namun tetap akurat. Gunakan poin-poin singkat. "
        "Selalu ingatkan untuk berkonsultasi dengan dokter."
    )
    usr_p = (
        "Jelaskan citra medis ini dengan bahasa sederhana: "
        "(1) Jenis citra / bagian tubuh, (2) Temuan utama, "
        "(3) Kemungkinan kondisi medis, (4) Saran umum bagi pasien."
    )
    if doctor_note.strip():
        usr_p += f'\n\nCatatan dokter yang perlu dirangkum: "{doctor_note.strip()}"'

    img = Image.open(io.BytesIO(image_bytes))
    out = _gemini([sys_p + "\n\n" + usr_p, img])
    if out:
        return out

    extra = ""
    if doctor_note.strip():
        extra = f"\n\n**📋 Catatan Dokter:**\n> {doctor_note.strip()}"
    return (
        "**🔍 Analisis Citra Medis (Demo — tanpa API key)**\n\n"
        "**1. Jenis Citra** — Citra medis terdeteksi (X-Ray / CT / MRI / USG).\n\n"
        "**2. Temuan Utama** — Struktur anatomi dalam batas normal secara umum.\n\n"
        "**3. Kemungkinan Kondisi** — Diperlukan analisis AI nyata.\n\n"
        "**4. Saran** — Diskusikan hasil ini langsung dengan dokter Anda."
        + extra
        + "\n\n> ⚙️ *Tambahkan `GOOGLE_API_KEY` ke Streamlit Secrets untuk analisis nyata.*"
    )


def chat_general(question: str, context: str, history: list) -> str:
    sys_p = (
        "Kamu adalah asisten medis edukatif. Kamu sudah menganalisis citra medis. "
        "Jawab dengan jelas dan empati. Ingatkan bahwa diagnosis final harus dari dokter.\n\n"
        f"Konteks analisis:\n{context}"
    )
    hist = "\n".join(f"{'Pasien' if h['role']=='user' else 'AI'}: {h['content']}" for h in history[-6:])
    out = _gemini(text=f"{sys_p}\n\nRiwayat:\n{hist}\n\nPasien: {question}")
    return out or "Silakan konsultasikan langsung dengan dokter Anda."


# ── AI: bone age ──────────────────────────────────────────────────────────────

def analyze_bone_age(image_bytes: bytes, chron_months: int, sex: str) -> dict:
    chron_years = chron_months / 12
    sys_p = (
        "Kamu adalah radiolog AI terlatih mengestimasi usia tulang (bone age) "
        "dari X-ray tangan menggunakan metode Greulich-Pyle."
    )
    usr_p = (
        f"X-ray tangan kanan, pasien {sex}, usia kronologis {chron_years:.1f} tahun ({chron_months} bulan).\n\n"
        "Lakukan:\n"
        "1. Estimasi bone age dalam bulan dari osifikasi & epifisis.\n"
        "2. Tentukan status:\n"
        "   - NORMAL (selisih < 12 bulan)\n"
        "   - DELAYED (bone age < kronologis, selisih ≥ 12 bulan)\n"
        "   - ADVANCED (bone age > kronologis, selisih ≥ 12 bulan)\n"
        "3. Jelaskan temuan tulang spesifik.\n"
        "4. Berikan kemungkinan penyebab & rekomendasi.\n\n"
        "Balas HANYA dengan JSON murni (tanpa markdown), format:\n"
        '{"bone_age_months":<int>,"status":"NORMAL|DELAYED|ADVANCED","difference_months":<int>,'
        '"findings":"...","explanation":"...","possible_causes":"...","recommendations":"..."}'
    )
    img = Image.open(io.BytesIO(image_bytes))
    raw = _gemini([sys_p + "\n\n" + usr_p, img])

    if not raw or raw.startswith("⚠️"):
        return {
            "bone_age_months": chron_months, "status": "DEMO", "difference_months": 0,
            "findings": "Mode demo — tidak ada API key.",
            "explanation": "Tambahkan GOOGLE_API_KEY untuk analisis nyata.",
            "possible_causes": "-", "recommendations": "Konsultasikan dengan dokter spesialis anak.",
        }
    try:
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        return json.loads(cleaned)
    except Exception:
        return {
            "bone_age_months": None, "status": "UNKNOWN", "difference_months": None,
            "findings": raw, "explanation": raw, "possible_causes": "", "recommendations": "",
        }


def chat_bone(question: str, context: str, history: list) -> str:
    sys_p = (
        "Kamu adalah asisten medis ahli pertumbuhan anak dan radiologi tulang. "
        "Kamu sudah menganalisis bone age dari X-ray tangan. "
        "Jawab dengan empati, bahasa mudah dipahami. "
        "Ingatkan untuk konsultasi SpA atau endokrinologi anak.\n\n"
        f"Konteks bone age:\n{context}"
    )
    hist = "\n".join(f"{'Pasien' if h['role']=='user' else 'AI'}: {h['content']}" for h in history[-6:])
    out = _gemini(text=f"{sys_p}\n\nRiwayat:\n{hist}\n\nPasien: {question}")
    return out or "Silakan konsultasikan langsung dengan dokter spesialis anak."


# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════

st.title("🩺 MedExplain AI")
st.caption("Asisten penjelasan citra medis berbahasa pasien · Prototype")

_k = get_api_key()
if _k:
    st.success(f"✅ GOOGLE_API_KEY terbaca ({len(_k)} karakter)")
else:
    st.warning("⚠️ GOOGLE_API_KEY belum terdeteksi — berjalan dalam mode demo.")

# ─────────────────────────────────────────────────────────────────────────────
# BAGIAN 1 — Analisis Citra Umum
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("🔬 Analisis Citra Medis")

st.markdown('<p class="section-title">1 · Upload Citra</p>', unsafe_allow_html=True)
uploaded = st.file_uploader("Upload citra", type=["jpg","jpeg","png","dcm"],
                             label_visibility="collapsed", key="up_general")
if uploaded:
    raw_bytes = uploaded.read()
    st.session_state.image_bytes = raw_bytes
    if uploaded.name.endswith(".dcm"):
        st.info("📄 File DICOM — preview tidak tersedia, analisis tetap berjalan.")
    else:
        st.image(Image.open(io.BytesIO(raw_bytes)), use_container_width=True, caption=uploaded.name)

st.markdown('<p class="section-title" style="margin-top:1rem">2 · Catatan Dokter (Opsional)</p>',
            unsafe_allow_html=True)
doctor_note = st.text_area("Catatan dokter", height=90, label_visibility="collapsed",
                           placeholder="Contoh: ada infiltrat di lobus kanan bawah, kemungkinan pneumonia...")

st.markdown('<p class="section-title" style="margin-top:1rem">3 · Analisis AI</p>',
            unsafe_allow_html=True)
if st.button("🔬 Analisis Sekarang", use_container_width=True, type="primary"):
    if not st.session_state.image_bytes:
        st.warning("Silakan upload citra terlebih dahulu.")
    else:
        with st.spinner("Menganalisis citra..."):
            st.session_state.analysis_text = analyze_image(st.session_state.image_bytes, doctor_note)
        st.session_state.analysis_done = True
        st.session_state.chat_history = []

if st.session_state.analysis_done:
    st.markdown(st.session_state.analysis_text)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<p class="section-title">4 · Tanya Jawab Lanjutan</p>', unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        cls = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-ai"
        icon = "🧑" if msg["role"] == "user" else "🤖"
        st.markdown(f'<div class="{cls}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)

    with st.form("form_general", clear_on_submit=True):
        q = st.text_input("Pertanyaan", placeholder="Apakah kondisi ini berbahaya?",
                          label_visibility="collapsed")
        if st.form_submit_button("Kirim →", use_container_width=True) and q.strip():
            st.session_state.chat_history.append({"role": "user", "content": q.strip()})
            with st.spinner("Menjawab..."):
                ans = chat_general(q.strip(), st.session_state.analysis_text,
                                   st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": ans})
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# BAGIAN 2 — Bone Age Detection
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("🦴 Deteksi Usia Tulang (Bone Age)")
st.caption("Estimasi kematangan tulang dari X-ray tangan · Metode Greulich-Pyle · Hanya untuk edukasi.")

st.markdown('<p class="section-title">1 · Upload X-Ray Tangan</p>', unsafe_allow_html=True)
st.caption("Gunakan X-ray tangan kanan (PA view). Format: JPG / PNG.")
bone_file = st.file_uploader("Upload X-ray", type=["jpg","jpeg","png"],
                              label_visibility="collapsed", key="up_bone")
if bone_file:
    bone_bytes = bone_file.read()
    st.session_state.bone_image_bytes = bone_bytes
    st.image(Image.open(io.BytesIO(bone_bytes)), use_container_width=True, caption="X-Ray Tangan")

st.markdown('<p class="section-title" style="margin-top:1rem">2 · Data Pasien</p>',
            unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
age_y = c1.number_input("Usia (tahun)", 0, 20, 8, 1)
age_m = c2.number_input("Bulan tambahan", 0, 11, 0, 1)
sex   = c3.selectbox("Jenis kelamin", ["Laki-laki", "Perempuan"])
total_m = age_y * 12 + age_m
st.caption(f"Usia kronologis: **{age_y} tahun {age_m} bulan** ({total_m} bulan)")

st.markdown('<p class="section-title" style="margin-top:1rem">3 · Analisis Bone Age</p>',
            unsafe_allow_html=True)
if st.button("🦴 Analisis Usia Tulang", use_container_width=True, type="primary"):
    if not st.session_state.bone_image_bytes:
        st.warning("Silakan upload X-ray tangan terlebih dahulu.")
    else:
        with st.spinner("Menganalisis usia tulang..."):
            st.session_state.bone_result = analyze_bone_age(
                st.session_state.bone_image_bytes, total_m, sex)
        st.session_state.bone_done = True
        st.session_state.bone_chat_history = []

if st.session_state.bone_done:
    r = st.session_state.bone_result
    bm     = r.get("bone_age_months")
    status = r.get("status", "UNKNOWN")
    diff   = r.get("difference_months")

    if bm is not None and status != "UNKNOWN":
        by = int(bm) // 12
        bmo = int(bm) % 12
        sign = "+" if (diff or 0) >= 0 else ""

        m1, m2, m3 = st.columns(3)
        m1.metric("Usia Kronologis",  f"{age_y}t {age_m}b")
        m2.metric("Estimasi Bone Age", f"{by}t {bmo}b")
        m3.metric("Selisih", f"{sign}{diff or 0} bln")

        status_map = {
            "NORMAL":   ("status-normal",   "✅ Normal"),
            "DELAYED":  ("status-delayed",  "⚠️ Keterlambatan Pertumbuhan (Delayed)"),
            "ADVANCED": ("status-advanced", "🔺 Percepatan Pertumbuhan (Advanced)"),
            "DEMO":     ("status-normal",   "🔧 Mode Demo"),
        }
        scls, slbl = status_map.get(status, ("", status))
        diff_txt = f"Selisih: <b>{sign}{diff} bulan</b> dari usia kronologis" if diff is not None else ""
        st.markdown(
            f'<div class="bone-card"><b>Status:</b> <span class="{scls}">{slbl}</span><br>{diff_txt}</div>',
            unsafe_allow_html=True)

    if r.get("findings") and status not in ("UNKNOWN",):
        with st.expander("📋 Temuan Tulang Spesifik", expanded=True):
            st.markdown(r["findings"])
    if r.get("explanation"):
        with st.expander("💬 Penjelasan untuk Orang Tua / Pasien", expanded=True):
            st.markdown(r["explanation"])
    if r.get("possible_causes"):
        with st.expander("🔍 Kemungkinan Penyebab"):
            st.markdown(r["possible_causes"])
    if r.get("recommendations"):
        with st.expander("📌 Rekomendasi Tindak Lanjut", expanded=True):
            st.markdown(r["recommendations"])
    if status == "UNKNOWN" and r.get("findings"):
        st.markdown(r["findings"])

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<p class="section-title">Tanya Jawab Bone Age</p>', unsafe_allow_html=True)

    bone_ctx = (
        f"Pasien: {sex}, usia kronologis {total_m} bulan. "
        f"Estimasi bone age: {bm} bulan. Status: {status}. "
        f"Temuan: {r.get('findings','')}. Penjelasan: {r.get('explanation','')}."
    )
    for msg in st.session_state.bone_chat_history:
        cls = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-ai"
        icon = "🧑" if msg["role"] == "user" else "🤖"
        st.markdown(f'<div class="{cls}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)

    with st.form("form_bone", clear_on_submit=True):
        bq = st.text_input("Pertanyaan bone age",
                           placeholder="Apakah keterlambatan ini berbahaya? Apa yang harus dilakukan?",
                           label_visibility="collapsed")
        if st.form_submit_button("Kirim →", use_container_width=True) and bq.strip():
            st.session_state.bone_chat_history.append({"role": "user", "content": bq.strip()})
            with st.spinner("Menjawab..."):
                ba = chat_bone(bq.strip(), bone_ctx, st.session_state.bone_chat_history)
            st.session_state.bone_chat_history.append({"role": "assistant", "content": ba})
            st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.caption(
    "⚠️ MedExplain AI hanyalah alat bantu edukatif. "
    "Bukan pengganti diagnosis atau saran medis profesional. "
    "Selalu konsultasikan kondisi kesehatan Anda dengan dokter."
)
