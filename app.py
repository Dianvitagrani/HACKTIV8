import streamlit as st
from PIL import Image
import io
import os
import json
import re

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bone Age AI",
    page_icon="🦴",
    layout="centered",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 2rem; max-width: 800px; }
    .chat-bubble-user {
        background: #e8f0fe; border-radius: 12px;
        padding: 10px 14px; margin: 6px 0; text-align: right;
    }
    .chat-bubble-ai {
        background: #f1f3f4; border-radius: 12px;
        padding: 10px 14px; margin: 6px 0;
    }
    .section-title {
        font-size: 0.8rem; color: #5f6368;
        text-transform: uppercase; letter-spacing: .06em;
        margin-bottom: 4px; margin-top: 0;
    }
    .bone-card {
        background: #f8f9fa; border: 1px solid #e0e0e0;
        border-radius: 12px; padding: 16px 20px; margin: 10px 0;
    }
    .status-normal   { color: #1e7e34; font-weight: 700; font-size: 1.05rem; }
    .status-delayed  { color: #c0392b; font-weight: 700; font-size: 1.05rem; }
    .status-advanced { color: #d35400; font-weight: 700; font-size: 1.05rem; }
    hr { border: none; border-top: 1px solid #e0e0e0; margin: 1.4rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for _k, _v in {
    "bone_done": False,
    "bone_result": {},
    "bone_chat_history": [],
    "bone_image_bytes": None,
    "bone_age_y": 8,
    "bone_age_m": 0,
    "bone_sex": "Laki-laki",
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
    # SDK baru: google-genai
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=key)
        contents = []
        for p in (parts or []):
            contents.append(types.Part.from_text(text=p) if isinstance(p, str) else p)
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=contents or text,
        )
        return response.text
    except ImportError:
        pass
    except Exception as e:
        return f"⚠️ Gemini error: {e}"
    # Fallback SDK lama: google-generativeai
    try:
        import google.generativeai as g
        g.configure(api_key=key)
        m = g.GenerativeModel("gemini-3.5-flash-lite")
        response = m.generate_content(parts if parts else text)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini error: {e}"


# ── AI: Bone Age ──────────────────────────────────────────────────────────────

def analyze_bone_age(image_bytes: bytes, chron_months: int, sex: str) -> dict:
    chron_years = chron_months / 12
    sys_p = (
        "Kamu adalah radiolog AI yang terlatih mengestimasi usia tulang (bone age) "
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
            "explanation": "Tambahkan GOOGLE_API_KEY ke Streamlit Secrets untuk analisis nyata.",
            "possible_causes": "-",
            "recommendations": "Konsultasikan dengan dokter spesialis anak.",
            "_raw_error": raw,
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
        "Jawab dengan empati dan bahasa yang mudah dipahami orang tua maupun pasien. "
        "Selalu ingatkan untuk konsultasi ke dokter SpA atau endokrinologi anak.\n\n"
        f"Konteks bone age:\n{context}"
    )
    hist = "\n".join(
        f"{'Pasien' if h['role'] == 'user' else 'AI'}: {h['content']}"
        for h in history[-6:]
    )
    out = _gemini(text=f"{sys_p}\n\nRiwayat:\n{hist}\n\nPasien: {question}")
    return out or "Silakan konsultasikan langsung dengan dokter spesialis anak."


# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════

st.title("🦴 Bone Age AI")
st.caption("Estimasi kematangan tulang dari X-ray tangan · Metode Greulich-Pyle · Hanya untuk edukasi")

# Status API key
_k = get_api_key()
if _k:
    st.success(f"✅ GOOGLE_API_KEY terbaca ({len(_k)} karakter)")
else:
    st.warning("⚠️ GOOGLE_API_KEY belum terdeteksi — berjalan dalam mode demo.")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Step 1: Upload ────────────────────────────────────────────────────────────
st.markdown('<p class="section-title">1 · Upload X-Ray Tangan</p>', unsafe_allow_html=True)
st.caption("Gunakan X-ray tangan kanan (PA view). Format: JPG / PNG.")

bone_file = st.file_uploader(
    "Upload X-ray tangan", type=["jpg", "jpeg", "png"],
    label_visibility="collapsed", key="up_bone"
)
if bone_file:
    bone_bytes = bone_file.read()
    st.session_state.bone_image_bytes = bone_bytes
    st.image(Image.open(io.BytesIO(bone_bytes)), use_container_width=True, caption="X-Ray Tangan")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Step 2: Data pasien ───────────────────────────────────────────────────────
st.markdown('<p class="section-title">2 · Data Pasien</p>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
age_y = c1.number_input("Usia (tahun)", min_value=0, max_value=20, value=8, step=1)
age_m = c2.number_input("Bulan tambahan", min_value=0, max_value=11, value=0, step=1)
sex   = c3.selectbox("Jenis kelamin", ["Laki-laki", "Perempuan"])
total_m = age_y * 12 + age_m
st.caption(f"Usia kronologis: **{age_y} tahun {age_m} bulan** ({total_m} bulan total)")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Step 3: Analisis ──────────────────────────────────────────────────────────
st.markdown('<p class="section-title">3 · Analisis Bone Age</p>', unsafe_allow_html=True)

if st.button("🦴 Analisis Usia Tulang", use_container_width=True, type="primary"):
    if not st.session_state.bone_image_bytes:
        st.warning("Silakan upload X-ray tangan terlebih dahulu.")
    else:
        with st.spinner("Menganalisis usia tulang..."):
            st.session_state.bone_result = analyze_bone_age(
                st.session_state.bone_image_bytes, total_m, sex
            )
        st.session_state.bone_done = True
        st.session_state.bone_chat_history = []

# ── Hasil ─────────────────────────────────────────────────────────────────────
if st.session_state.bone_done:
    r      = st.session_state.bone_result
    bm     = r.get("bone_age_months")
    status = r.get("status", "UNKNOWN")
    diff   = r.get("difference_months")

    if bm is not None and status not in ("UNKNOWN",):
        by  = int(bm) // 12
        bmo = int(bm) % 12
        sign = "+" if (diff or 0) >= 0 else ""

        m1, m2, m3 = st.columns(3)
        m1.metric("Usia Kronologis",   f"{age_y}t {age_m}b")
        m2.metric("Estimasi Bone Age", f"{by}t {bmo}b")
        m3.metric("Selisih",           f"{sign}{diff or 0} bln")

        status_map = {
            "NORMAL":   ("status-normal",   "✅ Normal"),
            "DELAYED":  ("status-delayed",  "⚠️ Keterlambatan Pertumbuhan (Delayed)"),
            "ADVANCED": ("status-advanced", "🔺 Percepatan Pertumbuhan (Advanced)"),
            "DEMO":     ("status-normal",   "🔧 Mode Demo"),
        }
        scls, slbl = status_map.get(status, ("", status))
        diff_txt = (
            f"Selisih: <b>{sign}{diff} bulan</b> dari usia kronologis"
            if diff is not None else ""
        )
        st.markdown(
            f'<div class="bone-card">'
            f'<b>Status:</b> <span class="{scls}">{slbl}</span><br>{diff_txt}'
            f'</div>',
            unsafe_allow_html=True,
        )

    if r.get("findings") and status != "UNKNOWN":
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

    # ── Step 4: Chat Q&A ──────────────────────────────────────────────────────
    st.markdown('<p class="section-title">4 · Tanya Jawab Lanjutan</p>', unsafe_allow_html=True)

    bone_ctx = (
        f"Pasien: {sex}, usia kronologis {total_m} bulan. "
        f"Estimasi bone age: {bm} bulan. Status: {status}. "
        f"Temuan: {r.get('findings', '')}. Penjelasan: {r.get('explanation', '')}."
    )

    for msg in st.session_state.bone_chat_history:
        cls  = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-ai"
        icon = "🧑" if msg["role"] == "user" else "🤖"
        st.markdown(f'<div class="{cls}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)

    with st.form("form_bone", clear_on_submit=True):
        bq = st.text_input(
            "Pertanyaan",
            placeholder="Contoh: Apakah keterlambatan ini berbahaya? Apa yang harus dilakukan?",
            label_visibility="collapsed",
        )
        if st.form_submit_button("Kirim →", use_container_width=True) and bq.strip():
            st.session_state.bone_chat_history.append({"role": "user", "content": bq.strip()})
            with st.spinner("Menjawab..."):
                ba = chat_bone(bq.strip(), bone_ctx, st.session_state.bone_chat_history)
            st.session_state.bone_chat_history.append({"role": "assistant", "content": ba})
            st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.caption(
    "⚠️ Bone Age AI hanyalah alat bantu edukatif. "
    "Bukan pengganti diagnosis atau saran medis profesional. "
    "Selalu konsultasikan kondisi kesehatan dengan dokter spesialis anak (SpA)."
)
