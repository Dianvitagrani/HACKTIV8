"""
Holiday Planner & Smart Assistant
Main Streamlit Application
"""

import streamlit as st
from datetime import datetime

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Holiday Planner ✈️",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #0F172A !important; }
section[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
section[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: 1px solid #334155 !important;
    color: #CBD5E1 !important;
    border-radius: 10px !important;
    text-align: left !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    margin: 2px 0 !important;
    transition: all 0.15s !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #1E3A5F !important;
    border-color: #3B82F6 !important;
    color: white !important;
}

/* Main area */
.main .block-container { padding-top: 1.5rem !important; max-width: 1100px; }

/* Hide default Streamlit chrome */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }

/* Tab styling */
button[data-baseweb="tab"] {
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    border-radius: 8px 8px 0 0 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: #EFF6FF !important;
    color: #2563EB !important;
}

/* Form inputs */
.stSelectbox > div, .stTextInput > div, .stNumberInput > div {
    border-radius: 10px !important;
}

/* Primary button */
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #2563EB, #7C3AED) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
}

/* Expander */
details summary {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #374151 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

from modules.utils import CARD_CSS

# ─── Session State ───────────────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "active_module": "home",
        "itinerary": None,
        "trip_info": {},
        "voice_enabled": True,
        "voice_auto_read": False,
        "current_day": 1,
        "chat_messages": [],
        "gemini_api_key": "",
        "ai_model": "gemini-2.0-flash-lite",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ─── Sidebar Navigation ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='padding:12px 0 6px;text-align:center'>"
        "<div style='font-size:36px'>✈️</div>"
        "<div style='font-size:17px;font-weight:700;margin-top:4px'>Holiday Planner</div>"
        "<div style='font-size:11px;color:#94A3B8;margin-top:2px'>Smart Travel Assistant</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    NAV = [
        ("🏠", "home",       "Beranda"),
        ("💬", "ai_chat",    "AI Assistant ✨"),
        ("🗓️", "itinerary",  "Susun Itinerary"),
        ("⏰", "departure",  "Manajemen Keberangkatan"),
        ("🚨", "emergency",  "Backup Darurat"),
        ("🏨", "hotel",      "Rekomendasi Penginapan"),
        ("🎤", "voice",      "Pengaturan Suara"),
    ]

    for icon, key, label in NAV:
        if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state.active_module = key
            st.rerun()

    st.divider()

    # Active trip info
    if st.session_state.itinerary:
        info = st.session_state.trip_info
        st.markdown(
            f"""<div style='padding:10px;background:#1E3A5F;border-radius:10px;font-size:13px'>
            <div style='font-weight:600;margin-bottom:6px'>📍 Trip Aktif</div>
            <div>🌏 <b>{info.get('destination','—')}</b></div>
            <div>📅 {info.get('start_date','—')} → {info.get('end_date','—')}</div>
            <div>👥 {info.get('travelers',1)} orang · {info.get('num_days',1)} hari</div>
            </div>""",
            unsafe_allow_html=True,
        )
        st.markdown("")
        if st.button("🗑️ Hapus Trip", use_container_width=True, key="reset_trip"):
            st.session_state.itinerary = None
            st.session_state.trip_info = {}
            st.session_state.active_module = "home"
            st.rerun()

    st.divider()

    voice_icon = "🔊 ON" if st.session_state.voice_enabled else "🔇 OFF"
    if st.button(f"Suara: {voice_icon}", use_container_width=True, key="sidebar_voice_toggle"):
        st.session_state.voice_enabled = not st.session_state.voice_enabled
        st.rerun()

    st.markdown(
        "<div style='font-size:10px;color:#475569;text-align:center;padding-top:8px'>"
        "Made with ❤️ for Indonesian Travelers<br>© 2025 Holiday Planner</div>",
        unsafe_allow_html=True,
    )

# ─── Page Header ────────────────────────────────────────────────────────────────
MODULE_TITLES = {
    "home":       ("✈️", "Holiday Planner & Smart Assistant", "Rencanakan liburanmu dari A sampai Z"),
    "ai_chat":    ("💬", "AI Assistant", "Chat cerdas untuk itinerary, bandara, backup, & hotel — ke seluruh dunia"),
    "itinerary":  ("🗓️", "Susun Itinerary Cerdas", "Jadwal lengkap hari per hari dengan durasi & transportasi"),
    "departure":  ("⏰", "Manajemen Keberangkatan", "H-1 & Hari-H — analisis waktu bandara real-time"),
    "emergency":  ("🚨", "Backup Darurat & Dynamic Plan", "Destinasi tutup? Langsung kami carikan penggantinya!"),
    "hotel":      ("🏨", "Rekomendasi Penginapan Strategis", "Pilih penginapan berdasarkan waktu tempuh ke seluruh itinerary"),
    "voice":      ("🎤", "Pengaturan Suara", "Konfigurasi speech-to-text & text-to-speech"),
}

icon, title, subtitle = MODULE_TITLES.get(st.session_state.active_module, ("✈️", "Holiday Planner", ""))

st.markdown(
    f"""<div style='margin-bottom:6px'>
    <span style='font-size:32px'>{icon}</span>
    <span style='font-size:26px;font-weight:800;color:#0F172A;vertical-align:middle;margin-left:10px'>{title}</span><br>
    <span style='font-size:14px;color:#64748B;margin-left:6px'>{subtitle}</span>
    </div>""",
    unsafe_allow_html=True,
)
st.divider()

# ─── Module: HOME ────────────────────────────────────────────────────────────────
if st.session_state.active_module == "home":
    st.markdown(CARD_CSS, unsafe_allow_html=True)

    # Hero — AI-first
    st.markdown(
        """<div style='background:linear-gradient(135deg,#1E3A8A,#7C3AED);
            border-radius:18px;padding:28px 32px;margin-bottom:20px;color:white'>
        <div style='font-size:22px;font-weight:800;margin-bottom:10px'>
            👋 Halo, Traveler! Meet your AI Travel Companion ✨
        </div>
        <div style='font-size:15px;line-height:1.8;opacity:.92'>
            <b>Holiday Planner AI</b> siap membantu merencanakan perjalananmu ke
            <b>seluruh penjuru dunia</b> — dari Bali hingga Barcelona, Tokyo hingga Tunisia.<br>
            Cukup ketik atau ucapkan apa yang kamu butuhkan. Semua dalam satu chat.
        </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Primary CTA — AI Chat
    if st.button(
        "💬 Mulai Chat dengan AI Assistant →",
        type="primary",
        use_container_width=True,
        key="home_ai_cta",
    ):
        st.session_state.active_module = "ai_chat"
        st.rerun()

    st.markdown("")

    # Feature cards
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, emoji, title_c, desc in [
        (c1, "💬", "AI Assistant",
         "Chat natural — tanya apa saja, ke kota mana saja di dunia."),
        (c2, "🗓️", "Itinerary Cerdas",
         "Jadwal hari per hari dengan durasi & transportasi."),
        (c3, "⏰", "Alarm Bandara",
         "Waktu bangun & berangkat optimal, anti mepet flight."),
        (c4, "🚨", "Backup Darurat",
         "Destinasi tutup? Langsung dapat alternatif + jadwal baru."),
        (c5, "🏨", "Penginapan",
         "Rekomendasi hotel strategis berdasar waktu tempuh ke itinerary."),
    ]:
        with col:
            st.markdown(
                f"""<div class='info-card' style='height:150px'>
                <div style='font-size:28px;margin-bottom:6px'>{emoji}</div>
                <div style='font-weight:700;font-size:13px;margin-bottom:4px;color:#0F172A'>{title_c}</div>
                <div style='font-size:12px;color:#64748B;line-height:1.5'>{desc}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("#### 🚀 Akses Cepat")
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        if st.button("💬 AI Chat", type="primary", use_container_width=True):
            st.session_state.active_module = "ai_chat"
            st.rerun()
    with col_b:
        if st.button("✈️ Cek Waktu Bandara", use_container_width=True):
            st.session_state.active_module = "departure"
            st.rerun()
    with col_c:
        if st.button("🚨 Backup Darurat", use_container_width=True):
            st.session_state.active_module = "emergency"
            st.rerun()
    with col_d:
        if st.button("🏨 Cari Penginapan", use_container_width=True):
            st.session_state.active_module = "hotel"
            st.rerun()

    # How it works
    st.markdown("#### 📖 Cara Pakai")
    st.markdown(
        """<div class='info-card'>
        <div style='display:flex;gap:16px;flex-wrap:wrap'>
          <div style='flex:1;min-width:160px;text-align:center;padding:10px'>
            <div style='font-size:24px'>1️⃣</div>
            <div style='font-weight:600;margin:6px 0'>Isi Info Trip</div>
            <div style='font-size:12px;color:#64748B'>Pilih kota, tanggal, & jumlah orang</div>
          </div>
          <div style='flex:1;min-width:160px;text-align:center;padding:10px'>
            <div style='font-size:24px'>2️⃣</div>
            <div style='font-weight:600;margin:6px 0'>Dapatkan Itinerary</div>
            <div style='font-size:12px;color:#64748B'>Jadwal otomatis disusun lengkap</div>
          </div>
          <div style='flex:1;min-width:160px;text-align:center;padding:10px'>
            <div style='font-size:24px'>3️⃣</div>
            <div style='font-weight:600;margin:6px 0'>Set Alarm Bandara</div>
            <div style='font-size:12px;color:#64748B'>Waktu bangun & berangkat optimal</div>
          </div>
          <div style='flex:1;min-width:160px;text-align:center;padding:10px'>
            <div style='font-size:24px'>4️⃣</div>
            <div style='font-weight:600;margin:6px 0'>Nikmati Liburan!</div>
            <div style='font-size:12px;color:#64748B'>Backup otomatis jika ada perubahan</div>
          </div>
        </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Voice CTA
    if st.session_state.voice_enabled:
        st.markdown(
            """<div class='info-card' style='border-left:4px solid #2563EB'>
            <span class='badge badge-blue'>🎤 Voice Assistant Aktif</span>
            <span style='font-size:13px;color:#374151;margin-left:8px'>
              Pergi ke <b>Pengaturan Suara</b> untuk uji coba input suara & text-to-speech.
            </span>
            </div>""",
            unsafe_allow_html=True,
        )

# ─── Module: AI CHAT ────────────────────────────────────────────────────────────
elif st.session_state.active_module == "ai_chat":
    from modules.chat_ui import render_chat_module
    render_chat_module()

# ─── Module: ITINERARY ───────────────────────────────────────────────────────────
elif st.session_state.active_module == "itinerary":
    from modules.itinerary import render_itinerary_module
    render_itinerary_module()

    # Voice input section
    if st.session_state.voice_enabled:
        st.divider()
        with st.expander("🎤 Ucapkan Pertanyaan Seputar Itinerary"):
            st.markdown(
                "*Tanya asisten via suara — contoh: 'Tampilkan jadwal hari ke-2' atau 'Apa transportasi ke Tanah Lot?'*"
            )
            from modules.voice import render_voice_input
            render_voice_input(key="itin_voice", height=200)

# ─── Module: DEPARTURE ──────────────────────────────────────────────────────────
elif st.session_state.active_module == "departure":
    from modules.departure import render_departure_module
    render_departure_module()

    if st.session_state.voice_enabled:
        st.divider()
        with st.expander("🎤 Ucapkan Info Penerbangan"):
            st.markdown(
                "*Contoh: 'Pesawat jam tujuh pagi, hotel empat puluh menit dari bandara'*"
            )
            from modules.voice import render_voice_input
            render_voice_input(key="dep_voice", height=200)

# ─── Module: EMERGENCY ──────────────────────────────────────────────────────────
elif st.session_state.active_module == "emergency":
    from modules.emergency import render_emergency_module
    render_emergency_module()

    if st.session_state.voice_enabled:
        st.divider()
        with st.expander("🎤 Laporkan Tempat Tutup via Suara"):
            st.markdown(
                "*Contoh: 'Hari ini Ubud Monkey Forest tutup, tolong carikan alternatif'*"
            )
            from modules.voice import render_voice_input
            render_voice_input(key="emerg_voice", height=200)

# ─── Module: HOTEL ──────────────────────────────────────────────────────────────
elif st.session_state.active_module == "hotel":
    from modules.hotel import render_hotel_module
    render_hotel_module()

# ─── Module: VOICE SETTINGS ─────────────────────────────────────────────────────
elif st.session_state.active_module == "voice":
    from modules.voice import render_voice_settings
    render_voice_settings()
