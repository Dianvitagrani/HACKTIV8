"""
Chat UI Module — Glancable chat interface with structured card rendering.
Renders AI responses as beautiful visual cards when structured data is detected.
"""

import streamlit as st
import time
from modules.utils import (
    CARD_CSS,
    format_activity_row,
    get_transport_icon,
    fmt_duration,
    fmt_price,
)
from modules.ai_assistant import (
    chat_with_ai,
    extract_structured_data,
    QUICK_PROMPTS,
    OPENAI_AVAILABLE,
)

CHAT_CSS = """
<style>
/* ── Chat layout ── */
.chat-wrap { display: flex; flex-direction: column; gap: 14px; padding: 4px 0; }

/* ── Bubbles ── */
.msg-row { display: flex; align-items: flex-end; gap: 10px; }
.msg-row.user  { flex-direction: row-reverse; }
.msg-row.bot   { flex-direction: row; }

.avatar {
    width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; font-weight: 700;
}
.avatar-user { background: linear-gradient(135deg,#2563EB,#7C3AED); color: white; }
.avatar-bot  { background: linear-gradient(135deg,#0EA5E9,#2563EB); color: white; }

.bubble {
    padding: 12px 16px; border-radius: 18px;
    max-width: 78%; line-height: 1.65; font-size: 14px;
    word-break: break-word;
}
.bubble-user {
    background: linear-gradient(135deg,#2563EB,#7C3AED);
    color: white;
    border-bottom-right-radius: 4px;
}
.bubble-bot {
    background: #F8FAFC;
    color: #1E293B;
    border: 1px solid #E2E8F0;
    border-bottom-left-radius: 4px;
}
.bubble-bot a { color: #2563EB; }

/* ── Typing indicator ── */
.typing-dot {
    display: inline-block; width: 7px; height: 7px;
    background: #94A3B8; border-radius: 50%; margin: 0 2px;
    animation: blink 1.2s infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink { 0%,80%,100% { opacity:.2; } 40% { opacity:1; } }

/* ── Structured cards inside chat ── */
.ai-card {
    background: white; border-radius: 14px; padding: 16px 18px;
    border: 1px solid #E2E8F0; margin: 8px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
}
.ai-card-header { font-size: 11px; font-weight: 700; color: #64748B;
    text-transform: uppercase; letter-spacing: .5px; margin-bottom: 8px; }
.ai-card-title  { font-size: 16px; font-weight: 700; color: #0F172A; margin-bottom: 6px; }

/* ── Departure status cards ── */
.dep-scenario {
    border-radius: 12px; padding: 14px 16px; margin: 6px 0;
    border: 1px solid #E2E8F0;
}
.dep-scenario-hero  { background: #F0FDF4; border-color: #86EFAC; }
.dep-scenario-rec   { background: #EFF6FF; border-color: #93C5FD; }
.dep-scenario-ideal { background: #FFFBEB; border-color: #FCD34D; }
.dep-time-big { font-size: 28px; font-weight: 800; color: #0F172A; }

/* ── Hotel cards ── */
.hotel-ai-card {
    background: white; border-radius: 12px; padding: 16px;
    border: 1px solid #E2E8F0; margin: 8px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
.hotel-rank-badge {
    display: inline-block; background: linear-gradient(135deg,#2563EB,#7C3AED);
    color: white; border-radius: 99px; padding: 2px 10px;
    font-size: 11px; font-weight: 700; margin-bottom: 6px;
}

/* ── Quick prompts ── */
.qprompt-btn {
    background: white; border: 1px solid #E2E8F0; border-radius: 10px;
    padding: 8px 14px; font-size: 13px; color: #374151; cursor: pointer;
    transition: all .15s; white-space: nowrap; overflow: hidden;
    text-overflow: ellipsis; max-width: 100%;
}
.qprompt-btn:hover { background: #EFF6FF; border-color: #93C5FD; color: #1D4ED8; }

/* ── Status pills ── */
.status-ok     { background:#DCFCE7; color:#15803D; border:1px solid #86EFAC; }
.status-warn   { background:#FEF3C7; color:#92400E; border:1px solid #FCD34D; }
.status-danger { background:#FEE2E2; color:#DC2626; border:1px solid #FCA5A5; }

/* ── Input area ── */
.input-hint { font-size: 12px; color: #94A3B8; margin-top: 4px; }

/* ── Empty state ── */
.empty-state { text-align:center; padding: 40px 20px; color: #94A3B8; }
.empty-state-icon { font-size: 52px; margin-bottom: 12px; }
</style>
"""


# ─── Main render function ────────────────────────────────────────────────────────
def render_chat_module():
    st.markdown(CARD_CSS + CHAT_CSS, unsafe_allow_html=True)

    # ── API Key gate ──────────────────────────────────────────────────────────
    api_key = _get_api_key()
    if not api_key:
        _render_api_key_setup()
        return

    # ── Layout: chat | sidebar-context ───────────────────────────────────────
    col_chat, col_ctx = st.columns([7, 3])

    with col_chat:
        _render_chat_area(api_key)

    with col_ctx:
        _render_context_panel()


# ─── API Key management ──────────────────────────────────────────────────────────
import os


def _get_api_key() -> str | None:
    # 1. Already cached in session
    if st.session_state.get("gemini_api_key"):
        return st.session_state["gemini_api_key"]

    # 2. Streamlit secrets — try every common pattern
    key = None
    try:
        # Direct key (most common: GEMINI_API_KEY = "AQa..." or "AIza...")
        key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    if not key:
        try:
            # Some users wrap it: [gemini]\napi_key = "AQa..."
            key = st.secrets["gemini"]["api_key"]
        except Exception:
            pass
    if not key:
        try:
            # Lowercase variant
            key = st.secrets["gemini_api_key"]
        except Exception:
            pass

    if key:
        st.session_state["gemini_api_key"] = key
        return key

    # 3. Environment variable (local dev / Docker)
    env_key = os.environ.get("GEMINI_API_KEY", "")
    if env_key:
        st.session_state["gemini_api_key"] = env_key
        return env_key

    return None


def _render_api_key_setup():
    # ── Last-chance: scan ALL secret keys for anything that looks like a Gemini key ──
    found_key = None
    try:
        for secret_key in st.secrets:
            val = str(st.secrets[secret_key])
            if val.startswith(("AIza", "AQ")):
                found_key = val
                break
    except Exception:
        pass

    if found_key:
        # Secret exists but wasn't matched by name — use it and skip the form
        st.session_state["gemini_api_key"] = found_key
        st.rerun()
        return

    # ── No secret found — show manual input form ─────────────────────────────────
    st.markdown(
        """<div style='max-width:560px;margin:0 auto'>
        <div style='text-align:center;padding:32px 0 16px'>
          <div style='font-size:52px'>🔑</div>
          <div style='font-size:22px;font-weight:700;color:#0F172A;margin:10px 0'>
            Hubungkan Google Gemini API
          </div>
          <div style='font-size:14px;color:#64748B;line-height:1.7'>
            Holiday Planner AI menggunakan <b>Google Gemini</b> untuk memberikan
            rekomendasi cerdas ke <b>seluruh destinasi di dunia</b>.<br><br>
            Masukkan Gemini API key kamu untuk mulai, atau simpan di
            <b>Streamlit Secrets</b> agar tidak perlu dimasukkan ulang.
          </div>
        </div>
        </div>""",
        unsafe_allow_html=True,
    )

    with st.form("api_key_form"):
        key_input = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AQ... atau AIza...",
            help="Dapatkan API key gratis di aistudio.google.com/apikey",
        )
        model_choice = st.selectbox(
            "Model",
            options=["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.1-pro", "gemini-2.5-flash"],
            index=0,
            help="gemini-3.5-flash-lite = tercepat & terhemat (default). gemini-3.6-flash = lebih pintar.",
        )
        submitted = st.form_submit_button("🚀 Mulai Chat", type="primary", use_container_width=True)

    if submitted and key_input.strip():
        st.session_state["gemini_api_key"] = key_input.strip()
        st.session_state["ai_model"] = model_choice
        st.success("✅ API Key tersimpan! Memuat asisten...")
        time.sleep(0.8)
        st.rerun()
    elif submitted:
        st.error("⚠️ API Key tidak boleh kosong.")

    # Setup instructions
    with st.expander("📖 Cara mendapatkan Gemini API Key (GRATIS)"):
        st.markdown("""
1. Buka [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Login dengan akun Google kamu
3. Klik **"Create API key"**
4. Copy key dan paste di atas

**Estimasi biaya per sesi:**
- `gemini-3.5-flash-lite` → Tercepat & terhemat, terbaru ✅ (default)
- `gemini-3.6-flash` → All-around, lebih pintar
- `gemini-3.1-pro` → Advanced reasoning, terkuat

**Alternatif:** Simpan key di `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "AQ..."
```
atau set environment variable `GEMINI_API_KEY`.
        """)

    # Show feature preview even without key
    st.divider()
    st.markdown("#### ✨ Yang bisa dilakukan AI Assistant:")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
- 🗓️ **Itinerary** — semua kota di dunia
- ⏰ **Waktu bandara** — H-1 & Hari-H
        """)
    with c2:
        st.markdown("""
- 🚨 **Backup darurat** — alternatif instan
- 🏨 **Hotel strategis** — berdasarkan itinerary
        """)


# ─── Main chat area ──────────────────────────────────────────────────────────────
def _render_chat_area(api_key: str):
    # Init chat history
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []

    model = st.session_state.get("ai_model", "gemini-3.5-flash-lite")

    # Chat header bar
    col1, col2, col3 = st.columns([5, 2, 2])
    with col1:
        st.markdown(
            f"<div style='font-size:13px;color:#64748B;padding-top:6px'>"
            f"🤖 Model: <b>{model}</b> &nbsp;·&nbsp; "
            f"💬 {len(st.session_state['chat_messages']) // 2} pesan</div>",
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("🗑️ Reset Chat", use_container_width=True):
            st.session_state["chat_messages"] = []
            st.rerun()
    with col3:
        if st.button("🔑 Ganti Key", use_container_width=True):
            st.session_state.pop("gemini_api_key", None)
            st.rerun()

    st.divider()

    # ── Message history ───────────────────────────────────────────────────────
    messages = st.session_state["chat_messages"]

    if not messages:
        _render_empty_state()
    else:
        for msg in messages:
            _render_message(msg["role"], msg["content"], msg.get("structured"))

    # ── Input area ────────────────────────────────────────────────────────────
    st.markdown("")
    input_col, btn_col = st.columns([9, 1])
    with input_col:
        user_input = st.chat_input(
            "Tanya apa saja — itinerary, bandara, hotel, backup... 🌍",
        )

    if user_input and user_input.strip():
        _handle_user_message(user_input.strip(), api_key, model)


def _handle_user_message(text: str, api_key: str, model: str):
    messages = st.session_state["chat_messages"]

    # Append user message
    messages.append({"role": "user", "content": text})
    st.session_state["chat_messages"] = messages

    # Render user bubble immediately
    _render_message("user", text)

    # Show typing indicator while waiting
    with st.status("⏳ AI sedang memproses...", expanded=False):
        try:
            # Build messages list (only role+content; Gemini role mapping is done inside chat_with_ai)
            chat_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in messages
            ]

            full_response = ""
            stream = chat_with_ai(
                messages=chat_messages,
                api_key=api_key,
                model=model,
                session_state=st.session_state,
                stream=True,
            )

            response_placeholder = st.empty()
            for chunk in stream:
                # Gemini streaming: chunk.text (may be None on final metadata chunk)
                delta = chunk.text or ""
                full_response += delta
                # Show progressive text
                response_placeholder.markdown(
                    f"<div class='bubble bubble-bot' style='display:inline-block'>{full_response}▌</div>",
                    unsafe_allow_html=True,
                )

            response_placeholder.empty()

        except Exception as e:
            full_response = (
                f"⚠️ Terjadi kesalahan: `{str(e)}`\n\n"
                "Pastikan API key valid dan kamu terhubung ke internet."
            )

    # Parse structured data from response
    parsed = extract_structured_data(full_response)

    # Store assistant message with structured data
    messages.append({
        "role": "assistant",
        "content": full_response,
        "structured": parsed,
    })
    st.session_state["chat_messages"] = messages

    # If itinerary data found, save to session state
    if parsed.get("itinerary"):
        itin = parsed["itinerary"]
        st.session_state["itinerary"] = itin
        st.session_state["trip_info"] = {
            "destination": itin.get("city", ""),
            "start_date":  itin["days"][0]["label"] if itin.get("days") else "",
            "end_date":    itin["days"][-1]["label"] if itin.get("days") else "",
            "travelers":   itin.get("travelers", 1),
            "num_days":    itin.get("total_days", 1),
        }

    st.rerun()


# ─── Message renderers ───────────────────────────────────────────────────────────
def _render_message(role: str, content: str, structured: dict = None):
    if role == "user":
        st.markdown(
            f"""<div class='msg-row user'>
              <div class='avatar avatar-user'>🙂</div>
              <div class='bubble bubble-user'>{content}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        # Narrative text
        parsed = structured or extract_structured_data(content)
        narrative = parsed.get("narrative", content).strip()

        st.markdown(
            f"""<div class='msg-row bot'>
              <div class='avatar avatar-bot'>✈️</div>
              <div class='bubble bubble-bot'>{_md_to_html(narrative)}</div>
            </div>""",
            unsafe_allow_html=True,
        )

        # Render structured cards below the bubble
        if parsed.get("itinerary"):
            _render_itinerary_card(parsed["itinerary"])
        if parsed.get("departure"):
            _render_departure_card(parsed["departure"])
        if parsed.get("backup"):
            _render_backup_card(parsed["backup"])
        if parsed.get("hotel"):
            _render_hotel_card(parsed["hotel"])


def _md_to_html(text: str) -> str:
    """Very light markdown → HTML for inside bubble."""
    import re
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    # Inline code
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Newlines
    text = text.replace("\n\n", "<br><br>").replace("\n", "<br>")
    return text


# ─── Structured card renderers ───────────────────────────────────────────────────
def _render_itinerary_card(itin: dict):
    city = itin.get("city", "Unknown")
    days = itin.get("days", [])
    travelers = itin.get("travelers", 1)

    st.markdown(
        f"""<div class='ai-card'>
        <div class='ai-card-header'>🗓️ Itinerary Generated</div>
        <div class='ai-card-title'>📍 {city.title()}</div>
        <span class='badge badge-blue'>🗓️ {len(days)} hari</span>
        <span class='badge badge-green'>👥 {travelers} orang</span>
        </div>""",
        unsafe_allow_html=True,
    )

    if not days:
        return

    day_labels = [f"Hari {d['day_number']} — {d.get('label', '')}" for d in days]
    sel = st.selectbox(
        "Pilih hari untuk ditampilkan",
        range(len(day_labels)),
        format_func=lambda i: day_labels[i],
        key=f"itin_day_sel_{city}_{len(days)}",
    )

    day = days[sel]
    activities = day.get("activities", [])

    rows_html = "".join(format_activity_row(a) for a in activities)
    st.markdown(
        f"<div class='timeline-wrap'>{rows_html}</div>",
        unsafe_allow_html=True,
    )

    # Transport legend
    transports = set()
    for a in activities:
        for t in a.get("transport", []):
            transports.add(t)
    if transports:
        icons = " ".join(
            f"{get_transport_icon(t)} <span style='font-size:12px'>{t.replace('_',' ').title()}</span>"
            for t in sorted(transports)
        )
        st.markdown(
            f"<div class='ai-card' style='font-size:13px;padding:10px 14px'>"
            f"<b>🚗 Transportasi:</b> {icons}</div>",
            unsafe_allow_html=True,
        )

    # Save button
    if st.button("💾 Simpan sebagai Trip Aktif", key=f"save_itin_{city}_{len(days)}", type="primary"):
        st.session_state["itinerary"] = itin
        st.session_state["trip_info"] = {
            "destination": city,
            "start_date": days[0].get("label", ""),
            "end_date":   days[-1].get("label", ""),
            "travelers":  travelers,
            "num_days":   len(days),
        }
        st.success(f"✅ Itinerary {city.title()} disimpan sebagai trip aktif!")


def _render_departure_card(dep: dict):
    dep_type = dep.get("type", "hm1")

    if dep_type == "hm1":
        scenarios = dep.get("scenarios", {})
        st.markdown(
            f"""<div class='ai-card'>
            <div class='ai-card-header'>⏰ Rekomendasi Waktu Keberangkatan (H-1)</div>
            <div class='ai-card-title'>✈️ Penerbangan jam {dep.get('departure_time','?')}</div>
            <span class='badge badge-amber'>🚗 ~{dep.get('hotel_to_airport_minutes','?')} menit ke bandara</span>
            {f"<br><small style='color:#64748B'>{dep.get('traffic_note','')}</small>" if dep.get('traffic_note') else ''}
            </div>""",
            unsafe_allow_html=True,
        )

        styles = [
            ("hero",        "dep-scenario dep-scenario-hero",  "🏆 Hero (Super Aman)"),
            ("recommended", "dep-scenario dep-scenario-rec",   "✅ Rekomendasi Asisten"),
            ("ideal",       "dep-scenario dep-scenario-ideal", "⚡ Ideal (Tepat Waktu)"),
        ]
        cols = st.columns(3)
        for col, (key, cls, label) in zip(cols, styles):
            s = scenarios.get(key, {})
            with col:
                st.markdown(
                    f"""<div class='{cls}'>
                    <div style='font-size:11px;font-weight:600;margin-bottom:6px'>{label}</div>
                    <div style='font-size:12px;color:#64748B'>⏰ Bangun</div>
                    <div class='dep-time-big'>{s.get('wake','?')}</div>
                    <div style='font-size:12px;color:#64748B;margin-top:6px'>🚗 Berangkat</div>
                    <div style='font-size:20px;font-weight:700'>{s.get('leave','?')}</div>
                    <div style='font-size:12px;color:#64748B;margin-top:6px'>🛬 Tiba Bandara</div>
                    <div style='font-size:16px;font-weight:600'>{s.get('airport_arrival','?')}</div>
                    <div style='font-size:11px;color:#555;margin-top:8px'>{s.get('desc','')}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

    else:  # harih
        status_cls = {
            "ok": "status-ok", "warning": "status-warn",
            "urgent": "status-danger", "danger": "status-danger",
        }.get(dep.get("status", "ok"), "status-ok")

        st.markdown(
            f"""<div class='ai-card'>
            <div class='ai-card-header'>🛫 Analisis Hari-H Real-time</div>
            <div class='dep-scenario {status_cls}' style='margin-top:8px'>
              <div style='font-size:18px;font-weight:700'>{dep.get('status_label','')}</div>
              <div style='font-size:13px;margin-top:4px'>{dep.get('advice','')}</div>
            </div>
            <div style='display:flex;gap:16px;margin-top:12px;flex-wrap:wrap'>
              <div><div style='font-size:11px;color:#64748B'>Penerbangan</div>
                   <div style='font-weight:700'>{dep.get('departure_time','?')}</div></div>
              <div><div style='font-size:11px;color:#64748B'>Gate</div>
                   <div style='font-weight:700'>{dep.get('gate','?')}</div></div>
              <div><div style='font-size:11px;color:#64748B'>Traffic</div>
                   <div style='font-weight:700'>{dep.get('traffic_label','?')}</div></div>
              <div><div style='font-size:11px;color:#64748B'>Batas berangkat</div>
                   <div style='font-weight:700;color:#DC2626'>{dep.get('leave_latest','?')}</div></div>
              <div><div style='font-size:11px;color:#64748B'>Sisa waktu</div>
                   <div style='font-weight:700;font-size:20px;color:#2563EB'>{dep.get('minutes_until_must_leave','?')} mnt</div></div>
            </div>
            </div>""",
            unsafe_allow_html=True,
        )


def _render_backup_card(backup: dict):
    st.markdown(
        f"""<div class='ai-card' style='border-left:4px solid #F59E0B'>
        <div class='ai-card-header'>🚨 Backup Darurat Aktif</div>
        <div style='font-size:13px;color:#374151'>
          🔒 <b>{backup.get('closed_place','?')}</b> tidak bisa dikunjungi.
          Berikut destinasi pengganti terbaik:
        </div>
        </div>""",
        unsafe_allow_html=True,
    )

    options = backup.get("backup_options", [])
    if not options:
        return

    cols = st.columns(min(len(options), 3))
    for col, opt in zip(cols, options):
        with col:
            transport_icons = " ".join(
                get_transport_icon(t) for t in opt.get("transport", [])[:3]
            )
            st.markdown(
                f"""<div class='ai-card'>
                <span class='badge badge-amber'>{opt.get('category','')}</span>
                <div style='font-weight:700;margin:6px 0;font-size:14px'>{opt.get('name','')}</div>
                <div style='font-size:12px;color:#64748B'>{opt.get('why','')}</div>
                <div style='margin-top:6px;font-size:12px'>
                  ⏱️ {fmt_duration(opt.get('duration_hours', 1.5))} &nbsp; {transport_icons}
                </div>
                <div style='font-size:12px;color:#374151;margin-top:4px'>💡 {opt.get('tip','')}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    # Revised schedule
    revised = backup.get("revised_schedule", [])
    if revised:
        st.markdown("**📋 Jadwal Hari Ini Setelah Revisi:**")
        rows_html = "".join(
            format_activity_row({
                "time": item.get("time", ""),
                "end_time": item.get("end_time", ""),
                "name": item.get("name", ""),
                "duration": 1.0,
                "tip": item.get("tip", ""),
                "transport": [],
                "is_buffer": False,
                "is_backup": True,
            })
            for item in revised
        )
        st.markdown(f"<div class='timeline-wrap'>{rows_html}</div>", unsafe_allow_html=True)

    if backup.get("mood_booster"):
        st.success(backup["mood_booster"])


def _render_hotel_card(hotel_data: dict):
    city  = hotel_data.get("city", "")
    hotels = hotel_data.get("hotels", [])
    if not hotels:
        return

    st.markdown(
        f"""<div class='ai-card'>
        <div class='ai-card-header'>🏨 Rekomendasi Penginapan</div>
        <div class='ai-card-title'>📍 {city.title() if city else 'Hotel Pilihan'}</div>
        <span class='badge badge-blue'>{len(hotels)} penginapan direkomendasikan</span>
        </div>""",
        unsafe_allow_html=True,
    )

    MEDAL = {1: "🥇", 2: "🥈", 3: "🥉"}

    for h in hotels:
        rank  = h.get("rank", 0)
        stars = "⭐" * h.get("stars", 0)
        p_min = h.get("price_min", 0)
        p_max = h.get("price_max", 0)
        price_str = (
            f"{fmt_price(p_min)} – {fmt_price(p_max)}"
            if p_min and p_max
            else h.get("price_range", "Hubungi hotel")
        )
        fac_html = " ".join(
            f"<span style='background:#F1F5F9;border-radius:6px;padding:2px 7px;"
            f"font-size:11px;color:#374151;display:inline-block;margin:2px'>{f}</span>"
            for f in h.get("facilities", [])
        )
        avg_t = h.get("avg_travel_minutes")
        strat = h.get("strategic_label", "")
        why   = h.get("why_strategic", "")

        st.markdown(
            f"""<div class='hotel-ai-card'>
            <div class='hotel-rank-badge'>{MEDAL.get(rank, str(rank))} #{rank} Pilihan Terbaik</div>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:6px'>
              <div>
                <div style='font-size:16px;font-weight:700;color:#0F172A'>{h.get('name','')}</div>
                <div style='font-size:13px;color:#64748B'>📍 {h.get('area','')} &nbsp;·&nbsp; {stars}</div>
              </div>
              <div style='text-align:right'>
                <div style='font-size:14px;font-weight:700;color:#2563EB'>{price_str}</div>
                <div style='font-size:11px;color:#94A3B8'>per malam</div>
              </div>
            </div>
            <div style='margin:8px 0'>
              {f"<span class='badge badge-green'>{strat}</span>" if strat else ""}
              {f"<span class='badge badge-blue'>⌀ {avg_t} mnt ke destinasi</span>" if avg_t else ""}
            </div>
            <div style='font-size:13px;color:#374151;margin-bottom:6px'>
              💡 {h.get('tip','')}
              {f'<br><span style="color:#2563EB;font-size:12px">🗺️ {why}</span>' if why else ''}
            </div>
            <div>{fac_html}</div>
            </div>""",
            unsafe_allow_html=True,
        )


# ─── Context panel ───────────────────────────────────────────────────────────────
def _render_context_panel():
    st.markdown(CARD_CSS, unsafe_allow_html=True)
    st.markdown("#### 💡 Saran Pertanyaan")

    categories = [
        ("🗓️ Itinerary", "itinerary"),
        ("⏰ Bandara", "departure"),
        ("🚨 Backup", "emergency"),
        ("🏨 Hotel", "hotel"),
    ]

    for cat_label, cat_key in categories:
        with st.expander(cat_label, expanded=(cat_key == "itinerary")):
            for prompt in QUICK_PROMPTS.get(cat_key, []):
                if st.button(
                    prompt,
                    key=f"qp_{cat_key}_{prompt[:20]}",
                    use_container_width=True,
                ):
                    _inject_quick_prompt(prompt)

    st.divider()

    # Active trip summary
    if st.session_state.get("itinerary"):
        itin = st.session_state["itinerary"]
        info = st.session_state.get("trip_info", {})
        st.markdown(
            f"""<div class='ai-card'>
            <div class='ai-card-header'>📍 Trip Aktif</div>
            <div style='font-weight:700'>{itin['city'].title()}</div>
            <div style='font-size:13px;color:#64748B'>
              {info.get('num_days', len(itin['days']))} hari · {itin['travelers']} orang
            </div>
            <div style='margin-top:8px'>
              <span class='badge badge-green'>✅ Itinerary tersimpan</span>
            </div>
            <div style='margin-top:8px;font-size:12px;color:#64748B'>
              Tanyakan AI untuk rekomendasi hotel, backup darurat, atau ubah jadwal.
            </div>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """<div class='ai-card'>
            <div style='text-align:center;padding:12px 0;color:#94A3B8'>
              <div style='font-size:28px'>🗺️</div>
              <div style='font-size:13px;margin-top:6px'>Belum ada trip aktif.<br>Minta AI buatkan itinerary!</div>
            </div>
            </div>""",
            unsafe_allow_html=True,
        )


def _inject_quick_prompt(prompt: str):
    """Simulate user typing the quick prompt."""
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []
    st.session_state["pending_prompt"] = prompt
    st.rerun()


# ─── Empty state ─────────────────────────────────────────────────────────────────
def _render_empty_state():
    # Check for pending quick prompt
    if st.session_state.get("pending_prompt"):
        prompt = st.session_state.pop("pending_prompt")
        st.session_state["chat_messages"].append({"role": "user", "content": prompt})
        st.rerun()
        return

    st.markdown(
        """<div class='empty-state'>
        <div class='empty-state-icon'>✈️</div>
        <div style='font-size:18px;font-weight:700;color:#374151;margin-bottom:8px'>
          Halo! Saya Holiday Planner AI
        </div>
        <div style='font-size:14px;color:#64748B;max-width:400px;margin:0 auto;line-height:1.7'>
          Tanyakan apa saja tentang perjalananmu — itinerary ke mana pun di dunia,
          waktu keberangkatan, backup darurat, atau rekomendasi penginapan.
        </div>
        <div style='margin-top:20px;font-size:13px;color:#94A3B8'>
          Ketik di kolom chat di bawah, atau pilih contoh pertanyaan di kanan →
        </div>
        </div>""",
        unsafe_allow_html=True,
    )
